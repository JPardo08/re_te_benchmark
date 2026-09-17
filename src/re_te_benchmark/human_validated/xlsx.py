"""Stdlib XLSX reader for the historical human-validation Excels."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
MAIN_T = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"


def _col_to_idx(col: str) -> int:
    value = 0
    for char in col:
        value = value * 26 + (ord(char) - 64)
    return value - 1


def _normalize_target(target: str) -> str:
    while target.startswith("/"):
        target = target[1:]
    if not target.startswith("xl/"):
        target = "xl/" + target
    while "xl/xl/" in target:
        target = target.replace("xl/xl/", "xl/")
    return target


def _cell_text(cell: ET.Element, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value = cell.find("m:v", NS)
    inline = cell.find("m:is", NS)
    if value is None and inline is not None:
        return "".join(node.text or "" for node in inline.iter(MAIN_T))
    if value is None:
        return ""
    if cell_type == "s":
        return shared[int(value.text)]
    if cell_type == "inlineStr" and inline is not None:
        return "".join(node.text or "" for node in inline.iter(MAIN_T))
    return value.text or ""


def load_workbook(path: Path) -> dict[str, list[list[str]]]:
    """Return sheet_name -> raw rows including header."""
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", NS):
                shared.append("".join(node.text or "" for node in item.iter(MAIN_T)))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets: list[tuple[str, str]] = []
        for sheet in workbook.find("m:sheets", NS):
            sheets.append((sheet.attrib["name"], sheet.attrib[f"{REL_NS}id"]))

        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {
            rel.attrib["Id"]: _normalize_target(rel.attrib["Target"])
            for rel in relationships
        }

        out: dict[str, list[list[str]]] = {}
        for name, rid in sheets:
            root = ET.fromstring(archive.read(rid_to_target[rid]))
            rows: list[list[str]] = []
            for row in root.find("m:sheetData", NS):
                cells: dict[int, str] = {}
                max_col = -1
                for cell in row.findall("m:c", NS):
                    match = re.match(r"[A-Z]+", cell.attrib["r"])
                    if match is None:
                        continue
                    index = _col_to_idx(match.group(0))
                    max_col = max(max_col, index)
                    cells[index] = _cell_text(cell, shared)
                if max_col >= 0:
                    rows.append([cells.get(i, "") for i in range(max_col + 1)])
            out[name] = rows
        return out


def sheet_records(rows: list[list[str]]) -> list[dict[str, Any]]:
    """Convert sheet rows to dictionaries, trimming empty trailing headers."""
    if not rows:
        return []
    header = list(rows[0])
    while header and str(header[-1]).strip() == "":
        header.pop()
    width = len(header)
    records: list[dict[str, Any]] = []
    for row in rows[1:]:
        values = (row + [""] * width)[:width]
        if all(str(value).strip() == "" for value in values):
            continue
        records.append(dict(zip(header, values)))
    return records
