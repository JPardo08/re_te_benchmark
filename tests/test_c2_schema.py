from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from re_te_benchmark.conditioning.c2 import (  # noqa: E402
    C2SchemaError,
    attach_integrity,
    canonical_dumps,
    content_sha256,
    load_c1_labels,
    load_c2_package,
    model_payload,
    validate_c2_package,
)


CONDITIONS_PATH = PROJECT_ROOT / "schemas" / "conditioning_conditions.json"
PACKAGE_PATH = PROJECT_ROOT / "schemas" / "c2" / "c2_schema_v1.json"
SIGNATURE_RE = re.compile(
    r"Legal(?:Agent|Entity|Concept)-Legal(?:Agent|Entity|Concept)"
)


class C2SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.conditions = json.loads(CONDITIONS_PATH.read_text(encoding="utf-8"))
        cls.package = load_c2_package()
        cls.payload = model_payload(cls.package)
        cls.payload_text = canonical_dumps(cls.payload)
        cls.package_text = PACKAGE_PATH.read_text(encoding="utf-8")

    def test_c0_has_no_target_schema_knowledge(self) -> None:
        c0 = self.conditions["conditions"]["C0"]
        self.assertEqual(c0["permitted_knowledge_components"], [])
        self.assertIn("relation_definitions", c0["forbidden_knowledge_components"])
        self.assertIn("formal_axioms", c0["forbidden_knowledge_components"])

    def test_c1_inventory_is_exact_and_reused(self) -> None:
        labels = load_c1_labels()
        self.assertEqual(labels, ["Duty", "Right", "Privilege", "NoRight"])
        self.assertEqual(
            [relation["id"] for relation in self.package["relations"]],
            labels,
        )
        self.assertEqual(self.payload["relation_labels"], labels)

    def test_definitions_have_identifiable_provenance(self) -> None:
        for relation in self.package["relations"]:
            self.assertTrue(relation["definition"].strip())
            self.assertIn("hohfeld_1913", relation["sources"])
            self.assertEqual(
                relation["verification_status"],
                "PARAPHRASE_OF_PRIMARY_SOURCE",
            )
            self.assertTrue(relation["correlative"]["statement"].strip())
            self.assertTrue(relation["opposite"]["statement"].strip())

    def test_payload_has_no_gold_or_silver_examples(self) -> None:
        for marker in (
            "subvenciones",
            "desgravaciones",
            "Ningún",
            "contratado en prácticas",
            "annotations.jsonl",
            "right_sample.owl",
        ):
            self.assertNotIn(marker, self.payload_text)
            self.assertNotIn(marker, self.package_text)
        for marker in ("Gold", "Silver"):
            self.assertNotIn(marker, self.payload_text)

    def test_signatures_are_not_axioms(self) -> None:
        self.assertIsNone(SIGNATURE_RE.search(self.package_text))
        self.assertIsNone(SIGNATURE_RE.search(self.payload_text))
        self.assertIn(
            "gold_signatures_as_axioms",
            {item["id"] for item in self.package["exclusions"]},
        )

    def test_domain_and_range_are_absent(self) -> None:
        def keys(value: object) -> set[str]:
            if isinstance(value, dict):
                found = set(value)
                for nested in value.values():
                    found |= keys(nested)
                return found
            if isinstance(value, list):
                found: set[str] = set()
                for nested in value:
                    found |= keys(nested)
                return found
            return set()

        forbidden = {
            "domain",
            "range",
            "domain_constraints",
            "range_constraints",
        }
        self.assertTrue(forbidden.isdisjoint(keys(self.package)))
        self.assertTrue(forbidden.isdisjoint(keys(self.payload)))
        unresolved = self.conditions["conditions"]["C2"]["unresolved_components"]
        self.assertIn("normative_domain_constraints", unresolved)
        self.assertIn("normative_range_constraints", unresolved)

    def test_no_owl_shacl_or_swrl(self) -> None:
        lowered = self.package_text.lower()
        for marker in ("owl:imports", "owl:equivalentclass", "sh:nodeshape", "swrl:"):
            self.assertNotIn(marker, lowered)
            self.assertNotIn(marker, self.payload_text.lower())

    def test_metadata_is_separated_from_payload(self) -> None:
        for key in ("exclusions", "provenance_notes", "integrity"):
            self.assertIn(key, self.package)
            self.assertNotIn(key, self.payload)
        self.assertIn("sources", self.package["relations"][0])
        self.assertNotIn("sources", self.payload["relations"][0])
        self.assertNotIn("unresolved_reason", self.payload_text)
        self.assertNotIn("not_adopted", self.payload_text)
        self.assertIn("hohfeld_1913", self.package_text)
        self.assertNotIn("doi.org", self.payload_text)

    def test_unresolved_entity_types_are_not_extractor_instructions(self) -> None:
        self.assertEqual(
            [item["id"] for item in self.package["entity_types"]],
            ["LegalAgent", "LegalEntity", "LegalConcept"],
        )
        for entity_type in self.package["entity_types"]:
            self.assertEqual(entity_type["definition_status"], "UNRESOLVED_DEFINITION")
            self.assertIsNone(entity_type["definition"])
            self.assertFalse(entity_type["include_in_payload"])
        for name in ("LegalAgent", "LegalEntity", "LegalConcept"):
            self.assertNotIn(name, self.payload_text)
        self.assertNotIn("person/entity/object", self.payload_text)

    def test_serialization_and_hash_are_stable(self) -> None:
        self.assertEqual(self.package_text, canonical_dumps(self.package))
        again = load_c2_package()
        self.assertEqual(
            again["integrity"]["content_sha256"],
            self.package["integrity"]["content_sha256"],
        )
        self.assertEqual(
            again["integrity"]["payload_sha256"],
            self.package["integrity"]["payload_sha256"],
        )
        rebuilt = attach_integrity(copy.deepcopy(self.package))
        self.assertEqual(
            rebuilt["integrity"]["content_sha256"],
            content_sha256(self.package),
        )
        self.assertEqual(canonical_dumps(model_payload(rebuilt)), self.payload_text)

    def test_invalid_structure_fails_explicitly(self) -> None:
        broken = copy.deepcopy(self.package)
        del broken["relations"]
        with self.assertRaises(C2SchemaError):
            validate_c2_package(broken)
        with self.assertRaises(C2SchemaError):
            validate_c2_package(["not", "an", "object"])

    def test_unresolved_definition_cannot_be_projected(self) -> None:
        mutated = copy.deepcopy(self.package)
        mutated["entity_types"][0]["definition"] = "A natural person."
        mutated["entity_types"][0]["include_in_payload"] = True
        with self.assertRaises(C2SchemaError):
            model_payload(mutated)

    def test_output_contract_is_unchanged(self) -> None:
        self.assertEqual(
            self.package["output_contract"]["slots"],
            ["subject", "relation", "object"],
        )
        self.assertNotIn("output_contract", self.payload)
        self.assertNotIn("e1 = bearer", self.payload_text)
        self.assertNotIn("e2 = counterpart", self.payload_text)

    def test_payload_omits_annotation_markers_and_shell_instructions(self) -> None:
        for marker in (
            "MissingE1",
            "MissingE2",
            "e1",
            "e2",
            "Do not invent",
            "Do not swap",
            "Do not emit",
            "annotated example",
            "C2_SCHEMA_V1",
        ):
            self.assertNotIn(marker, self.payload_text)
        self.assertNotIn("condition_id", self.payload)
        self.assertNotIn("annotation_guidelines", self.payload)
        included = [
            item["id"]
            for item in self.package["annotation_constructs"]
            if item["include_in_payload"] is True
        ]
        self.assertEqual(included, [])
        self.assertIn(
            "annotation_marker_instructions",
            {item["id"] for item in self.package["exclusions"]},
        )
        self.assertIn("correlative", self.payload["relations"][0])
        self.assertIn("action_polarity", self.payload)

    def test_privilege_definition_separates_the_two_polarities(self) -> None:
        privilege = next(item for item in self.package["relations"] if item["id"] == "Privilege")
        definition = privilege["definition"]
        self.assertIn("privilege to perform", definition)
        self.assertIn("absence of a duty, toward that other party, to refrain", definition)
        self.assertIn("privilege to refrain", definition)
        self.assertIn("absence of a duty, toward that other party, to perform", definition)
        self.assertNotIn("either to perform or to refrain", definition)
        self.assertIn(definition, self.payload_text)
        self.assertEqual(
            [item["id"] for item in self.package["relations"]],
            ["Duty", "Right", "Privilege", "NoRight"],
        )
        notes = {item["id"] for item in self.package["provenance_notes"]}
        self.assertIn("privilege_polarity_c3_2c", notes)
        self.assertIn(
            "privilege to perform an act is the opposite of a duty to refrain",
            self.package["action_polarity"]["statement"],
        )

    def test_annotation_boundaries_stay_out_of_the_shared_payload(self) -> None:
        boundary = self.package["extraction_boundaries"][0]
        self.assertIn("annotation entity-type", boundary)
        self.assertNotIn("extraction_boundaries", self.payload)
        self.assertNotIn(boundary, self.payload_text)
        self.assertNotIn("no domain constraints, and no range constraints", self.payload_text)
        role = self.package["abstract_roles"]["textual_arguments"]
        self.assertIs(role["include_in_payload"], False)
        self.assertNotIn("textual_arguments", self.payload["abstract_roles"])
        self.assertNotIn("output slots", self.payload_text)
        self.assertIn("bearer", self.payload["abstract_roles"])
        self.assertIn("counterpart", self.payload["abstract_roles"])
        self.assertIn("normative_content", self.payload["abstract_roles"])
        exclusion_ids = {item["id"] for item in self.package["exclusions"]}
        self.assertIn("annotation_type_domain_range_boundary", exclusion_ids)
        self.assertIn("textual_argument_contract", exclusion_ids)


if __name__ == "__main__":
    unittest.main()
