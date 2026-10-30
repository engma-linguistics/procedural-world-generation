"""Which code made a run: stamped into run.json so a later replay can tell
whether it is running the same model.

A run is a cache: `slice` rebuilds any moment by replaying from its latest
checkpoint with today's code. If the model changed since the run was made, the
replay is a different planet, so runs record the code that made them and
slicing checks (and compares the replay with the stored keyframe).

code_hash(scope) is the one "has the code changed?" rule for every cache: a
hash of the import closure of the scope's entry modules (SCOPES).
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


# What each cache depends on (code_hash): the import closure of these entry modules.
SCOPES = {
    "all": None,  # every module (planet/**/*.py but __main__.py): what scorecard records
    "sim": ("planet.tectonics.simulation",),  # a run's simulation (replay, timeline.slice_world's warning)
    "finish": ("planet.world", "planet.finish"),  # a world built from a keyframe or a time zoom (api.find_slice)
    "lineages": ("planet.lineages.run",),  # the peoples' caches (lineages/land.py goods, recent.py climates)
    "highlights": ("planet.highlights",),  # a world's highlights (highlights.cached)
}


def _module_file(name: str) -> Path | None:
    rel = Path(*name.split(".")[1:])
    for p in (PLANET / rel / "__init__.py", (PLANET / rel).with_suffix(".py")):
        if p.is_file():
            return p
    return None


# Infrastructure: their own source counts, but not the modules they import inside functions (the legends store.py
# assembles, the job runners in parallel.py), which would put nearly every module in every scope.
SHALLOW = {"planet.store", "planet.parallel", "planet.provenance"}


def _imports(path: Path, name: str) -> set[str]:
    """The planet.* modules that the module `name` (at path) imports, anywhere in it (function-level imports too,
    except in SHALLOW modules), with their parent packages."""
    import ast
    pkg = name if path.name == "__init__.py" else name.rpartition(".")[0]
    tree = ast.parse(path.read_bytes())
    out = set()
    for node in (tree.body if name in SHALLOW else ast.walk(tree)):
        if isinstance(node, ast.Import):
            bases = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                up = pkg.split(".")[:len(pkg.split(".")) - node.level + 1]
                base = ".".join(up + ([base] if base else []))
            bases = [base] + [f"{base}.{a.name}" for a in node.names]  # (`from . import x` may name a module)
        else:
            continue
        for b in bases:
            if b == "planet" or b.startswith("planet."):
                parts = b.split(".")
                out.update(".".join(parts[:k]) for k in range(1, len(parts) + 1))
    return out


@lru_cache(maxsize=None)
def scope_files(scope: str) -> tuple[Path, ...]:
    """The source files a scope's hash covers: its entry modules and everything they import from planet/, sorted."""
    if SCOPES[scope] is None:
        return tuple(p for p in sorted(PLANET.rglob("*.py")) if not (p.name == "__main__.py" and p.parent == PLANET))
    seen, todo = {}, list(SCOPES[scope])
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen[name] = f = _module_file(name)
        if f is not None:
            todo += sorted(_imports(f, name) - set(seen))
    return tuple(sorted({f for f in seen.values() if f is not None}))


@lru_cache(maxsize=None)
def code_hash(scope: str) -> str:
    """Hash of the source a scope depends on (SCOPES; PW-1035): the one rule every "has the code changed?"
    check uses, so a change to the server or the zoom doesn't invalidate a run's caches and a change to
    the code a cache does depend on always does. Computed once per process."""
    h = hashlib.sha256(scope.encode() + b"\0")
    for p in scope_files(scope):
        h.update(p.relative_to(PLANET).as_posix().encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


@lru_cache(maxsize=1)
def code_version() -> dict:
    """{"commit": short hash or None, "dirty": uncommitted changes under
    planet/, "planet_src_sha": code_hash("all"), "sim_sha": code_hash("sim")}.
    The simulation's hash is what slice_world compares: it also catches
    uncommitted edits."""
    commit = _git("rev-parse", "--short", "HEAD")
    status = _git("status", "--porcelain", "--", "planet")
    return {"commit": commit, "dirty": bool(status) if status is not None else None,
            "planet_src_sha": code_hash("all"), "sim_sha": code_hash("sim")}


def describe(v: dict | None) -> str:
    if not v:
        return "unknown code (made before runs recorded it)"
    return f"commit {v.get('commit')}{' + uncommitted changes' if v.get('dirty') else ''} (source {v.get('planet_src_sha')})"
