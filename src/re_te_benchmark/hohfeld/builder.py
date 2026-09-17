"""Build the reproducible Hohfeld P0 benchmark."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .eligibility import argument_pattern, classify
from .manifests import (
    repository_metadata,
    sha256_file,
    source_file_entries,
    write_json,
    write_jsonl,
)
from .parser import article_sort_key, parse_source
from .projections import (
    build_sentence_projection,
    build_span_complete,
    historical_regression,
    load_oracle,
    load_projection_documents,
)

BENCHMARK_ID = "teresia_hohfeld"
BENCHMARK_VERSION = "0.1.0"
C1_ID = "hohfeld_labels"
C1_VERSION = "1.0.0"


def default_source_roots(repo_root: Path) -> tuple[Path, Path]:
    legacy = repo_root.parent / "_legacy"
    return legacy / "estatuto_goldstandard", legacy / "teresia-mrebel-corpus-juri"


def _duplicate_tags(annotations: list[dict[str, Any]]) -> dict[str, list[str]]:
    exact: dict[str, list[str]] = defaultdict(list)
    evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for annotation in annotations:
        payload = {
            key: annotation[key]
            for key in (
                "annotated_text",
                "relation_type",
                "relation_signature",
                "e1",
                "e2",
                "missing_e2",
                "relation_text",
                "complements",
                "modifier",
            )
        }
        exact[json.dumps(payload, ensure_ascii=False, sort_keys=True)].append(
            annotation["annotation_id"]
        )
        evidence[" ".join(annotation["clean_text"].split())].append(annotation)

    tags: dict[str, list[str]] = defaultdict(list)
    for ids in exact.values():
        if len(ids) > 1:
            for annotation_id in ids:
                tags[annotation_id].append("source_duplicate")
    for group in evidence.values():
        signatures = {item["relation_signature"] for item in group}
        e2_counts = {len(item["e2"]) for item in group}
        if len(group) > 1 and (len(signatures) > 1 or len(e2_counts) > 1):
            for item in group:
                tags[item["annotation_id"]].append("alternative_annotation")
    return tags


def _canonical_annotation(
    source: dict[str, Any], source_meta: dict[str, str], tags: list[str]
) -> dict[str, Any]:
    eligibility = source["eligibility"]
    te_view = None
    if eligibility["complete_triplet_with_missing_e2"]["eligible"]:
        objects = source["e2"] or [source["missing_e2"]]
        te_view = {
            "subject": source["e1"]["text"],
            "relation": source["relation_type"],
            "objects": [item["text"] for item in objects],
            "subject_source": "inline_e1",
            "object_sources": [item["source"] for item in objects],
        }
    return {
        "annotation_id": source["annotation_id"],
        "relation": source["relation_type"],
        "signature": source["relation_signature"],
        "arguments": {
            "e1": source["e1"],
            "e2": source["e2"],
            "missing_e2": source["missing_e2"],
        },
        "relation_text": source["relation_text"],
        "complements": source["complements"],
        "modifier": source["modifier"],
        "evidence_text": source["clean_text"],
        "annotated_text": source["annotated_text"],
        "raw_block": source["raw_block"],
        "te_view": te_view,
        "eligibility": eligibility,
        "metadata": {
            "argument_pattern": argument_pattern(source),
            "tags": sorted(tags),
            "e2_multiplicity": len(source["e2"]),
        },
        "provenance": {
            "repository": source_meta["repository"],
            "repository_url": source_meta["url"],
            "commit": source_meta["commit"],
            "relative_file": source["source_file"],
            "block_id": source["block_id"],
            "original_annotation_id": source["annotation_id"],
        },
    }


def _mark_projection_eligibility(
    annotations: list[dict[str, Any]], sentence_rows: list[dict[str, Any]]
) -> None:
    by_id = {annotation["annotation_id"]: annotation for annotation in annotations}
    for row in sentence_rows:
        annotation = by_id[row["original_annotation_id"]]
        annotation["eligibility"]["sentence_projection"] = {
            "eligible": True,
            "reason": "mapped_under_historical_notebook_policy",
        }
        complete = all(
            row[field] is not None
            for field in ("subj_start", "subj_end", "obj_start", "obj_end")
        )
        annotation["eligibility"]["sentence_span"] = {
            "eligible": complete,
            "reason": (
                "complete_projected_argument_spans"
                if complete
                else "projected_argument_span_incomplete"
            ),
        }


def _tag_projection_collisions(rows: list[dict[str, Any]]) -> None:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (row["doc"], row["sent_id"], row["subject"], row["relation"], row["object"])
        groups[key].append(row)
    for group in groups.values():
        if len(group) > 1:
            ids = [item["projection_id"] for item in group]
            for row in group:
                row["metadata"] = {
                    "tags": ["projection_collision"],
                    "collision_projection_ids": ids,
                }


def _statistics(
    annotations: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    sentence_rows: list[dict[str, Any]],
    span_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    eligibility_names = list(annotations[0]["eligibility"])
    eligibility_counts = {
        name: sum(item["eligibility"][name]["eligible"] for item in annotations)
        for name in eligibility_names
    }
    return {
        "benchmark_id": BENCHMARK_ID,
        "benchmark_version": BENCHMARK_VERSION,
        "documents": len(documents),
        "annotations": len(annotations),
        "relation_distribution": dict(
            sorted(Counter(item["relation_type"] for item in annotations).items())
        ),
        "argument_patterns": dict(
            sorted(Counter(argument_pattern(item) for item in annotations).items())
        ),
        "eligibility_counts": eligibility_counts,
        "document_level": {
            "complete_te": eligibility_counts["document_level_te"],
            "partial_te": len(annotations) - eligibility_counts["document_level_te"],
        },
        "projections": {
            "sentence_aligned": len(sentence_rows),
            "span_complete": len(span_rows),
            "unmatched_parseable_original": (
                sum(bool(item["e1"]) for item in annotations) - len(sentence_rows)
            ),
            "historically_parser_excluded": sum(not bool(item["e1"]) for item in annotations),
        },
    }


def build(
    repo_root: Path,
    estatuto_root: Path,
    corpus_juri_root: Path,
) -> dict[str, Any]:
    relations_dir = estatuto_root / "data" / "old" / "rels"
    articles_dir = estatuto_root / "data" / "old" / "old_articles"
    oracle_path = corpus_juri_root / "gold_standard" / "laboral" / "hohfeld_laboral.json"
    notebook_path = corpus_juri_root / "code" / "build_corpus.ipynb"
    projection_text_dir = corpus_juri_root / "corpus" / "laboral" / "brat"
    schema_path = repo_root / "schemas" / "c1" / "hohfeld_labels.json"

    for required in (
        relations_dir,
        articles_dir,
        oracle_path,
        notebook_path,
        projection_text_dir,
        schema_path,
    ):
        if not required.exists():
            raise FileNotFoundError(required)

    estatuto_meta = repository_metadata(estatuto_root)
    corpus_meta = repository_metadata(corpus_juri_root)
    annotations = parse_source(relations_dir, estatuto_root)
    for annotation in annotations:
        annotation["eligibility"] = classify(annotation)

    oracle = load_oracle(oracle_path)
    projection_documents = load_projection_documents(projection_text_dir, corpus_juri_root)
    sentence_rows, _ = build_sentence_projection(annotations, projection_documents)
    for row_index, row in enumerate(sentence_rows, start=1):
        row["provenance"]["historical_row_id"] = row_index
        row["provenance"][
            "historical_artifact"
        ] = "gold_standard/laboral/hohfeld_laboral.json"
    _tag_projection_collisions(sentence_rows)
    span_rows = build_span_complete(sentence_rows)
    regression = historical_regression(sentence_rows, oracle)
    _mark_projection_eligibility(annotations, sentence_rows)

    tags = _duplicate_tags(annotations)
    canonical_annotations = [
        _canonical_annotation(item, estatuto_meta, tags[item["annotation_id"]])
        for item in annotations
    ]
    annotations_by_article: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for annotation in canonical_annotations:
        annotations_by_article[annotation["annotation_id"].split("#", 1)[0]].append(annotation)

    documents: list[dict[str, Any]] = []
    for article_id in sorted(
        annotations_by_article,
        key=lambda value: article_sort_key(Path(f"{value}.txt")),
    ):
        article_path = articles_dir / f"{article_id}.txt"
        documents.append(
            {
                "document_id": article_id,
                "source_text": article_path.read_text(encoding="utf-8") if article_path.exists() else None,
                "annotations": annotations_by_article[article_id],
                "provenance": {
                    "repository": estatuto_meta["repository"],
                    "commit": estatuto_meta["commit"],
                    "relative_file": (
                        article_path.relative_to(estatuto_root).as_posix()
                        if article_path.exists()
                        else None
                    ),
                },
            }
        )

    dataset_root = repo_root / "datasets" / "teresia_hohfeld"
    artifact_specs = [
        (
            dataset_root / "canonical" / "documents.jsonl",
            documents,
            "canonical_documents",
        ),
        (
            dataset_root / "canonical" / "annotations.jsonl",
            canonical_annotations,
            "canonical_annotations",
        ),
        (
            dataset_root / "views" / "sentence_aligned" / "annotations.jsonl",
            sentence_rows,
            "sentence_aligned",
        ),
        (
            dataset_root / "views" / "span_complete" / "annotations.jsonl",
            span_rows,
            "span_complete",
        ),
    ]
    artifact_records: list[dict[str, Any]] = []
    for path, records, role in artifact_specs:
        count = write_jsonl(path, records)
        artifact_records.append(
            {
                "role": role,
                "relative_path": path.relative_to(repo_root).as_posix(),
                "sha256": sha256_file(path),
                "records": count,
            }
        )

    stats = _statistics(annotations, documents, sentence_rows, span_rows)
    stats_path = dataset_root / "manifests" / "statistics.json"
    regression_path = dataset_root / "manifests" / "historical_regression.json"
    write_json(stats_path, stats)
    write_json(regression_path, regression)
    for path, role in (
        (stats_path, "statistics"),
        (regression_path, "historical_regression"),
    ):
        artifact_records.append(
            {
                "role": role,
                "relative_path": path.relative_to(repo_root).as_posix(),
                "sha256": sha256_file(path),
                "records": 1,
            }
        )

    relation_files = list(relations_dir.glob("articulo_*.txt"))
    article_files = [
        articles_dir / f"{document['document_id']}.txt"
        for document in documents
        if (articles_dir / f"{document['document_id']}.txt").exists()
    ]
    manifest = {
        "benchmark_id": BENCHMARK_ID,
        "benchmark_version": BENCHMARK_VERSION,
        "sources": [
            {
                **estatuto_meta,
                "role": "authoritative_original_hohfeld_gold",
                "files": source_file_entries(estatuto_root, relation_files + article_files),
            },
            {
                **corpus_meta,
                "role": "historical_sentence_projection_and_transformation",
                "files": source_file_entries(
                    corpus_juri_root,
                    [
                        oracle_path,
                        notebook_path,
                        *projection_text_dir.glob("ejemplo_3_*.txt"),
                    ],
                ),
            },
        ],
        "builder": {
            "repository": "re_te_benchmark",
            "commit": repository_metadata(repo_root)["commit"]
            if (repo_root / ".git" / "refs" / "heads" / "main").exists()
            else "UNCOMMITTED",
        },
        "counts": stats,
        "artifacts": sorted(artifact_records, key=lambda item: item["relative_path"]),
        "schema": {
            "id": C1_ID,
            "version": C1_VERSION,
            "relative_path": schema_path.relative_to(repo_root).as_posix(),
            "sha256": sha256_file(schema_path),
        },
        "content_metadata": {
            "timestamps_in_content": False,
            "ordering": "numeric article id, source block order, historical projection row order",
        },
    }
    manifest_path = dataset_root / "manifests" / "manifest.json"
    write_json(manifest_path, manifest)
    return {
        "manifest": manifest,
        "statistics": stats,
        "regression": regression,
        "manifest_path": manifest_path,
    }
