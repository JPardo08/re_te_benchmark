"""Deterministic IAA recomputation for dual Sí/No judgments."""

from __future__ import annotations

from collections import Counter
from typing import Any


def cohen_kappa(labels_a: list[bool], labels_b: list[bool]) -> float | None:
    if not labels_a or len(labels_a) != len(labels_b):
        return None
    n = len(labels_a)
    observed = sum(1 for left, right in zip(labels_a, labels_b) if left == right) / n
    p_a = sum(1 for value in labels_a if value) / n
    p_b = sum(1 for value in labels_b if value) / n
    expected = p_a * p_b + (1 - p_a) * (1 - p_b)
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


def compute_iaa(candidates: list[dict[str, Any]], subdomain: str) -> dict[str, Any]:
    subset = [item for item in candidates if item["subdomain"] == subdomain]
    labeled = [
        item
        for item in subset
        if item["judgments"]["annotator_A"]["valid"] is not None
        and item["judgments"]["annotator_B"]["valid"] is not None
    ]
    labels_a = [bool(item["judgments"]["annotator_A"]["valid"]) for item in labeled]
    labels_b = [bool(item["judgments"]["annotator_B"]["valid"]) for item in labeled]
    matrix = Counter(
        (
            "Si" if item["judgments"]["annotator_A"]["valid"] else "No",
            "Si" if item["judgments"]["annotator_B"]["valid"] else "No",
        )
        for item in labeled
    )
    observed = (
        sum(1 for left, right in zip(labels_a, labels_b) if left == right) / len(labeled)
        if labeled
        else None
    )
    return {
        "source": "AUDIT_RECOMPUTATION",
        "subdomain": subdomain,
        "n_overlap": len(labeled),
        "observed_agreement": observed,
        "cohen_kappa": cohen_kappa(labels_a, labels_b),
        "matrix_2x2": {
            "A_Si_B_Si": matrix[("Si", "Si")],
            "A_Si_B_No": matrix[("Si", "No")],
            "A_No_B_Si": matrix[("No", "Si")],
            "A_No_B_No": matrix[("No", "No")],
        },
        "annotator_ids": ["annotator_A", "annotator_B"],
    }
