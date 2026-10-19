"""Common instruction shell for C0, C1, C2, C3, and C3-NL.

The instruction text is identical for every condition. The only condition
variable is the target-schema conditioning slot. This module does not call a
model and it does not select a backbone.
"""

from __future__ import annotations

from re_te_benchmark.conditioning.c2 import canonical_dumps, load_c1_labels, model_payload
from re_te_benchmark.conditioning.c3 import c3_model_payload, c3_nl_model_payload


SHELL_ID = "common-instruction-shell-v2"
PREVIOUS_SHELL_ID = "common-instruction-shell-v1"
CONDITIONS = ("C0", "C1", "C2", "C3", "C3-NL")
_CONDITIONING_MARK = "[[CONDITIONING]]"
_TEXT_MARK = "[[TEXT]]"
_RELATION_LINE = (
    "If the input text states more than one relation, write one line for each "
    "relation, in the order in which the text states them.\n"
)
_OBJECT_LINE = (
    "If one stated relation has more than one object, write one separate line "
    "for each object. Repeat the subject and the relation on each of those lines.\n"
)
_TEMPLATE_V1 = """\
Task: extract each directed relation that the input text states.

Write one relation per line. Each line contains exactly three fields separated by one tab, in this order: subject, relation, object.
Copy the subject and the object as contiguous spans of the input text. Do not add words that the input text does not contain.
Do not invent a subject or an object that the text does not state. If either one is absent, do not write a line for that relation.
If the input text states no relation, write no lines.
If the input text states more than one relation, write one line for each relation, in the order in which the text states them.
A line without exactly three non-empty tab-separated fields is malformed. Do not repair it and do not reinterpret it.
When the target-schema conditioning contains relation labels, use one of those labels in the relation field.
When the target-schema conditioning contains no relation labels, write a short relation name that the input text supports.
Do not drop, rewrite, or filter any line because of which conditioning block was used.
The conditioning block is not an example. Do not copy it as a relation.

Target-schema conditioning:
[[CONDITIONING]]
Input text:
[[TEXT]]
Relations:
"""
if _TEMPLATE_V1.count(_RELATION_LINE) != 1:
    raise RuntimeError("The v1 shell lost its relation-line anchor.")
_TEMPLATE = _TEMPLATE_V1.replace(_RELATION_LINE, _RELATION_LINE + _OBJECT_LINE, 1)


def shell_template() -> str:
    """Return the current instruction text, including the two slot marks."""
    return _TEMPLATE


def previous_shell_template() -> str:
    """Return the v1 instruction text. It is not the rendered shell."""
    return _TEMPLATE_V1


def render_instruction(conditioning: str, text: str) -> str:
    """Insert the conditioning slot and the input text into the fixed shell."""
    if not isinstance(conditioning, str):
        raise TypeError("conditioning must be a string.")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("input text must be a non-empty string.")
    if _CONDITIONING_MARK not in _TEMPLATE or _TEXT_MARK not in _TEMPLATE:
        raise RuntimeError("The instruction shell lost a slot mark.")
    rendered = _TEMPLATE.replace(_CONDITIONING_MARK, conditioning, 1)
    rendered = rendered.replace(_TEXT_MARK, text, 1)
    if _CONDITIONING_MARK in rendered or _TEXT_MARK in rendered:
        raise ValueError("Conditioning or input text contains a reserved slot mark.")
    return rendered


def conditioning_for(condition: str) -> str:
    """Return the only text that differs across the five experimental arms."""
    if condition == "C0":
        return ""
    if condition == "C1":
        lines = ["relation_labels:"]
        lines.extend(f"- {label}" for label in load_c1_labels())
        return "\n".join(lines) + "\n"
    if condition == "C2":
        return canonical_dumps(model_payload())
    if condition == "C3":
        return canonical_dumps(c3_model_payload())
    if condition == "C3-NL":
        return canonical_dumps(c3_nl_model_payload())
    raise ValueError(f"Unknown condition {condition!r}.")


def render_condition(condition: str, text: str) -> str:
    """Render one condition without changing the surrounding instruction."""
    return render_instruction(conditioning_for(condition), text)
