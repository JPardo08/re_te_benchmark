"""Lossless parser for the original inline-tagged Hohfeld annotations."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

INLINE_TAG_RE = re.compile(r"</?(e1|e2|rel|comp|mod)>")
VALUE_RE = {
    name: re.compile(rf"<{name}>(.*?)</{name}>", re.DOTALL)
    for name in ("e1", "e2", "rel", "comp", "mod")
}
SIGNATURE_RE = re.compile(r"RelationSignature:\s*(.*?)\s*\(e1,\s*e2\)")
TYPE_RE = re.compile(r"RelationType:\s*(.*?)\s*\(rel\)")
MISSING_E2_RE = re.compile(r"^MissingE2:\s*(.*?)\s*$", re.MULTILINE)


def article_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"(\d+)$", path.stem)
    return (int(match.group(1)) if match else 10**9, path.name)


def _clean_and_spans(annotated_text: str) -> tuple[str, dict[str, list[dict[str, Any]]]]:
    """Strip known tags while retaining character offsets in the clean text."""
    output: list[str] = []
    spans: dict[str, list[dict[str, Any]]] = {
        name: [] for name in ("e1", "e2", "rel", "comp", "mod")
    }
    stack: list[tuple[str, int]] = []
    source_pos = 0
    clean_pos = 0

    for match in INLINE_TAG_RE.finditer(annotated_text):
        chunk = annotated_text[source_pos : match.start()]
        output.append(chunk)
        clean_pos += len(chunk)
        tag = match.group(1)
        is_closing = match.group(0).startswith("</")
        if not is_closing:
            stack.append((tag, clean_pos))
        else:
            for index in range(len(stack) - 1, -1, -1):
                open_tag, start = stack[index]
                if open_tag == tag:
                    del stack[index]
                    text = "".join(output)[start:clean_pos]
                    spans[tag].append({"text": text, "span": [start, clean_pos]})
                    break
        source_pos = match.end()

    output.append(annotated_text[source_pos:])
    clean = "".join(output)
    return clean, spans


def parse_block(block: str, source_file: str, article_id: str) -> dict[str, Any] | None:
    """Parse one typed source block without requiring either argument."""
    type_match = TYPE_RE.search(block)
    if not type_match:
        return None

    lines = block.strip().splitlines()
    first_line = lines[0] if lines else ""
    if "\t" in first_line:
        block_id, annotated_text = first_line.split("\t", 1)
        block_id = block_id.strip()
    else:
        block_id = "unknown"
        annotated_text = first_line

    clean_text, spans = _clean_and_spans(annotated_text)
    signature_match = SIGNATURE_RE.search(block)
    signature = signature_match.group(1).strip() if signature_match else None
    signature_types = signature.split("-", 1) if signature and "-" in signature else [None, None]
    e1_type = signature_types[0].strip() if signature_types[0] else None
    e2_type = signature_types[1].strip() if signature_types[1] else None
    missing_match = MISSING_E2_RE.search(block)

    for value in spans["e1"]:
        value["type"] = e1_type
        value["source"] = "inline_e1"
        value["inline_span"] = value.pop("span")
    for value in spans["e2"]:
        value["type"] = e2_type
        value["source"] = "inline_e2"
        value["inline_span"] = value.pop("span")

    annotation_id = f"{article_id}#{block_id}"
    return {
        "annotation_id": annotation_id,
        "article_id": article_id,
        "source_file": source_file,
        "block_id": block_id,
        "raw_block": block,
        "annotated_text": annotated_text,
        "clean_text": clean_text,
        "relation_type": type_match.group(1).strip(),
        "relation_signature": signature,
        "e1": spans["e1"][0] if spans["e1"] else None,
        "e2": spans["e2"],
        "missing_e2": (
            {
                "text": missing_match.group(1).strip(),
                "type": e2_type,
                "span": None,
                "source": "MissingE2",
            }
            if missing_match
            else None
        ),
        "relation_text": spans["rel"][0] if spans["rel"] else None,
        "complements": spans["comp"],
        "modifier": spans["mod"][0] if spans["mod"] else None,
    }


def parse_source(relations_dir: Path, source_root: Path) -> list[dict[str, Any]]:
    """Parse all RelationType blocks in stable article/block order."""
    annotations: list[dict[str, Any]] = []
    for path in sorted(relations_dir.glob("articulo_*.txt"), key=article_sort_key):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(source_root).as_posix()
        blocks = re.split(r"\n\s*\n", text.strip()) if text.strip() else []
        for block in blocks:
            parsed = parse_block(block, relative, path.stem)
            if parsed is not None:
                annotations.append(parsed)
    return annotations
