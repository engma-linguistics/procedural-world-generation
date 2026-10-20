"""The CLI entry: source -> simulate -> save."""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path

from .. import timeline as T
from .output import save
from .params import TZParams
from .sim import simulate
from .sources import source_earth, source_from_run


def timezoom(run_ref: str, at: float = 0.0, kyr: float = 1000.0, step: float = 0.5, every: float = 2.0,
             overrides: dict | None = None, level: int = 6, name: str | None = None,
             progress=True) -> Path:
    """CLI entry: source (a run id, or 'earth') -> simulate -> runs/<id>/.
    progress: as simulate's."""
    known = {f.name for f in fields(TZParams)}
    bad = set(overrides or {}) - known
    if bad:
        raise SystemExit(f"unknown timezoom params: {sorted(bad)}; known: {sorted(known)}")
    params = TZParams(**(overrides or {}))
    src = source_earth(level) if run_ref == "earth" else source_from_run(T.find_run(run_ref), at)
    res = simulate(src, kyr, step, every, params, progress=progress)
    return save(res, src, kyr, step, every, name)
