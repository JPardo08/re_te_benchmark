"""Load, validate, and project C2_SCHEMA_V1.

The checked-in JSON file is the knowledge package. The model-facing payload is
a deterministic projection of that package. Provenance, unresolved definitions,
and exclusion records stay out of the payload.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = REPO_ROOT / "schemas" / "c2" / "c2_schema_v1.json"
C1_PATH = REPO_ROOT / "schemas" / "c1" / "hohfeld_labels.json"

PACKAGE_ID = "C2_SCHEMA_V1"
PACKAGE_VERSION = "1.0.0"

_REQUIRED_PACKAGE_KEYS = (
    "package_id",
    "package_version",
    "condition_id",
    "c1_label_schema",
    "output_contract",
    "normative_scope",
    "action_polarity",
    "relations",
    "entity_types",
    "abstract_roles",
    "annotation_constructs",
    "exclusions",
    "extraction_boundaries",
    "integrity",
)

_REQUIRED_RELATION_KEYS = (
    "id",
    "legal_name",
    "definition",
    "relational_semantics",
    "correlative",
    "opposite",
    "direction",
    "verification_status",
    "sources",
)

_FORBIDDEN_PAYLOAD_MARKERS = (
    "owl:imports",
    "owl:equivalentClass",
    "sh:NodeShape",
    "swrl:",
    "annotation.conf",
    "right_sample.owl",
    "LegalAgent-LegalEntity",
    "LegalAgent-LegalAgent",
    "LegalEntity-LegalAgent",
    "LegalEntity-LegalEntity",
    "LegalAgent-LegalConcept",
    "annotations.jsonl",
    "subvenciones",
    "desgravaciones",
    "Ningún",
    "contratado en prácticas",
)

_SIGNATURE_RE = re.compile(
    r"Legal(?:Agent|Entity|Concept)-Legal(?:Agent|Entity|Concept)"
)


class C2SchemaError(ValueError):
    """The C2 package or a caller-supplied mutation is not valid."""


def canonical_dumps(document: dict[str, Any]) -> str:
    """Serialize with the repository's deterministic JSON profile."""
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_c1_labels(path: Path = C1_PATH) -> list[str]:
    """Return the frozen C1 label inventory."""
    document = json.loads(path.read_text(encoding="utf-8"))
    labels = document.get("labels")
    if not isinstance(labels, list) or not labels:
        raise C2SchemaError(f"C1 schema at {path} has no label list.")
    if any(not isinstance(label, str) for label in labels):
        raise C2SchemaError(f"C1 schema at {path} contains a non-string label.")
    return list(labels)


def _without_integrity(package: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in package.items() if key != "integrity"}


def content_sha256(package: dict[str, Any]) -> str:
    """Hash the knowledge package excluding its integrity block."""
    return _sha256(canonical_dumps(_without_integrity(package)))


