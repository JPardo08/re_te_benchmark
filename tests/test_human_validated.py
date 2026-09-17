from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from re_te_benchmark.human_validated.builder import build
from re_te_benchmark.human_validated.iaa import compute_iaa
from re_te_benchmark.human_validated.parser import (
    default_source_roots,
    load_all_candidates,
)
from re_te_benchmark.hohfeld.manifests import repository_metadata


MREBEL_ROOT, CORPUS_ROOT = default_source_roots(PROJECT_ROOT)


class HumanValidatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates = load_all_candidates(
            MREBEL_ROOT, repository_metadata(MREBEL_ROOT)
        )

    def test_counts_and_dual_overlap(self) -> None:
        laboral = [c for c in self.candidates if c["subdomain"] == "laboral"]
        tributario = [c for c in self.candidates if c["subdomain"] == "tributario"]
        self.assertEqual(len(laboral), 1153)
        self.assertEqual(len(tributario), 1036)
        self.assertEqual(len(self.candidates), 2189)
        self.assertEqual(
            sum(1 for c in laboral if c["status"] == "accepted"), 303
        )
        self.assertEqual(
            sum(1 for c in laboral if c["status"] == "rejected"), 850
        )
        self.assertEqual(
            sum(1 for c in tributario if c["status"] == "accepted"), 162
        )
        self.assertEqual(
            sum(1 for c in tributario if c["status"] == "rejected"), 874
        )
        self.assertEqual(
            sum(1 for c in laboral if c["flags"]["disputed_before_consensus"]),
            300,
        )
        self.assertEqual(
            sum(
                1 for c in tributario if c["flags"]["disputed_before_consensus"]
            ),
            169,
        )
        self.assertEqual(
            sum(1 for c in self.candidates if c["status"] == "unresolved"), 0
        )
        self.assertEqual(
            sum(1 for c in self.candidates if c["agreement"]["both_labeled"]),
            2189,
        )
        self.assertEqual(
            sum(1 for c in self.candidates if c["status"] == "accepted")
            + sum(1 for c in self.candidates if c["status"] == "rejected"),
            2189,
        )

    def test_unique_ids_and_semantics(self) -> None:
        ids = [c["candidate_id"] for c in self.candidates]
        self.assertEqual(len(ids), len(set(ids)))
        for candidate in self.candidates:
            if candidate["status"] == "rejected":
                self.assertEqual(
                    candidate["semantics"]["rejected_means"],
                    "human_rejected_model_prediction",
                )
                self.assertFalse(
                    candidate["semantics"]["rejected_is_exhaustive_negative"]
                )

    def test_iaa_recomputation(self) -> None:
        laboral = compute_iaa(self.candidates, "laboral")
        tributario = compute_iaa(self.candidates, "tributario")
        self.assertEqual(laboral["source"], "AUDIT_RECOMPUTATION")
        self.assertEqual(tributario["source"], "AUDIT_RECOMPUTATION")
        self.assertAlmostEqual(laboral["cohen_kappa"], 0.3999666937280127)
        self.assertAlmostEqual(tributario["cohen_kappa"], 0.5156039042960537)
        self.assertEqual(laboral["n_overlap"], 1153)
        self.assertEqual(tributario["n_overlap"], 1036)


class HumanValidatedBuildTests(unittest.TestCase):
    def test_build_views_regression_and_determinism(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = build(root, MREBEL_ROOT, CORPUS_ROOT)
            first_hash = hashlib.sha256(first["manifest_path"].read_bytes()).hexdigest()
            second = build(root, MREBEL_ROOT, CORPUS_ROOT)
            second_hash = hashlib.sha256(
                second["manifest_path"].read_bytes()
            ).hexdigest()
            self.assertEqual(first_hash, second_hash)
            self.assertTrue(second["regression"]["exact"])
            self.assertEqual(
                second["regression"]["laboral"]["exact_soft_key_matches"], 303
            )
            self.assertEqual(
                second["regression"]["tributario"]["exact_soft_key_matches"], 162
            )

            accepted = [
                json.loads(line)
                for line in (
                    root
                    / "datasets/teresia_mrebel_human_validated/views/accepted/candidates.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            ]
            rejected = [
                json.loads(line)
                for line in (
                    root
                    / "datasets/teresia_mrebel_human_validated/views/rejected/candidates.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            ]
            disputed = [
                json.loads(line)
                for line in (
                    root
                    / "datasets/teresia_mrebel_human_validated/views/disputed/candidates.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            ]
            canonical_ids = {
                json.loads(line)["candidate_id"]
                for line in (
                    root
                    / "datasets/teresia_mrebel_human_validated/canonical/candidates.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            }
            self.assertEqual(len(accepted), 465)
            self.assertEqual(len(rejected), 1724)
            self.assertEqual(len(disputed), 469)
            for row in accepted + rejected + disputed:
                self.assertIn(row["candidate_id"], canonical_ids)

            constraints = second["statistics"]["evaluation_constraints"]
            self.assertFalse(constraints["independent_of_generator"])
            self.assertFalse(constraints["recall_evaluation_of_generator_valid"])
            self.assertTrue(constraints["candidate_selection_bias"])


if __name__ == "__main__":
    unittest.main()
