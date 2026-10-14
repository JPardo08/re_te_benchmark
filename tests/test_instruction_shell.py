"""Tests for the shared C0-C3 instruction shell.

These tests check identity, the empty C0 slot, and the existing output-field
contract. They do not call a model or a parser in re_te_system.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from re_te_benchmark.conditioning.c2 import load_c1_labels  # noqa: E402
from re_te_benchmark.conditioning.shell import (  # noqa: E402
    CONDITIONS,
    SHELL_ID,
    conditioning_for,
    render_condition,
    render_instruction,
    shell_template,
)


TEXT = "The company pays the worker."
LABELS = ("Duty", "Right", "Privilege", "NoRight")
LEAKS = (
    "Hohfeld",
    "bearer",
    "counterpart",
    "e1",
    "e2",
    "Gold",
    "Silver",
    "LegalAgent",
    "estatuto",
    "few-shot",
    "basic-v1",
    "gollie-prompt-v1",
)


class InstructionShellTests(unittest.TestCase):
    def test_template_is_stable_and_has_one_conditioning_slot(self) -> None:
        template = shell_template()
        self.assertEqual(SHELL_ID, "common-instruction-shell-v1")
        self.assertEqual(template.count("[[CONDITIONING]]"), 1)
        self.assertEqual(template.count("[[TEXT]]"), 1)
        self.assertIn("subject, relation, object", template)
        self.assertIn("one tab", template)
        for marker in (*LABELS, *LEAKS):
            self.assertNotIn(marker, template)
        again = render_instruction("", TEXT)
        self.assertEqual(again, render_instruction("", TEXT))

    def test_only_the_conditioning_slot_changes_across_conditions(self) -> None:
        template = shell_template()
        bodies = []
        for condition in CONDITIONS:
            slot = conditioning_for(condition)
            rendered = render_condition(condition, TEXT)
            expected = template.replace("[[CONDITIONING]]", slot, 1).replace("[[TEXT]]", TEXT, 1)
            self.assertEqual(rendered, expected)
            bodies.append(expected.replace(slot, "[[SLOT]]", 1) if slot else expected.replace("\n\nInput text:\n", "\n[[SLOT]]\nInput text:\n", 1))
        self.assertEqual(len(set(bodies)), 1)
        self.assertEqual(conditioning_for("C0"), "")
        c0 = render_condition("C0", TEXT)
        for marker in (*LABELS, *LEAKS):
            self.assertNotIn(marker, c0)

    def test_c1_slot_is_the_label_inventory_without_provenance(self) -> None:
        slot = conditioning_for("C1")
        self.assertEqual(slot, "relation_labels:\n- Duty\n- Right\n- Privilege\n- NoRight\n")
        self.assertEqual(load_c1_labels(), ["Duty", "Right", "Privilege", "NoRight"])
        self.assertNotIn("estatuto", slot)
        self.assertNotIn("definition", slot.lower())

    def test_later_slots_reuse_the_existing_payloads(self) -> None:
        from re_te_benchmark.conditioning.c2 import canonical_dumps, model_payload
        from re_te_benchmark.conditioning.c3 import c3_model_payload, c3_nl_model_payload

        self.assertEqual(conditioning_for("C2"), canonical_dumps(model_payload()))
        self.assertEqual(conditioning_for("C3"), canonical_dumps(c3_model_payload()))
        self.assertEqual(conditioning_for("C3-NL"), canonical_dumps(c3_nl_model_payload()))
        self.assertIn("owl_functional", conditioning_for("C3"))
        self.assertIn("formal_natural", conditioning_for("C3-NL"))
        self.assertNotIn("owl_functional", conditioning_for("C2"))

    def test_readiness_and_output_fields_stay_unchanged(self) -> None:
        manifest = json.loads(
            (PROJECT_ROOT / "schemas" / "conditioning_conditions.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["conditions"]["C3"]["readiness"], "NOT_READY")
        package = json.loads(
            (PROJECT_ROOT / "schemas" / "c3" / "c3_ontology_v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(package["experimental_condition_status"], "NOT_EXECUTABLE")
        self.assertEqual(package["artifact_role"], "TBOX_ONLY")
        self.assertIn("Performance", package["artifact_role_note"])
        self.assertIn("no individual derived from a corpus", package["artifact_role_note"])


if __name__ == "__main__":
    unittest.main()