def validate_c2_package(
    package: dict[str, Any],
    c1_labels: list[str] | None = None,
    *,
    require_integrity: bool = True,
) -> None:
    """Raise C2SchemaError when the package violates C2 invariants."""
    if not isinstance(package, dict):
        raise C2SchemaError("C2 package must be a JSON object.")
    missing = [key for key in _REQUIRED_PACKAGE_KEYS if key not in package]
    if missing and not (missing == ["integrity"] and not require_integrity):
        raise C2SchemaError(
            "C2 package is missing required keys: " + ", ".join(missing)
        )
    if package.get("package_id") != PACKAGE_ID:
        raise C2SchemaError(
            f"Expected package_id {PACKAGE_ID}, found {package.get('package_id')!r}."
        )
    if package.get("package_version") != PACKAGE_VERSION:
        raise C2SchemaError(
            f"Expected package_version {PACKAGE_VERSION}, "
            f"found {package.get('package_version')!r}."
        )
    if package.get("condition_id") != "C2":
        raise C2SchemaError("C2 package condition_id must be 'C2'.")

    contract = package.get("output_contract")
    if not isinstance(contract, dict) or contract.get("slots") != [
        "subject",
        "relation",
        "object",
    ]:
        raise C2SchemaError(
            "C2 output contract must remain (subject, relation, object)."
        )

    labels = c1_labels if c1_labels is not None else load_c1_labels()
    relations = package.get("relations")
    if not isinstance(relations, list):
        raise C2SchemaError("C2 relations must be a list.")
    relation_ids = []
    for relation in relations:
        if not isinstance(relation, dict):
            raise C2SchemaError("Each C2 relation must be an object.")
        absent = [key for key in _REQUIRED_RELATION_KEYS if key not in relation]
        if absent:
            raise C2SchemaError(
                f"Relation {relation.get('id')!r} is missing keys: "
                + ", ".join(absent)
            )
        if not str(relation["definition"]).strip():
            raise C2SchemaError(
                f"Relation {relation['id']!r} has an empty definition."
            )
        if not relation.get("sources"):
            raise C2SchemaError(
                f"Relation {relation['id']!r} has no provenance sources."
            )
        relation_ids.append(relation["id"])
    if relation_ids != labels:
        raise C2SchemaError(
            "C2 relation ids must equal the C1 inventory in the same order. "
            f"Found {relation_ids!r}; C1 is {labels!r}."
        )

    entity_types = package.get("entity_types")
    if not isinstance(entity_types, list) or not entity_types:
        raise C2SchemaError("C2 entity_types must be a non-empty list.")
    for entity_type in entity_types:
        if not isinstance(entity_type, dict) or "id" not in entity_type:
            raise C2SchemaError("Each entity type must be an object with an id.")
        status = entity_type.get("definition_status")
        if status == "UNRESOLVED_DEFINITION":
            if entity_type.get("definition") not in (None, ""):
                raise C2SchemaError(
                    f"Unresolved entity type {entity_type['id']!r} must not "
                    "carry a definition."
                )
            if entity_type.get("include_in_payload") is True:
                raise C2SchemaError(
                    f"Unresolved entity type {entity_type['id']!r} must not be "
                    "projected into the extractor payload as a definition."
                )
        elif status != "DEFINED":
            raise C2SchemaError(
                f"Entity type {entity_type['id']!r} has unknown "
                f"definition_status {status!r}."
            )

    constructs = package.get("annotation_constructs")
    if not isinstance(constructs, list) or not constructs:
        raise C2SchemaError("C2 annotation_constructs must be a non-empty list.")
    exclusions = package.get("exclusions")
    if not isinstance(exclusions, list) or not exclusions:
        raise C2SchemaError("C2 exclusions must be a non-empty list.")
    exclusion_ids = {item.get("id") for item in exclusions if isinstance(item, dict)}
    for required_exclusion in (
        "gold_examples",
        "silver_examples",
        "gold_signatures_as_axioms",
        "unverified_domain_range",
        "brat_grids",
        "external_ontology_import",
        "few_shot_examples",
    ):
        if required_exclusion not in exclusion_ids:
            raise C2SchemaError(
                f"C2 package does not record the required exclusion "
                f"{required_exclusion!r}."
            )

    serialized = canonical_dumps(package)
    if _SIGNATURE_RE.search(serialized):
        raise C2SchemaError(
            "C2 package contains an observed relation-signature string."
        )
    lowered = serialized.lower()
    for marker in ("owl:imports", "sh:nodeshape", "swrl:"):
        if marker in lowered:
            raise C2SchemaError(
                f"C2 package contains forbidden formal marker {marker!r}."
            )

    if require_integrity:
        integrity = package.get("integrity")
        if not isinstance(integrity, dict):
            raise C2SchemaError("C2 integrity block must be an object.")
        expected_content = content_sha256(package)
        if integrity.get("content_sha256") != expected_content:
            raise C2SchemaError(
                "C2 content_sha256 does not match the canonical package bytes."
            )
        payload = project_model_payload(package)
        expected_payload = _sha256(canonical_dumps(payload))
        if integrity.get("payload_sha256") != expected_payload:
            raise C2SchemaError(
                "C2 payload_sha256 does not match the projected payload."
            )
        _reject_forbidden_payload(payload)


