#!/usr/bin/env python3
"""Build the Hohfeld benchmark without requiring package installation."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from re_te_benchmark.cli import build_main


if __name__ == "__main__":
    raise SystemExit(build_main())
