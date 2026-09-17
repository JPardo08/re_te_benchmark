from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from re_te_benchmark.hohfeld.builder import build, default_source_roots
from re_te_benchmark.hohfeld.eligibility import argument_pattern, classify
from re_te_benchmark.hohfeld.parser import parse_source
from re_te_benchmark.hohfeld.projections import (
    build_sentence_projection,
    build_span_complete,
    historical_regression,
    load_oracle,
    load_projection_documents,
)


ESTATUTO_ROOT, CORPUS_ROOT = default_source_roots(PROJECT_ROOT)
RELATIONS_DIR = ESTATUTO_ROOT / "data" / "old" / "rels"
ORACLE_PATH = CORPUS_ROOT / "gold_standard" / "laboral" / "hohfeld_laboral.json"
PROJECTION_TEXT_DIR = CORPUS_ROOT / "corpus" / "laboral" / "brat"


class HohfeldSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.annotations = parse_source(RELATIONS_DIR, ESTATUTO_ROOT)
        for annotation in cls.annotations:
            annotation["eligibility"] = classify(annotation)

    def test_original_inventory(self) -> None:
        self.assertEqual(len(self.annotations), 95)
        self.assertEqual(
            Counter(item["relation_type"] for item in self.annotations),
            Counter({"Duty": 49, "Right": 37, "NoRight": 5, "Privilege": 4}),
        )

    def test_argument_patterns(self) -> None:
        patterns = Counter(argument_pattern(item) for item in self.annotations)
        self.assertEqual(patterns["e1+e2+comp"], 53)
        self.assertEqual(patterns["e1+e2"], 6)
        self.assertEqual(patterns["e1+comp+MissingE2"], 25)
        self.assertEqual(patterns["e1+comp_without_MissingE2"], 5)
        self.assertEqual(patterns["e2+comp_without_e1"], 5)
        self.assertEqual(patterns["e1+e2+comp+mod"], 1)

    def test_capability_eligibility(self) -> None:
        count = lambda name: sum(
            item["eligibility"][name]["eligible"] for item in self.annotations
        )
        self.assertEqual(count("relation_type"), 95)
        self.assertEqual(count("complete_triplet_strict_inline"), 60)
        self.assertEqual(count("complete_triplet_with_missing_e2"), 85)
        self.assertEqual(count("document_level_te"), 85)
        self.assertEqual(95 - count("document_level_te"), 10)

    def test_lossless_special_fields(self) -> None:
        by_id = {item["annotation_id"]: item for item in self.annotations}
        self.assertEqual(len(by_id["articulo_47#3"]["e2"]), 2)
        self.assertEqual(by_id["articulo_12#3"]["missing_e2"]["text"], "trabajador")
        self.assertEqual(by_id["articulo_11#3"]["modifier"]["text"], "Ningún")
        self.assertGreaterEqual(
            max(len(item["complements"]) for item in self.annotations), 3
        )

    def test_historical_projection(self) -> None:
        oracle = load_oracle(ORACLE_PATH)
        documents = load_projection_documents(PROJECTION_TEXT_DIR, CORPUS_ROOT)
        projected, ids = build_sentence_projection(self.annotations, documents)
        spans = build_span_complete(projected)
        self.assertEqual(len(projected), 65)
        self.assertEqual(len(set(ids)), 65)
        self.assertEqual(len(spans), 41)
        self.assertTrue(historical_regression(projected, oracle)["exact"])


class C1Tests(unittest.TestCase):
    def test_exact_c1_labels(self) -> None:
        schema = json.loads(
            (PROJECT_ROOT / "schemas" / "c1" / "hohfeld_labels.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["version"], "1.0.0")
        self.assertEqual(schema["labels"], ["Duty", "Right", "Privilege", "NoRight"])
        self.assertEqual(
            set(schema),
            {"id", "labels", "provenance", "schema_condition", "version"},
        )


class DeterministicBuildTests(unittest.TestCase):
    def test_two_builds_have_identical_artifact_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_target = root / "schemas" / "c1" / "hohfeld_labels.json"
            schema_target.parent.mkdir(parents=True)
            schema_target.write_bytes(
                (PROJECT_ROOT / "schemas" / "c1" / "hohfeld_labels.json").read_bytes()
            )
            first = build(root, ESTATUTO_ROOT, CORPUS_ROOT)
            first_hash = hashlib.sha256(
                first["manifest_path"].read_bytes()
            ).hexdigest()
            second = build(root, ESTATUTO_ROOT, CORPUS_ROOT)
            second_hash = hashlib.sha256(
                second["manifest_path"].read_bytes()
            ).hexdigest()
            self.assertEqual(first_hash, second_hash)
            self.assertTrue(second["regression"]["exact"])


if __name__ == "__main__":
    unittest.main()
