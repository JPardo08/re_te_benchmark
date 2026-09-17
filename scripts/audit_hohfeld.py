#!/usr/bin/env python3
"""Audit generated Hohfeld benchmark invariants and hashes."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from re_te_benchmark.cli import audit_main


if __name__ == "__main__":
    raise SystemExit(audit_main())