def project_model_payload(package: dict[str, Any]) -> dict[str, Any]:
    """Project extractor-facing text. Does not copy provenance or exclusions."""
    relations = []
    for relation in package["relations"]:
        relations.append(
            {
                "id": relation["id"],
                "name": relation["legal_name"],
                "definition": relation["definition"],
                "relational_semantics": relation["relational_semantics"],
                "correlative": relation["correlative"]["statement"],
                "opposite": relation["opposite"]["statement"],
                "direction": relation["direction"]["statement"],
            }
        )
    guidelines = []
    for construct in package["annotation_constructs"]:
        if construct.get("include_in_payload") is not True:
            continue
        if construct.get("verification_status") == "UNRESOLVED_DEFINITION":
            raise C2SchemaError(
                f"Annotation construct {construct.get('id')!r} is unresolved "
                "and cannot be sent to the extractor."
            )
        guidelines.append(
            {
                "id": construct["id"],
                "statement": construct["payload_statement"],
            }
        )
    for entity_type in package["entity_types"]:
        if entity_type.get("definition_status") == "UNRESOLVED_DEFINITION":
            if entity_type.get("include_in_payload") is True:
                raise C2SchemaError(
                    f"Unresolved entity type {entity_type['id']!r} cannot be "
                    "sent to the extractor as a definition."
                )
            if entity_type.get("definition") not in (None, ""):
                raise C2SchemaError(
                    f"Unresolved entity type {entity_type['id']!r} has a "
                    "definition that would leak into conditioning."
                )
    abstract_roles = {}
    for role_id in ("bearer", "counterpart", "normative_content", "textual_arguments"):
        role = package["abstract_roles"][role_id]
        if role.get("include_in_payload") is False:
            continue
        if role_id == "textual_arguments":
            abstract_roles[role_id] = _role_payload_text(role)
        else:
            abstract_roles[role_id] = role["statement"]
    payload = {
        "relation_labels": [relation["id"] for relation in relations],
        "normative_scope": package["normative_scope"]["statement"],
        "action_polarity": package["action_polarity"]["statement"],
        "relations": relations,
        "abstract_roles": abstract_roles,
    }
    if guidelines:
        payload["annotation_guidelines"] = guidelines
    return payload


def _role_payload_text(role: dict[str, Any]) -> str:
    """Use the prompt wording when the knowledge statement names annotation tags."""
    payload_statement = role.get("payload_statement")
    if isinstance(payload_statement, str) and payload_statement.strip():
        return payload_statement
    return role["statement"]


def _reject_forbidden_payload(payload: dict[str, Any]) -> None:
    serialized = canonical_dumps(payload)
    for marker in _FORBIDDEN_PAYLOAD_MARKERS:
        if marker in serialized:
            raise C2SchemaError(
                f"C2 payload contains forbidden marker {marker!r}."
            )
    if _SIGNATURE_RE.search(serialized):
        raise C2SchemaError("C2 payload contains a relation-signature string.")
    for key in ("sources", "exclusions", "provenance", "example", "examples"):
        if key in payload:
            raise C2SchemaError(
                f"C2 payload must not contain knowledge-package key {key!r}."
            )


def model_payload(package: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate the package and return the extractor-facing projection."""
    document = package if package is not None else load_c2_package()
    validate_c2_package(document)
    payload = project_model_payload(document)
    _reject_forbidden_payload(payload)
    return payload


def load_c2_package(path: Path = PACKAGE_PATH) -> dict[str, Any]:
    """Load the checked-in C2 package and reject a drifted or invalid file."""
    if not path.is_file():
        raise C2SchemaError(f"C2 package file does not exist: {path}")
    package = json.loads(path.read_text(encoding="utf-8"))
    validate_c2_package(package)
    return package


def attach_integrity(package: dict[str, Any]) -> dict[str, Any]:
    """Return a copy whose integrity hashes match the canonical bytes."""
    body = _without_integrity(package)
    provisional = dict(body)
    provisional["integrity"] = {
        "canonicalization": "json.dumps ensure_ascii=false indent=2 trailing-newline",
        "content_sha256": _sha256(canonical_dumps(body)),
        "payload_sha256": "",
    }
    payload_hash = _sha256(canonical_dumps(project_model_payload(provisional)))
    provisional["integrity"]["payload_sha256"] = payload_hash
    validate_c2_package(provisional)
    return provisional
