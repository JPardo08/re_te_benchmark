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
    PREVIOUS_SHELL_ID,
    SHELL_ID,
    conditioning_for,
    previous_shell_template,
    render_condition,
    render_instruction,
    shell_template,
)


TEXT = "The company pays the worker."
TWO_OBJECTS = "Alpha supplies Beta and Alpha supplies Gamma."
REPEATED = "Alpha supplies Beta. Alpha supplies Beta."
OBJECT_LINE = (
    "If one stated relation has more than one object, write one separate line "
    "for each object. Repeat the subject and the relation on each of those lines."
)
RELATION_LINE = (
    "If the input text states more than one relation, write one line for each "
    "relation, in the order in which the text states them."
)
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
        self.assertEqual(SHELL_ID, "common-instruction-shell-v2")
        self.assertEqual(PREVIOUS_SHELL_ID, "common-instruction-shell-v1")
        self.assertNotEqual(SHELL_ID, PREVIOUS_SHELL_ID)
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
        self.assertEqual(manifest["conditions"]["C2"]["readiness"], "PARTIAL")

    def test_v2_adds_only_the_multi_object_sentence(self) -> None:
        current = shell_template()
        previous = previous_shell_template()
        self.assertNotIn(OBJECT_LINE, previous)
        self.assertEqual(current.count(OBJECT_LINE), 1)
        self.assertIn(RELATION_LINE + "\n" + OBJECT_LINE + "\n", current)
        self.assertEqual(
            current,
            previous.replace(RELATION_LINE + "\n", RELATION_LINE + "\n" + OBJECT_LINE + "\n", 1),
        )
        for marker in (*LABELS, *LEAKS, "articulo_"):
            self.assertNotIn(marker, current)
            self.assertNotIn(marker, OBJECT_LINE)

    def test_five_conditions_share_v2_for_two_objects_and_repeats(self) -> None:
        for text in (TWO_OBJECTS, REPEATED):
            bodies = []
            for condition in CONDITIONS:
                slot = conditioning_for(condition)
                rendered = render_condition(condition, text)
                self.assertIn(OBJECT_LINE, rendered)
                self.assertEqual(rendered.count(text), 1)
                self.assertNotIn(OBJECT_LINE, slot)
                self.assertNotIn(text, slot)
                if slot:
                    bodies.append(rendered.replace(slot, "[[SLOT]]", 1))
                else:
                    bodies.append(
                        rendered.replace("\n\nInput text:\n", "\n[[SLOT]]\nInput text:\n", 1)
                    )
            self.assertEqual(len(set(bodies)), 1)


if __name__ == "__main__":
    unittest.main()
