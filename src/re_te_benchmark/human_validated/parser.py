"""Canonical parsing of the human-judged mREBEL candidate universe."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path
from typing import Any

from .xlsx import load_workbook, sheet_records

SUBDOMAIN_CONFIG = {
    "laboral": {
        "final_relative": (
            "src/rebel/v3/evaluacion/resultados_finales/metricas_finales_laboral.xlsx"
        ),
        "sheet": "tripletas_etiquetadas",
        "annotator_a": "annotator_A",
        "annotator_b": "annotator_B",
        "eval_a": "eval_Patri",
        "eval_b": "eval_Elena",
        "notes_a": "notas_Patri",
        "notes_b": "notas_Elena",
        "published_relative": "silver_standard/laboral/tripletas_laboral.csv",
        "historical_iaa": {
            "source": "HISTORICAL_REPORTED_METRIC",
            "artifact": (
                "src/rebel/v3/evaluacion/resultados_finales/metricas_finales_laboral.xlsx"
            ),
            "sheet": "iaa_pre_adjudicacion",
            "cohen_kappa": 0.3999666937280127,
            "observed_agreement": 0.7398091934084996,
            "n_overlap": 1153,
        },
    },
    "tributario": {
        "final_relative": (
            "src/rebel/v3/evaluacion/resultados_finales/metricas_finales_tributario.xlsx"
        ),
        "sheet": "tripletas_etiquetadas",
        "annotator_a": "annotator_A",
        "annotator_b": "annotator_B",
        "eval_a": "eval_Victoria",
        "eval_b": "eval_Soco",
        "notes_a": "notas_Victoria",
        "notes_b": "notas_Soco",
        "published_relative": "silver_standard/tributario/tripletas_tributario.csv",
        "historical_iaa": {
            "source": "HISTORICAL_REPORTED_METRIC",
            "artifact": (
                "src/rebel/v3/evaluacion/resultados_finales/"
                "metricas_finales_tributario.xlsx"
            ),
            "sheet": "iaa_pre_adjudicacion",
            "cohen_kappa": 0.5156039042960537,
            "observed_agreement": 0.8368725868725869,
            "n_overlap": 1036,
        },
    },
}

CONTEXT_FIELDS = ("doc", "sent_id", "subject", "relation", "object")


def default_source_roots(repo_root: Path) -> tuple[Path, Path]:
    legacy = repo_root.parent / "_legacy"
    return legacy / "teresia-mrebel", legacy / "teresia-mrebel-corpus-juri"


def normalize_eval(value: Any) -> bool | None:
    text = unicodedata.normalize("NFD", str(value).strip().lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    if text in {"si", "yes", "true", "1"}:
        return True
    if text in {"no", "false", "0"}:
        return False
    if text == "":
        return None
    return None


def soft_key(record: dict[str, Any]) -> tuple[str, str, str, str, str]:
    sent_id = str(record.get("sent_id", "")).strip()
    if sent_id.endswith(".0"):
        sent_id = sent_id[:-2]
    return (
        str(record.get("doc", "")).strip(),
        sent_id,
        str(record.get("subject", "")).strip(),
        str(record.get("relation", "")).strip(),
        str(record.get("object", "")).strip(),
    )


def _offset(value: Any) -> float | None:
    text = str(value).strip()
    if text == "" or text.lower() in {"none", "nan", "null"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _candidate_id(subdomain: str, row_canon: str, soft: tuple[str, ...]) -> str:
    payload = "|".join((subdomain, str(row_canon).strip(), *soft))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    safe_canon = re.sub(r"[^0-9A-Za-z]+", "", str(row_canon).strip()) or "na"
    return f"{subdomain}_{safe_canon}_{digest}"


def _status(valid: bool | None) -> str:
    if valid is True:
        return "accepted"
    if valid is False:
        return "rejected"
    return "unresolved"


def parse_final_sheet(
    path: Path,
    subdomain: str,
    source_meta: dict[str, str],
) -> list[dict[str, Any]]:
    config = SUBDOMAIN_CONFIG[subdomain]
    workbook = load_workbook(path)
    if config["sheet"] not in workbook:
        raise KeyError(f"Missing sheet {config['sheet']} in {path}")
    records = sheet_records(workbook[config["sheet"]])
    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(records, start=1):
        valid_a = normalize_eval(row.get(config["eval_a"]))
        valid_b = normalize_eval(row.get(config["eval_b"]))
        consensus = normalize_eval(row.get("eval_final"))
        soft = soft_key(row)
        row_canon = str(row.get("row_canon", "")).strip() or str(index)
        candidate_id = _candidate_id(subdomain, row_canon, soft)
        if candidate_id in seen_ids:
            raise ValueError(f"Duplicate candidate_id: {candidate_id}")
        seen_ids.add(candidate_id)
        origen = str(row.get("origen_eval_final", "")).strip()
        disputed = origen == "adjudicado" or (
            valid_a is not None and valid_b is not None and valid_a != valid_b
        )
        relative_file = config["final_relative"]
        candidates.append(
            {
                "candidate_id": candidate_id,
                "subdomain": subdomain,
                "context": {
                    "doc": soft[0],
                    "sent_id": soft[1],
                    "text": str(row.get("sent_text", "")),
                },
                "prediction": {
                    "subject": soft[2],
                    "subject_type": str(row.get("subject_type", "")).strip() or None,
                    "relation": soft[3],
                    "object": soft[4],
                    "object_type": str(row.get("object_type", "")).strip() or None,
                    "subj_start": _offset(row.get("subj_start")),
                    "subj_end": _offset(row.get("subj_end")),
                    "obj_start": _offset(row.get("obj_start")),
                    "obj_end": _offset(row.get("obj_end")),
                },
                "generator": {
                    "family": "mREBEL",
                    "model_dependent": True,
                    "checkpoint": "Babelscape/mrebel-large",
                    "exact_historical_revision": "UNKNOWN",
                    "provenance_status": (
                        "canonical_from_human_judged_stage;"
                        "raw_prediction_dump_not_used_as_parent"
                    ),
                    "relation_family": "wikidata_like_rebel",
                    "historical_relation_filter": "REL_ALLOWED",
                },
                "judgments": {
                    config["annotator_a"]: {
                        "valid": valid_a,
                        "notes": str(row.get(config["notes_a"], "") or ""),
                    },
                    config["annotator_b"]: {
                        "valid": valid_b,
                        "notes": str(row.get(config["notes_b"], "") or ""),
                    },
                },
                "agreement": {
                    "agreed": bool(
                        valid_a is not None
                        and valid_b is not None
                        and valid_a == valid_b
                    ),
                    "both_labeled": valid_a is not None and valid_b is not None,
                },
                "consensus": {
                    "valid": consensus,
                    "notes": str(row.get("notas_final", "") or ""),
                    "origin": origen or None,
                    "adjudication_notes": str(row.get("notas_resueltas", "") or ""),
                    "disagreement_reason": str(row.get("motivo_discrepancia", "") or ""),
                },
                "status": _status(consensus),
                "semantics": {
                    "accepted_means": "human_accepted_mrebel_proposal",
                    "rejected_means": "human_rejected_model_prediction",
                    "rejected_is_exhaustive_negative": False,
                },
                "flags": {
                    "disputed_before_consensus": disputed,
                    "model_dependent_human_validated": True,
                },
                "provenance": {
                    "repository": source_meta["repository"],
                    "repository_url": source_meta["url"],
                    "commit": source_meta["commit"],
                    "relative_file": relative_file,
                    "sheet": config["sheet"],
                    "row_canon": row_canon,
                    "source_row_index": index,
                    "soft_key": {
                        "doc": soft[0],
                        "sent_id": soft[1],
                        "subject": soft[2],
                        "relation": soft[3],
                        "object": soft[4],
                    },
                },
            }
        )
    return candidates


def load_all_candidates(
    teresia_mrebel_root: Path,
    source_meta: dict[str, str],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for subdomain, config in SUBDOMAIN_CONFIG.items():
        path = teresia_mrebel_root / config["final_relative"]
        if not path.exists():
            raise FileNotFoundError(path)
        candidates.extend(parse_final_sheet(path, subdomain, source_meta))
    candidates.sort(
        key=lambda item: (
            0 if item["subdomain"] == "laboral" else 1,
            int(str(item["provenance"]["row_canon"]))
            if str(item["provenance"]["row_canon"]).isdigit()
            else 10**9,
            item["candidate_id"],
        )
    )
    return candidates
