"""Deterministic hashing and repository provenance helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(
                json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                + "\n"
            )
            count += 1
    return count


def _git_value(root: Path, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _read_ref(root: Path) -> str | None:
    git_dir = root / ".git"
    head = git_dir / "HEAD"
    if not head.exists():
        return None
    value = head.read_text(encoding="utf-8").strip()
    if not value.startswith("ref: "):
        return value or None
    ref = value.removeprefix("ref: ")
    loose = git_dir / ref
    if loose.exists():
        return loose.read_text(encoding="utf-8").strip()
    packed = git_dir / "packed-refs"
    if packed.exists():
        for line in packed.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#") and line.endswith(f" {ref}"):
                return line.split(" ", 1)[0]
    return None


def repository_metadata(root: Path) -> dict[str, str]:
    commit = _git_value(root, "rev-parse", "HEAD") or _read_ref(root) or "UNKNOWN"
    url = _git_value(root, "remote", "get-url", "origin") or "UNKNOWN"
    if url == "UNKNOWN":
        config = root / ".git" / "config"
        if config.exists():
            for line in config.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("url ="):
                    url = line.split("=", 1)[1].strip()
                    break
    return {"repository": root.name, "url": url, "commit": commit}


def source_file_entries(root: Path, paths: Iterable[Path]) -> list[dict[str, Any]]:
    return [
        {
            "relative_path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(set(paths), key=lambda item: item.relative_to(root).as_posix())
    ]
