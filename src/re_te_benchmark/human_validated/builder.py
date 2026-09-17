"""Build the reproducible mREBEL human-validated asset."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ..hohfeld.manifests import (
    repository_metadata,
    sha256_file,
    source_file_entries,
    write_json,
    write_jsonl,
)
from .iaa import compute_iaa
from .parser import SUBDOMAIN_CONFIG, default_source_roots, load_all_candidates
from .views import load_published_csv, published_regression, view_records

RESOURCE_ID = "teresia_mrebel_human_validated"
RESOURCE_VERSION = "0.1.0"


def _counts(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    by_sub: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in candidates:
        by_sub[item["subdomain"]].append(item)

    def subdomain_block(name: str) -> dict[str, Any]:
        rows = by_sub[name]
        accepted = [row for row in rows if row["status"] == "accepted"]
        rejected = [row for row in rows if row["status"] == "rejected"]
        disputed = [row for row in rows if row["flags"]["disputed_before_consensus"]]
        unresolved = [row for row in rows if row["status"] == "unresolved"]
        dual = sum(1 for row in rows if row["agreement"]["both_labeled"])
        judged_rels = Counter(row["prediction"]["relation"] for row in rows)
        accepted_rels = Counter(row["prediction"]["relation"] for row in accepted)
        rejected_rels = Counter(row["prediction"]["relation"] for row in rejected)
        acceptance_rate = {
            relation: (
                accepted_rels.get(relation, 0) / count if count else None
            )
            for relation, count in sorted(judged_rels.items())
        }
        return {
            "judged": len(rows),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "disputed_before_consensus": len(disputed),
            "unresolved": len(unresolved),
            "dual_annotator_coverage": dual,
            "relation_distribution_judged": dict(sorted(judged_rels.items())),
            "relation_distribution_accepted": dict(sorted(accepted_rels.items())),
            "relation_distribution_rejected": dict(sorted(rejected_rels.items())),
            "acceptance_rate_by_relation": acceptance_rate,
        }

    laboral = subdomain_block("laboral")
    tributario = subdomain_block("tributario")
    return {
        "resource_id": RESOURCE_ID,
        "resource_version": RESOURCE_VERSION,
        "resource_type": "model_dependent_human_validated",
        "generator": "mREBEL",
        "total": {
            "judged": laboral["judged"] + tributario["judged"],
            "accepted": laboral["accepted"] + tributario["accepted"],
            "rejected": laboral["rejected"] + tributario["rejected"],
            "disputed_before_consensus": (
                laboral["disputed_before_consensus"]
                + tributario["disputed_before_consensus"]
            ),
            "unresolved": laboral["unresolved"] + tributario["unresolved"],
            "dual_annotator_coverage": (
                laboral["dual_annotator_coverage"]
                + tributario["dual_annotator_coverage"]
            ),
        },
        "laboral": laboral,
        "tributario": tributario,
    }


def build(
    repo_root: Path,
    teresia_mrebel_root: Path,
    corpus_juri_root: Path,
) -> dict[str, Any]:
    mrebel_meta = repository_metadata(teresia_mrebel_root)
    corpus_meta = repository_metadata(corpus_juri_root)
    candidates = load_all_candidates(teresia_mrebel_root, mrebel_meta)

    accepted = view_records(candidates, status="accepted")
    rejected = view_records(candidates, status="rejected")
    disputed = view_records(candidates, disputed_only=True)

    regression = {
        "laboral": published_regression(
            accepted,
            load_published_csv(
                corpus_juri_root / SUBDOMAIN_CONFIG["laboral"]["published_relative"]
            ),
            "laboral",
        ),
        "tributario": published_regression(
            accepted,
            load_published_csv(
                corpus_juri_root / SUBDOMAIN_CONFIG["tributario"]["published_relative"]
            ),
            "tributario",
        ),
    }
    regression["exact"] = (
        regression["laboral"]["exact"] and regression["tributario"]["exact"]
    )

    iaa = {
        "laboral": {
            "audit_recomputation": compute_iaa(candidates, "laboral"),
            "historical_reported": SUBDOMAIN_CONFIG["laboral"]["historical_iaa"],
        },
        "tributario": {
            "audit_recomputation": compute_iaa(candidates, "tributario"),
            "historical_reported": SUBDOMAIN_CONFIG["tributario"]["historical_iaa"],
        },
    }

    stats = _counts(candidates)
    stats["iaa"] = {
        subdomain: {
            "AUDIT_RECOMPUTATION": block["audit_recomputation"],
            "HISTORICAL_REPORTED_METRIC": block["historical_reported"],
            "kappa_matches_historical": (
                abs(
                    (block["audit_recomputation"]["cohen_kappa"] or 0)
                    - block["historical_reported"]["cohen_kappa"]
                )
                < 1e-12
            ),
        }
        for subdomain, block in iaa.items()
    }
    stats["published_regression"] = regression
    stats["evaluation_constraints"] = {
        "independent_of_generator": False,
        "recall_evaluation_of_generator_valid": False,
        "candidate_selection_bias": True,
        "relation_ontology": "wikidata_like_rebel_not_hohfeld",
        "rejected_semantics": "human_rejected_model_prediction",
    }
    stats["provenance_notes"] = {
        "canonical_universe": "human_judged_final_excels",
        "raw_prediction_dumps": (
            "recorded_as_historical_context_only;"
            "not_used_as_canonical_parent_due_to_laboral_version_drift"
        ),
        "published_silver_role": "regression_oracle_for_accepted_view",
    }

    dataset_root = repo_root / "datasets" / RESOURCE_ID
    artifact_specs = [
        (dataset_root / "canonical" / "candidates.jsonl", candidates, "canonical"),
        (dataset_root / "views" / "accepted" / "candidates.jsonl", accepted, "accepted"),
        (dataset_root / "views" / "rejected" / "candidates.jsonl", rejected, "rejected"),
        (dataset_root / "views" / "disputed" / "candidates.jsonl", disputed, "disputed"),
    ]
    artifacts: list[dict[str, Any]] = []
    for path, records, role in artifact_specs:
        count = write_jsonl(path, records)
        artifacts.append(
            {
                "role": role,
                "relative_path": path.relative_to(repo_root).as_posix(),
                "sha256": sha256_file(path),
                "records": count,
            }
        )

    stats_path = dataset_root / "manifests" / "statistics.json"
    regression_path = dataset_root / "manifests" / "historical_regression.json"
    write_json(stats_path, stats)
    write_json(regression_path, regression)
    for path, role in ((stats_path, "statistics"), (regression_path, "historical_regression")):
        artifacts.append(
            {
                "role": role,
                "relative_path": path.relative_to(repo_root).as_posix(),
                "sha256": sha256_file(path),
                "records": 1,
            }
        )

    context_dumps = [
        teresia_mrebel_root
        / "src/rebel/v3/results_completos/triplets_allowed_sentences_offsets_estatuto.csv",
        teresia_mrebel_root
        / "src/rebel/v3/results_completos/triplets_allowed_sentences_offsets_tributario.csv",
        teresia_mrebel_root / "src/rebel/v3/core/model.py",
    ]
    existing_context = [path for path in context_dumps if path.exists()]
    builder_commit = repository_metadata(repo_root)["commit"]
    if builder_commit == "UNKNOWN":
        builder_commit = "UNCOMMITTED"

    manifest = {
        "resource_id": RESOURCE_ID,
        "resource_version": RESOURCE_VERSION,
        "resource_type": "model_dependent_human_validated",
        "role": "AUXILIARY_HUMAN_VALIDATED_ASSET",
        "generator": {
            "family": "mREBEL",
            "checkpoint": "Babelscape/mrebel-large",
            "model_dependent": True,
        },
        "evaluation_constraints": stats["evaluation_constraints"],
        "sources": [
            {
                **mrebel_meta,
                "role": "authoritative_human_judged_universe",
                "files": source_file_entries(
                    teresia_mrebel_root,
                    [
                        teresia_mrebel_root / config["final_relative"]
                        for config in SUBDOMAIN_CONFIG.values()
                    ],
                ),
            },
            {
                **corpus_meta,
                "role": "published_accepted_silver_regression_oracle",
                "files": source_file_entries(
                    corpus_juri_root,
                    [
                        corpus_juri_root / config["published_relative"]
                        for config in SUBDOMAIN_CONFIG.values()
                    ],
                ),
            },
            {
                **mrebel_meta,
                "role": "historical_prediction_context_not_canonical_parent",
                "files": source_file_entries(teresia_mrebel_root, existing_context),
                "note": (
                    "Laboral allowed sentence dump exhibits soft-key drift versus "
                    "human Excels; dumps are provenance context only."
                ),
            },
        ],
        "builder": {
            "repository": "re_te_benchmark",
            "commit": builder_commit,
        },
        "counts": stats,
        "artifacts": sorted(artifacts, key=lambda item: item["relative_path"]),
        "content_metadata": {
            "timestamps_in_content": False,
            "ordering": (
                "subdomain laboral then tributario; ascending row_canon; candidate_id"
            ),
            "candidate_id_policy": (
                "sha256(subdomain|row_canon|doc|sent_id|subject|relation|object)[:16]; "
                "contextual soft-key collisions are distinct candidates"
            ),
            "notes_policy": "FREE_TEXT_ONLY; no error taxonomy",
        },
    }
    manifest_path = dataset_root / "manifests" / "manifest.json"
    write_json(manifest_path, manifest)
    return {
        "manifest": manifest,
        "statistics": stats,
        "regression": regression,
        "manifest_path": manifest_path,
        "candidates": candidates,
    }
