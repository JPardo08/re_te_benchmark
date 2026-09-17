"""Capability-specific eligibility decisions for Hohfeld annotations."""

from __future__ import annotations

from typing import Any


def decision(eligible: bool, reason: str) -> dict[str, Any]:
    return {"eligible": eligible, "reason": reason}


def classify(annotation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    has_e1 = bool(annotation["e1"])
    has_e2 = bool(annotation["e2"])
    has_missing_e2 = annotation["missing_e2"] is not None
    has_any_argument = has_e1 or has_e2 or has_missing_e2
    has_text = bool(annotation["clean_text"].strip())
    has_signature = bool(annotation["relation_signature"])
    strict = has_e1 and has_e2
    complete = has_e1 and (has_e2 or has_missing_e2)

    if strict:
        complete_reason = "inline_e1_and_inline_e2"
    elif complete:
        complete_reason = "second_argument_from_missing_e2"
    elif not has_e1:
        complete_reason = "missing_e1"
    else:
        complete_reason = "missing_second_argument"

    return {
        "relation_type": decision(bool(annotation["relation_type"]), "relation_type_present"),
        "complete_triplet_strict_inline": decision(
            strict, "inline_e1_and_inline_e2" if strict else "requires_inline_e1_and_inline_e2"
        ),
        "complete_triplet_with_missing_e2": decision(complete, complete_reason),
        "argument_level": decision(has_any_argument, "at_least_one_argument_present"),
        "span_level_original": decision(
            strict,
            "both_inline_argument_spans_present" if strict else "requires_both_inline_argument_spans",
        ),
        "textual_supportedness": decision(has_text, "nonempty_annotated_evidence"),
        "schema_type": decision(
            has_signature,
            "relation_signature_present" if has_signature else "relation_signature_missing",
        ),
        "document_level_te": decision(complete, complete_reason),
        "sentence_projection": decision(False, "not_mapped"),
        "sentence_span": decision(False, "not_mapped"),
    }


def argument_pattern(annotation: dict[str, Any]) -> str:
    has_e1 = bool(annotation["e1"])
    has_e2 = bool(annotation["e2"])
    has_comp = bool(annotation["complements"])
    has_missing = annotation["missing_e2"] is not None
    has_mod = annotation["modifier"] is not None
    if has_e1 and has_e2 and has_comp and has_mod:
        return "e1+e2+comp+mod"
    if has_e1 and has_e2 and has_comp:
        return "e1+e2+comp"
    if has_e1 and has_e2:
        return "e1+e2"
    if has_e1 and has_comp and has_missing:
        return "e1+comp+MissingE2"
    if has_e1 and has_comp:
        return "e1+comp_without_MissingE2"
    if has_e2 and has_comp and not has_e1:
        return "e2+comp_without_e1"
    return "other"
