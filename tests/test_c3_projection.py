"""Projection tests for the unapproved C3 and C3-NL payloads.

These tests check that the experimental surfaces contain the same asserted
axioms, that absent axioms stay outside those surfaces, and that serialization
is deterministic. They do not run an OWL reasoner and they do not authorize
the experimental condition.
"""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from re_te_benchmark.conditioning.c2 import (  # noqa: E402
    canonical_dumps,
    content_sha256,
    load_c1_labels,
    load_c2_package,
    model_payload,
)
from re_te_benchmark.conditioning.c3 import (  # noqa: E402
    C2_CONTENT_SHA256,
    C2_PAYLOAD_SHA256,
    ONTOLOGY_IRI,
    ONTOLOGY_SHA256,
    PACKAGE_CONTENT_SHA256,
    VOCABULARY_IRI,
    audit_axiom_records,
    c3_model_payload,
    c3_nl_model_payload,
    select_axioms,
    validate_c3_ontology,
)


FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "c3"
GOLD_MARKERS = (
    "LegalAgent",
    "LegalEntity",
    "LegalConcept",
    "Estatuto",
    "trabajador",
    "empresa",
    "subvenciones",
    "owl:imports",
    "subject = bearer",
    "object = counterpart",
    "e1 = bearer",
    "e2 = counterpart",
    "few-shot",
    "For example",
)
FORBIDDEN_NL = (
    "not functional",
    "not symmetric",
    "not closed",
    "No link",
    "No polarity",
    "No act",
    "asymmetric",
    "at most",
    "at least",
    "exactly one",
    "must ",
    "forbidden",
    "ComplementOf",
    "oneOf",
    "someValuesFrom",
    "minCardinality",
    "ObjectSomeValuesFrom",
    "ObjectMinCardinality",
)
FORBIDDEN_OWL = (
    "FunctionalObjectProperty(h:hasAct)",
    "ObjectSomeValuesFrom",
    "ObjectOneOf",
    "ObjectComplementOf",
    "ObjectMinCardinality",
    "owl:imports",
    "Import(",
)


