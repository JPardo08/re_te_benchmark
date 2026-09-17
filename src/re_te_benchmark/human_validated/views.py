"""Derived views and published-Silver regression helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .parser import soft_key


def view_records(
    candidates: list[dict[str, Any]],
    *,
    status: str | None = None,
    disputed_only: bool = False,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in candidates:
        if status is not None and item["status"] != status:
            continue
        if disputed_only and not item["flags"]["disputed_before_consensus"]:
            continue
        records.append(
            {
                "candidate_id": item["candidate_id"],
                "subdomain": item["subdomain"],
                "status": item["status"],
                "disputed_before_consensus": item["flags"]["disputed_before_consensus"],
                "consensus_valid": item["consensus"]["valid"],
                "soft_key": item["provenance"]["soft_key"],
                "context": item["context"],
                "prediction": item["prediction"],
                "semantics": item["semantics"],
            }
        )
    return records


def load_published_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def published_regression(
    accepted: list[dict[str, Any]],
    published_rows: list[dict[str, str]],
    subdomain: str,
) -> dict[str, Any]:
    accepted_keys = {
        soft_key(
            {
                "doc": item["soft_key"]["doc"],
                "sent_id": item["soft_key"]["sent_id"],
                "subject": item["soft_key"]["subject"],
                "relation": item["soft_key"]["relation"],
                "object": item["soft_key"]["object"],
            }
        )
        for item in accepted
        if item["subdomain"] == subdomain
    }
    published_keys = {soft_key(row) for row in published_rows}
    exact = len(accepted_keys & published_keys)
    return {
        "subdomain": subdomain,
        "accepted": len(accepted_keys),
        "published": len(published_keys),
        "exact_soft_key_matches": exact,
        "accepted_not_in_published": sorted(
            [
                {
                    "doc": key[0],
                    "sent_id": key[1],
                    "subject": key[2],
                    "relation": key[3],
                    "object": key[4],
                }
                for key in sorted(accepted_keys - published_keys)
            ],
            key=lambda item: (
                item["doc"],
                item["sent_id"],
                item["subject"],
                item["relation"],
                item["object"],
            ),
        ),
        "published_not_in_accepted": sorted(
            [
                {
                    "doc": key[0],
                    "sent_id": key[1],
                    "subject": key[2],
                    "relation": key[3],
                    "object": key[4],
                }
                for key in sorted(published_keys - accepted_keys)
            ],
            key=lambda item: (
                item["doc"],
                item["sent_id"],
                item["subject"],
                item["relation"],
                item["object"],
            ),
        ),
        "exact": exact == len(accepted_keys) == len(published_keys),
    }
