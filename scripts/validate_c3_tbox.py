#!/usr/bin/env python3
"""Re-check the pinned C3 TBox hashes and, optionally, ROBOT consistency.

The script does not download Java, ROBOT, or a reasoner, and it does not
modify the ontology. OWL 2 DL profile checking remains the procedure recorded
in docs/CONDITIONING_SPEC.md: OWL API 4.5.29 OWL2DLProfile, using an
externally supplied ROBOT 1.9.11 jar. This file does not embed that jar.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from re_te_benchmark.conditioning.c2 import load_c2_package  # noqa: E402
from re_te_benchmark.conditioning.c3 import (  # noqa: E402
    C2_CONTENT_SHA256,
    C2_PAYLOAD_SHA256,
    c3_model_payload,
    validate_c3_ontology,
)


FIXTURE_CONSISTENCY = {
    "consistent_absent_correlative.ttl": True,
    "consistent_opposite_different_act.ttl": True,
    "consistent_same_party.ttl": True,
    "consistent_two_acts.ttl": True,
    "consistent_unswapped.ttl": True,
    "inconsistent_correlative_type.ttl": False,
    "inconsistent_self_and_overlap.ttl": False,
    "inconsistent_two_classes_and_polarities.ttl": False,
}


def _run(java: str, robot: str, args: list[str]) -> int:
    completed = subprocess.run(
        [java, "-jar", robot, *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode not in (0, 1):
        sys.stderr.write(completed.stderr)
        raise RuntimeError(f"ROBOT command failed with status {completed.returncode}.")
    return completed.returncode


def check_hashes() -> None:
    """Fail if the live C2 package or the pinned C3 TBox has drifted."""
    package = load_c2_package()
    if package["integrity"]["content_sha256"] != C2_CONTENT_SHA256:
        raise RuntimeError("C2 content hash drifted.")
    if package["integrity"]["payload_sha256"] != C2_PAYLOAD_SHA256:
        raise RuntimeError("C2 payload hash drifted.")
    validate_c3_ontology()


def check_robot(java: str, robot: str) -> None:
    """Re-run HermiT consistency on the TBox and on each synthetic fixture merge."""
    ontology = REPO_ROOT / "schemas" / "c3" / "c3_ontology_v1.ttl"
    fixtures = REPO_ROOT / "tests" / "fixtures" / "c3"
    with tempfile.TemporaryDirectory(prefix="c3-tbox-") as temporary:
        folder = Path(temporary)
        status = _run(
            java,
            robot,
            ["reason", "--input", str(ontology), "--reasoner", "HermiT", "--output", str(folder / "tbox.ttl")],
        )
        if status != 0:
            raise RuntimeError("HermiT found the pinned TBox inconsistent.")
        for name, expect_consistent in FIXTURE_CONSISTENCY.items():
            merged = folder / f"{name}.merged.ttl"
            reasoned = folder / f"{name}.reasoned.ttl"
            merge_status = _run(
                java,
                robot,
                ["merge", "--input", str(ontology), "--input", str(fixtures / name), "--output", str(merged)],
            )
            if merge_status != 0:
                raise RuntimeError(f"ROBOT could not merge {name}.")
            reason_status = _run(
                java,
                robot,
                ["reason", "--input", str(merged), "--reasoner", "HermiT", "--output", str(reasoned)],
            )
            consistent = reason_status == 0
            if consistent != expect_consistent:
                raise RuntimeError(f"Unexpected HermiT result for {name}: consistent={consistent}.")
        projection = folder / "c3-projection.ofn"
        projection.write_text(c3_model_payload()["owl_functional"], encoding="utf-8")
        converted = folder / "c3-projection.ttl"
        convert_status = _run(
            java,
            robot,
            [
                "convert",
                "--input",
                str(projection),
                "--input-format",
                "ofn",
                "--output",
                str(converted),
            ],
        )
        if convert_status != 0:
            raise RuntimeError("ROBOT could not parse the OWL Functional projection.")
        projection_status = _run(
            java,
            robot,
            [
                "reason",
                "--input",
                str(converted),
                "--reasoner",
                "HermiT",
                "--output",
                str(folder / "c3-projection.reasoned.ttl"),
            ],
        )
        if projection_status != 0:
            raise RuntimeError("HermiT found the OWL Functional projection inconsistent.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", help="Path to a JDK java binary. Not stored in the repository.")
    parser.add_argument("--robot", help="Path to robot.jar. Not stored in the repository.")
    args = parser.parse_args(argv)
    if bool(args.java) != bool(args.robot):
        parser.error("--java and --robot must be supplied together.")
    check_hashes()
    if args.java and args.robot:
        check_robot(args.java, args.robot)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError) as exc:
        sys.stderr.write(f"{exc}\n")
        raise SystemExit(1) from exc