class C3ProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.c2 = model_payload()
        cls.c2_text = canonical_dumps(cls.c2)
        cls.c3 = c3_model_payload()
        cls.nl = c3_nl_model_payload()
        cls.c3_text = canonical_dumps(cls.c3)
        cls.nl_text = canonical_dumps(cls.nl)
        cls.graph = validate_c3_ontology()
        cls.records = select_axioms(cls.graph)
        cls.audit = audit_axiom_records(cls.graph)

    def test_pinned_hashes_match_the_live_bytes(self) -> None:
        live = load_c2_package()
        self.assertEqual(live["integrity"]["content_sha256"], C2_CONTENT_SHA256)
        self.assertEqual(live["integrity"]["payload_sha256"], C2_PAYLOAD_SHA256)
        self.assertEqual(content_sha256(live), C2_CONTENT_SHA256)
        ontology_path = PROJECT_ROOT / "schemas" / "c3" / "c3_ontology_v1.ttl"
        ontology_hash = hashlib.sha256(
            ontology_path.read_text(encoding="utf-8").encode("utf-8")
        ).hexdigest()
        self.assertEqual(ontology_hash, ONTOLOGY_SHA256)
        package = json.loads(
            (PROJECT_ROOT / "schemas" / "c3" / "c3_ontology_v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(package["integrity"]["content_sha256"], PACKAGE_CONTENT_SHA256)
        self.assertEqual(package["ontology"]["sha256"], ONTOLOGY_SHA256)
        self.assertEqual(package["ontology"]["version"], "1.0.1")
        self.assertEqual(package["c2_dependency"]["content_sha256"], C2_CONTENT_SHA256)
        self.assertEqual(package["c2_dependency"]["payload_sha256"], C2_PAYLOAD_SHA256)
        self.assertEqual(load_c1_labels(), ["Duty", "Right", "Privilege", "NoRight"])
        manifest = json.loads(
            (PROJECT_ROOT / "schemas" / "conditioning_conditions.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["conditions"]["C3"]["readiness"], "NOT_READY")
        self.assertEqual(package["experimental_condition_status"], "NOT_EXECUTABLE")
        self.assertNotIn("payload", package)
        self.assertNotIn("owl_functional", package)
        self.assertNotIn("formal", package)

    def test_shared_c2_block_is_identical_after_removing_the_formal_key(self) -> None:
        for payload, extra in ((self.c3, "owl_functional"), (self.nl, "formal_natural")):
            reduced = dict(payload)
            self.assertEqual(list(reduced)[-1], extra)
            del reduced[extra]
            self.assertEqual(canonical_dumps(reduced), self.c2_text)
        self.assertEqual(self.c3["relations"], self.c2["relations"])
        self.assertEqual(self.nl["abstract_roles"], self.c2["abstract_roles"])
        self.assertNotIn("owl_functional", self.c2)
        self.assertNotIn("formal", self.c2)
        self.assertNotIn("formal_natural", self.c2)
        self.assertNotIn("extraction_boundaries", self.c2)
        self.assertNotIn("textual_arguments", self.c2["abstract_roles"])
        self.assertNotIn("no domain constraints", self.c2_text)
        self.assertNotIn("output slots", self.c2_text)
        self.assertNotIn("ObjectPropertyDomain", self.c2_text)

    def test_asserted_axioms_are_separated_from_unspecified_absences(self) -> None:
        included = [record for record in self.records if record["included"] is True]
        self.assertEqual(included, self.records)
        self.assertTrue(all(record["status"] == "ASSERTED_AXIOM" for record in included))
        unspecified = [record for record in self.audit if record["status"] == "UNSPECIFIED"]
        self.assertGreaterEqual(len(unspecified), 1)
        self.assertTrue(all(record["included"] is False for record in unspecified))
        self.assertTrue(all(record["owl"] == "" and record["natural"] == "" for record in unspecified))
        self.assertNotIn("NOT_ENTAILED", {record["status"] for record in self.audit})
        self.assertNotIn("ENTAILED", {record["status"] for record in self.audit})
        functional = [record["id"] for record in included if record["id"].startswith("functional-")]
        self.assertEqual(functional, ["functional-hasPolarity"])
        self.assertIn("functionality-unspecified-hasAct", {record["id"] for record in unspecified})
        for marker in ("UNSPECIFIED", "functionality-unspecified", "not an assertion"):
            self.assertNotIn(marker, self.c3_text)
            self.assertNotIn(marker, self.nl_text)

    def test_owl_and_natural_language_state_the_same_axioms(self) -> None:
        owl = self.c3["owl_functional"]
        natural = self.nl["formal_natural"]
        self.assertEqual([item["id"] for item in natural], [record["id"] for record in self.records])
        self.assertEqual(len(natural), len({item["id"] for item in natural}))
        self.assertTrue(owl.startswith(f"Prefix(h:=<{VOCABULARY_IRI}>)\n"))
        self.assertIn(f"Ontology(<{ONTOLOGY_IRI}>", owl)
        self.assertTrue(owl.endswith(")\n"))
        for record, item in zip(self.records, natural, strict=True):
            self.assertEqual(item["id"], record["id"])
            self.assertEqual(item["text"], record["natural"])
            self.assertEqual(owl.count(record["owl"]), 1)
        for marker in (
            "Declaration(Class(h:Duty))",
            "ObjectUnionOf(h:Duty h:Right h:Privilege h:NoRight)",
            "DisjointClasses(h:Duty h:Right h:Privilege h:NoRight)",
            "ObjectPropertyDomain(h:hasBearer h:FirstOrderPosition)",
            "ObjectPropertyRange(h:hasBearer h:Party)",
            "SymmetricObjectProperty(h:correlatesWith)",
            "IrreflexiveObjectProperty(h:oppositeOf)",
            "FunctionalObjectProperty(h:hasPolarity)",
            "DisjointObjectProperties(h:correlatesWith h:oppositeOf)",
            "ObjectAllValuesFrom(h:correlatesWith h:Right)",
            "DifferentIndividuals(h:Forbearance h:Performance)",
        ):
            self.assertIn(marker, owl)
        for marker in FORBIDDEN_OWL:
            self.assertNotIn(marker, owl)
        natural_text = "\n".join(item["text"] for item in natural)
        for marker in FORBIDDEN_NL:
            self.assertNotIn(marker, natural_text)
        self.assertNotIn("urn:example", natural_text)
        self.assertNotIn("PROVISIONAL", natural_text)
        self.assertIn("hasPolarity is functional", natural_text)
        self.assertIn("no more than one distinct polarity", natural_text)
        self.assertIn("every linked individual is a Right", natural_text)
        self.assertNotIn("filler", natural_text)
        self.assertIn("exactly the union of Duty, Right, Privilege, and NoRight", natural_text)
        self.assertNotIn("hasAct is functional", natural_text)

    def test_serialization_is_deterministic_and_lengths_are_recorded(self) -> None:
        self.assertEqual(canonical_dumps(c3_model_payload()), self.c3_text)
        self.assertEqual(canonical_dumps(c3_nl_model_payload()), self.nl_text)
        self.assertEqual(select_axioms(self.graph), self.records)
        self.assertNotEqual(self.c3_text, self.nl_text)
        self.assertGreater(len(self.c3_text), len(self.c2_text))
        self.assertGreater(len(self.nl_text), len(self.c3_text))
        spec = (PROJECT_ROOT / "docs" / "CONDITIONING_SPEC.md").read_text(encoding="utf-8")
        self.assertIn(
            f"{len(self.c2_text)} characters for C2, {len(self.c3_text)} for "
            "the OWL projection payload",
            spec,
        )
        self.assertIn(
            f"{len(self.nl_text)} for the natural-language control",
            spec,
        )

    def test_payloads_exclude_gold_contracts_and_audit_metadata(self) -> None:
        for text in (self.c3["owl_functional"], canonical_dumps(self.nl["formal_natural"])):
            for marker in GOLD_MARKERS:
                self.assertNotIn(marker, text)
            self.assertNotIn("sha256", text)
        for payload in (self.c2, self.c3, self.nl):
            self.assertNotIn("output_contract", payload)
            self.assertNotIn("examples", payload)
            self.assertNotIn("prompt", payload)
        self.assertEqual(
            list(load_c2_package()["output_contract"]["slots"]),
            ["subject", "relation", "object"],
        )

    def test_fixtures_remain_synthetic(self) -> None:
        for path in FIXTURE_DIR.glob("*.ttl"):
            text = path.read_text(encoding="utf-8")
            for marker in ("Estatuto", "trabajador", "LegalAgent"):
                self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()
