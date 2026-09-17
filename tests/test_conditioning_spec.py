from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "schemas" / "conditioning_conditions.json"
C1_PATH = PROJECT_ROOT / "schemas" / "c1" / "hohfeld_labels.json"
SPEC_PATH = PROJECT_ROOT / "docs" / "CONDITIONING_SPEC.md"
PROVENANCE_PATH = PROJECT_ROOT / "docs" / "CONDITIONING_PROVENANCE.md"


class ConditioningSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
        cls.manifest = json.loads(cls.manifest_text)
        cls.conditions = cls.manifest["conditions"]
        cls.spec_text = SPEC_PATH.read_text(encoding="utf-8")
        cls.provenance_text = PROVENANCE_PATH.read_text(encoding="utf-8")

    @classmethod
    def provenance_row(cls, asset: str) -> list[str]:
        prefix = f"| {asset} |"
        matches = [
            line
            for line in cls.provenance_text.splitlines()
            if line.startswith(prefix)
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"Expected one provenance row for {asset!r}, found {len(matches)}"
            )
        return [cell.strip() for cell in matches[0].strip("|").split("|")]

    def test_c1_contains_exactly_four_labels(self) -> None:
        c1 = json.loads(C1_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            c1["labels"],
            ["Duty", "Right", "Privilege", "NoRight"],
        )
        self.assertEqual(len(c1["labels"]), 4)
        self.assertEqual(len(set(c1["labels"])), 4)

    def test_c0_forbids_all_target_schema_components(self) -> None:
        c0 = self.conditions["C0"]
        c3 = self.conditions["C3"]
        all_target_components = set(c3["permitted_knowledge_components"]) | set(
            c3["forbidden_knowledge_components"]
        )
        self.assertEqual(c0["permitted_knowledge_components"], [])
        self.assertEqual(
            set(c0["forbidden_knowledge_components"]),
            all_target_components,
        )

    def test_c1_permits_only_labels(self) -> None:
        c1 = self.conditions["C1"]
        self.assertEqual(c1["permitted_knowledge_components"], ["relation_labels"])
        for forbidden in (
            "relation_definitions",
            "entity_type_vocabulary",
            "relation_signatures",
            "examples",
            "gold_frequencies_statistics",
            "silver_examples",
        ):
            self.assertIn(forbidden, c1["forbidden_knowledge_components"])

    def test_c2_is_not_ready_with_required_gaps(self) -> None:
        c2 = self.conditions["C2"]
        self.assertEqual(c2["readiness"], "PARTIAL")
        self.assertIn("relation_definitions", c2["unresolved_components"])
        self.assertIn("argument_role_semantics", c2["unresolved_components"])
        self.assertIn(
            "normative_domain_constraints",
            c2["unresolved_components"],
        )
        self.assertIn(
            "normative_range_constraints",
            c2["unresolved_components"],
        )

    def test_c3_is_not_ready_with_formal_gaps(self) -> None:
        c3 = self.conditions["C3"]
        self.assertEqual(c3["readiness"], "NOT_READY")
        for unresolved in (
            "stable_uris",
            "formal_classes_properties",
            "formal_relationships_and_constraints",
            "justified_axioms",
        ):
            self.assertIn(unresolved, c3["unresolved_components"])

    def test_manifest_contains_no_gold_or_silver_payloads(self) -> None:
        forbidden_payload_keys = {
            "example",
            "examples",
            "frequency",
            "frequencies",
            "gold_example",
            "gold_examples",
            "gold_statistics",
            "silver_example",
            "silver_examples",
        }

        def keys(value: Any) -> set[str]:
            if isinstance(value, dict):
                return set(value) | {
                    nested_key
                    for nested_value in value.values()
                    for nested_key in keys(nested_value)
                }
            if isinstance(value, list):
                return {
                    nested_key
                    for nested_value in value
                    for nested_key in keys(nested_value)
                }
            return set()

        self.assertTrue(forbidden_payload_keys.isdisjoint(keys(self.manifest)))
        self.assertNotIn("Duty", self.manifest_text)
        self.assertNotIn("LegalAgent-LegalEntity", self.manifest_text)

    def test_missing_e1_is_an_original_annotation_construct(self) -> None:
        self.assertIn(
            "`MissingE1`, `MissingE2`, `RelationType`, and `RelationSignature`",
            self.spec_text,
        )
        role = self.provenance_row("MissingE1 role/concept")
        concrete = self.provenance_row("concrete MissingE1 values")
        self.assertEqual(role[4], "ORIGINAL_DESIGN")
        self.assertEqual(role[6:8], ["CONDITIONAL", "CONDITIONAL"])
        self.assertEqual(concrete[4], "OBSERVED_IN_GOLD")
        self.assertEqual(concrete[5:8], ["NO", "NO", "NO"])
        self.assertEqual(concrete[9], "EXCLUDE")
        self.assertIn(
            "MUST NOT be exposed in\nany C0–C3 conditioning payload",
            self.spec_text,
        )

    def test_missing_e1_and_missing_e2_leakage_policy_is_symmetric(self) -> None:
        missing_e1_role = self.provenance_row("MissingE1 role/concept")
        missing_e2_role = self.provenance_row("MissingE2 role/concept")
        missing_e1_values = self.provenance_row("concrete MissingE1 values")
        missing_e2_values = self.provenance_row("concrete MissingE2 values")
        self.assertEqual(missing_e1_role[4:10], missing_e2_role[4:10])
        self.assertEqual(missing_e1_values[4:10], missing_e2_values[4:10])
        self.assertIn(
            "Concrete values are Gold content and MUST NOT be exposed.",
            missing_e1_values[10],
        )
        self.assertIn(
            "Concrete values are Gold content and MUST NOT be exposed.",
            missing_e2_values[10],
        )

    def test_readiness_is_unchanged_by_missing_e1_correction(self) -> None:
        self.assertEqual(
            {
                condition_id: condition["readiness"]
                for condition_id, condition in self.conditions.items()
            },
            {
                "C0": "READY",
                "C1": "READY",
                "C2": "PARTIAL",
                "C3": "NOT_READY",
            },
        )

    def test_serialization_and_order_are_deterministic(self) -> None:
        expected = json.dumps(
            self.manifest,
            ensure_ascii=False,
            indent=2,
        ) + "\n"
        self.assertEqual(self.manifest_text, expected)
        self.assertEqual(list(self.manifest), ["schema_version", "conditions"])
        self.assertEqual(list(self.conditions), ["C0", "C1", "C2", "C3"])
        expected_condition_keys = [
            "id",
            "name",
            "description",
            "permitted_knowledge_components",
            "forbidden_knowledge_components",
            "readiness",
            "unresolved_components",
        ]
        for condition in self.conditions.values():
            self.assertEqual(list(condition), expected_condition_keys)


if __name__ == "__main__":
    unittest.main()
