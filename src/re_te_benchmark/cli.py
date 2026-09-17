"""Command-line entry points for building and auditing the benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .hohfeld.builder import build, default_source_roots
from .hohfeld.manifests import sha256_file


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_main() -> int:
    repo_root = _repo_root()
    default_estatuto, default_corpus = default_source_roots(repo_root)
    parser = argparse.ArgumentParser(description="Build the Hohfeld P0 benchmark")
    parser.add_argument("--estatuto-root", type=Path, default=default_estatuto)
    parser.add_argument("--corpus-juri-root", type=Path, default=default_corpus)
    args = parser.parse_args()
    result = build(repo_root, args.estatuto_root.resolve(), args.corpus_juri_root.resolve())
    stats = result["statistics"]
    print(f"Built {stats['annotations']} annotations in {stats['documents']} documents")
    print(f"Manifest: {result['manifest_path'].relative_to(repo_root)}")
    return 0


def audit_main() -> int:
    repo_root = _repo_root()
    manifest_path = (
        repo_root / "datasets" / "teresia_hohfeld" / "manifests" / "manifest.json"
    )
    if not manifest_path.exists():
        print("ERROR: benchmark has not been built")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stats = manifest["counts"]
    regression_path = (
        repo_root
        / "datasets"
        / "teresia_hohfeld"
        / "manifests"
        / "historical_regression.json"
    )
    regression = json.loads(regression_path.read_text(encoding="utf-8"))
    schema_path = repo_root / manifest["schema"]["relative_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    expected = {
        "annotations": 95,
        "complete_te": 85,
        "partial_te": 10,
        "sentence_aligned": 65,
        "span_complete": 41,
        "labels": 4,
    }
    actual = {
        "annotations": stats["annotations"],
        "complete_te": stats["document_level"]["complete_te"],
        "partial_te": stats["document_level"]["partial_te"],
        "sentence_aligned": stats["projections"]["sentence_aligned"],
        "span_complete": stats["projections"]["span_complete"],
        "labels": len(schema["labels"]),
    }
    errors = [f"{key}: expected {value}, got {actual[key]}" for key, value in expected.items() if actual[key] != value]
    if not regression["exact"]:
        errors.append(f"historical regression mismatches: {regression['mismatch_count']}")
    if sha256_file(schema_path) != manifest["schema"]["sha256"]:
        errors.append("C1 schema hash mismatch")
    for artifact in manifest["artifacts"]:
        path = repo_root / artifact["relative_path"]
        if not path.exists() or sha256_file(path) != artifact["sha256"]:
            errors.append(f"artifact hash mismatch: {artifact['relative_path']}")

    print("SOURCE")
    print(f"RelationType annotations: {actual['annotations']}")
    print()
    print("CANONICAL")
    print(f"Complete TE: {actual['complete_te']}")
    print(f"Partial: {actual['partial_te']}")
    print()
    print("PROJECTIONS")
    print(f"Sentence aligned: {actual['sentence_aligned']}")
    print(f"Span complete: {actual['span_complete']}")
    print()
    print("C1")
    print(f"Labels: {actual['labels']}")
    print()
    print(f"HISTORICAL REGRESSION: {'EXACT' if regression['exact'] else 'MISMATCH'}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("BENCHMARK_P0_READY = YES")
    return 0
