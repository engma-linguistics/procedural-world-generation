"""Which code made a run: stamped into run.json so a later replay can tell
whether it is running the same model.

A run is a cache: `slice` rebuilds any moment by replaying from t=0 with
today's code. If the model changed since the run was made, the replay is a
different planet, so runs record the code that made them and slicing checks.
"""

from __future__ import annotations

import hashlib
import subprocess
from functools import lru_cache
from pathlib import Path

PLANET = Path(__file__).resolve().parent
ROOT = PLANET.parent


def _git(*args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def source_sha() -> str:
    """Hash of the model source: planet/*.py except the command line /
    server (__main__.py), which can't change what a run computes."""
    h = hashlib.sha256()
    for p in sorted(PLANET.glob("*.py")):
        if p.name == "__main__.py":
            continue
        h.update(p.name.encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


@lru_cache(maxsize=1)
def code_version() -> dict:
    """{"commit": short hash or None, "dirty": uncommitted changes under
    planet/, "planet_src_sha": source_sha()}. The source hash is what replay
    compares: it also catches uncommitted edits."""
    commit = _git("rev-parse", "--short", "HEAD")
    status = _git("status", "--porcelain", "--", "planet")
    return {"commit": commit, "dirty": bool(status) if status is not None else None,
            "planet_src_sha": source_sha()}


def describe(v: dict | None) -> str:
    if not v:
        return "unknown code (made before runs recorded it)"
    return f"commit {v.get('commit')}{' + uncommitted changes' if v.get('dirty') else ''} (source {v.get('planet_src_sha')})"
