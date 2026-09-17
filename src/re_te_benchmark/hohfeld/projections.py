"""Deterministic historical sentence and span projections."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PROJECTION_FIELDS = (
    "subject",
    "subject_type",
    "relation",
    "object",
    "object_type",
    "relation_text",
    "complement",
    "relation_signature",
)


def _second_type(annotation: dict[str, Any]) -> str | None:
    signature = annotation.get("relation_signature")
    if signature and "-" in signature:
        return signature.split("-", 1)[1]
    return None


def _span(text: str, value: str) -> list[int] | None:
    if not value:
        return None
    start = text.find(value)
    return [start, start + len(value)] if start >= 0 else None


def load_oracle(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Historical projection must be a JSON list: {path}")
    return data


def load_projection_documents(
    brat_dir: Path, source_root: Path
) -> dict[str, dict[str, str]]:
    return {
        path.name: {
            "text": path.read_text(encoding="utf-8"),
            "relative_path": path.relative_to(source_root).as_posix(),
        }
        for path in sorted(brat_dir.glob("ejemplo_3_*.txt"), key=lambda item: item.name)
    }


def _find_sentence(sentence_clean: str, document_text: str) -> tuple[int, str] | None:
    norm_sent = " ".join(sentence_clean.split())
    norm_doc = " ".join(document_text.split())
    if norm_sent[:50] not in norm_doc:
        return None
    sentences = re.split(
        r"(?<=\.)\s+(?=[A-ZÁÉÍÓÚÑ0-9])", document_text.strip()
    )
    for index, sentence in enumerate(sentences, start=1):
        norm_candidate = " ".join(sentence.split())
        if norm_sent in norm_candidate or norm_candidate in norm_sent:
            return index, sentence.strip()
    key = norm_sent[:50]
    for index, sentence in enumerate(sentences, start=1):
        if key in " ".join(sentence.split()):
            return index, sentence.strip()
    return None


def _historical_annotation_key(annotation: dict[str, Any]) -> tuple[str, int]:
    try:
        block = int(annotation["block_id"])
    except ValueError:
        block = 10**9
    return annotation["source_file"], block


def build_sentence_projection(
    annotations: list[dict[str, Any]], documents: dict[str, dict[str, str]]
) -> tuple[list[dict[str, Any]], list[str]]:
    """Reproduce the notebook's sorted global sentence-search fallback."""
    projected: list[dict[str, Any]] = []
    mapped_ids: list[str] = []
    for annotation in sorted(annotations, key=_historical_annotation_key):
        if not annotation["e1"] or not annotation["relation_text"]:
            continue
        match: tuple[str, str, int, str] | None = None
        for document_name in sorted(documents):
            result = _find_sentence(
                annotation["clean_text"], documents[document_name]["text"]
            )
            if result is not None:
                sent_id, sent_text = result
                match = (
                    document_name,
                    documents[document_name]["relative_path"],
                    sent_id,
                    sent_text,
                )
                break
        if match is None:
            continue

        document_name, document_path, sent_id, sent_text = match
        annotation_id = annotation["annotation_id"]
        mapped_ids.append(annotation_id)
        row_index = len(projected) + 1
        subject = annotation["e1"]["text"]
        historical_object = annotation["e2"][0]["text"] if annotation["e2"] else ""
        subject_span = _span(sent_text, subject)
        object_span = _span(sent_text, historical_object)
        projection_id = f"sentence_projection_{row_index:03d}"
        projected.append(
            {
                "projection_id": projection_id,
                "original_annotation_id": annotation_id,
                "doc": document_name,
                "sent_id": sent_id,
                "sent_text": sent_text,
                "subject": subject,
                "subject_type": annotation["e1"]["type"],
                "relation": annotation["relation_type"],
                "object": historical_object,
                "object_type": _second_type(annotation),
                "subj_start": subject_span[0] if subject_span else None,
                "subj_end": subject_span[1] if subject_span else None,
                "obj_start": object_span[0] if object_span else None,
                "obj_end": object_span[1] if object_span else None,
                "relation_text": annotation["relation_text"]["text"],
                "complements": [item["text"] for item in annotation["complements"]],
                "relation_signature": annotation["relation_signature"],
                "canonical_arguments": {
                    "e1": annotation["e1"],
                    "e2": annotation["e2"],
                    "missing_e2": annotation["missing_e2"],
                },
                "provenance": {
                    "transformation": "historical_notebook_sorted_global_fallback",
                    "projection_source_file": document_path,
                },
            }
        )
    return projected, mapped_ids


def build_span_complete(sentence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required = ("subj_start", "subj_end", "obj_start", "obj_end")
    return [
        {**row, "span_projection_id": f"span_projection_{index:03d}"}
        for index, row in enumerate(
            (row for row in sentence_rows if all(row[field] is not None for field in required)),
            start=1,
        )
    ]


def historical_regression(
    rebuilt: list[dict[str, Any]], oracle: list[dict[str, Any]]
) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    fields = (
        "doc",
        "sent_id",
        "sent_text",
        *PROJECTION_FIELDS,
        "subj_start",
        "subj_end",
        "obj_start",
        "obj_end",
    )
    for index, (actual, expected) in enumerate(zip(rebuilt, oracle), start=1):
        for field in fields:
            expected_value = expected.get(field)
            if field == "complement":
                actual_value = " | ".join(actual["complements"])
            else:
                actual_value = actual.get(field)
            if actual_value != expected_value:
                mismatches.append(
                    {
                        "row": index,
                        "field": field,
                        "expected": expected_value,
                        "actual": actual_value,
                    }
                )
    return {
        "oracle_records": len(oracle),
        "rebuilt_records": len(rebuilt),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "exact": len(rebuilt) == len(oracle) and not mismatches,
    }
