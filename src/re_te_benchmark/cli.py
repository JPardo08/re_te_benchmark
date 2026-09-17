"""Command-line entry points for building and auditing the benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .hohfeld.builder import build as build_hohfeld
from .hohfeld.builder import default_source_roots as hohfeld_defaults
from .hohfeld.manifests import sha256_file
from .human_validated.builder import build as build_human_validated
from .human_validated.parser import default_source_roots as silver_defaults


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_main() -> int:
    repo_root = _repo_root()
    default_estatuto, default_corpus = hohfeld_defaults(repo_root)
    parser = argparse.ArgumentParser(description="Build the Hohfeld P0 benchmark")
    parser.add_argument("--estatuto-root", type=Path, default=default_estatuto)
    parser.add_argument("--corpus-juri-root", type=Path, default=default_corpus)
    args = parser.parse_args()
    result = build_hohfeld(
        repo_root, args.estatuto_root.resolve(), args.corpus_juri_root.resolve()
    )
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
    errors = [
        f"{key}: expected {value}, got {actual[key]}"
        for key, value in expected.items()
        if actual[key] != value
    ]
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


def build_silver_main() -> int:
    repo_root = _repo_root()
    default_mrebel, default_corpus = silver_defaults(repo_root)
    parser = argparse.ArgumentParser(
        description="Build the mREBEL human-validated P0 asset"
    )
    parser.add_argument("--teresia-mrebel-root", type=Path, default=default_mrebel)
    parser.add_argument("--corpus-juri-root", type=Path, default=default_corpus)
    args = parser.parse_args()
    result = build_human_validated(
        repo_root,
        args.teresia_mrebel_root.resolve(),
        args.corpus_juri_root.resolve(),
    )
    total = result["statistics"]["total"]
    print(
        f"Built {total['judged']} judged candidates "
        f"({total['accepted']} accepted / {total['rejected']} rejected)"
    )
    print(f"Manifest: {result['manifest_path'].relative_to(repo_root)}")
    return 0


def audit_silver_main() -> int:
    repo_root = _repo_root()
    manifest_path = (
        repo_root
        / "datasets"
        / "teresia_mrebel_human_validated"
        / "manifests"
        / "manifest.json"
    )
    if not manifest_path.exists():
        print("ERROR: silver asset has not been built")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stats = manifest["counts"]
    regression = stats["published_regression"]
    errors: list[str] = []

    expected = {
        ("laboral", "judged"): 1153,
        ("laboral", "accepted"): 303,
        ("laboral", "rejected"): 850,
        ("laboral", "disputed_before_consensus"): 300,
        ("laboral", "unresolved"): 0,
        ("tributario", "judged"): 1036,
        ("tributario", "accepted"): 162,
        ("tributario", "rejected"): 874,
        ("tributario", "disputed_before_consensus"): 169,
        ("tributario", "unresolved"): 0,
        ("total", "judged"): 2189,
        ("total", "accepted"): 465,
        ("total", "rejected"): 1724,
        ("total", "disputed_before_consensus"): 469,
        ("total", "unresolved"): 0,
        ("total", "dual_annotator_coverage"): 2189,
    }
    for (block, key), value in expected.items():
        actual = stats[block][key]
        if actual != value:
            errors.append(f"{block}.{key}: expected {value}, got {actual}")
    if stats["total"]["accepted"] + stats["total"]["rejected"] != stats["total"]["judged"]:
        errors.append("accepted + rejected != judged")
    if not regression["exact"]:
        errors.append("published silver regression mismatch")
    for artifact in manifest["artifacts"]:
        path = repo_root / artifact["relative_path"]
        if not path.exists() or sha256_file(path) != artifact["sha256"]:
            errors.append(f"artifact hash mismatch: {artifact['relative_path']}")

    lab_iaa = stats["iaa"]["laboral"]["AUDIT_RECOMPUTATION"]
    tri_iaa = stats["iaa"]["tributario"]["AUDIT_RECOMPUTATION"]

    print("RESOURCE")
    print("type: model_dependent_human_validated")
    print()
    print("LABORAL")
    print(f"judged: {stats['laboral']['judged']}")
    print(f"accepted: {stats['laboral']['accepted']}")
    print(f"rejected: {stats['laboral']['rejected']}")
    print(f"disputed: {stats['laboral']['disputed_before_consensus']}")
    print(f"agreement: {lab_iaa['observed_agreement']}")
    print(f"kappa: {lab_iaa['cohen_kappa']}")
    print()
    print("TRIBUTARIO")
    print(f"judged: {stats['tributario']['judged']}")
    print(f"accepted: {stats['tributario']['accepted']}")
    print(f"rejected: {stats['tributario']['rejected']}")
    print(f"disputed: {stats['tributario']['disputed_before_consensus']}")
    print(f"agreement: {tri_iaa['observed_agreement']}")
    print(f"kappa: {tri_iaa['cohen_kappa']}")
    print()
    print("PUBLISHED REGRESSION")
    print(
        "laboral: "
        f"{regression['laboral']['exact_soft_key_matches']}/"
        f"{regression['laboral']['published']}"
    )
    print(
        "tributario: "
        f"{regression['tributario']['exact_soft_key_matches']}/"
        f"{regression['tributario']['published']}"
    )
    print()
    print("CIRCULARITY")
    print("generator independent: NO")
    print("generator recall evaluation valid: NO")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("SILVER_ASSET_P0_READY = YES")
    return 0
