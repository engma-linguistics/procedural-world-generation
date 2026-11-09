"""Where each faith was at one stored moment of a peoples run (PW-1358): an equirectangular PNG for the workbench's Religion tab (drawn by faithmap_png.py, which the gods' code hash leaves out with the server it reads).

Each cell held by a culture (the presence table and demes_all, mapped to cultures through cultures.json, merges followed as gods.py
does) takes the colour of that culture's faith then (gods.json: cultures[c].faiths, faiths.list[f].color); peopled cells with no faith
(no spirit ritual yet) are pale; the rest is land or sea from the frame's elevation. Read-only.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

NONE = 65535
SEA, LAND, NOFAITH = (22, 34, 52), (58, 62, 66), (150, 150, 150)
_cache: dict = {}  # (run dir, run.json mtime) -> (run, elevation arrays, cultures doc)


def _load(run_dir: Path):
    from .. import timeline as T
    key = (str(run_dir), (run_dir / "run.json").stat().st_mtime)
    if key not in _cache:
        _cache.clear()
        run, arr = T.load_frames(run_dir, ("elevation", "ice"))
        doc = json.loads((run_dir / run["meta"]["cultures"]["file"]).read_text())
        _cache[key] = (run, arr, doc)
    return _cache[key]


def faith_of_culture(gods: dict, ago: float) -> dict[int, int]:
    """culture -> its faith at this time (the last change at or before it)."""
    out = {}
    for c, cu in (gods.get("cultures") or {}).items():
        f = None
        for a, fid in cu.get("faiths") or []:
            if a >= ago - 1e-9:
                f = fid
            else:
                break
        if f is not None:
            out[int(c)] = f
    return out


def cell_faiths(run_dir: Path, gods: dict, frame: int) -> tuple[np.ndarray, np.ndarray, float]:
    """(faith per cell or -1, peopled per cell, kyr ago) of one stored frame."""
    from ..grid import shared_grid
    from .gods import _resolver
    from .output import read_presence_frame
    run, arr, doc = _load(Path(run_dir))
    m = run["meta"]
    g = shared_grid(m["level"])
    ago = max(0.0, -run["frames"][frame]["t"])
    cells, dem, _ = read_presence_frame(Path(run_dir), m, frame)
    ok = dem != NONE
    cells, dem = cells[ok].astype(np.int64), dem[ok].astype(np.int64)
    dc = np.asarray(doc["deme_culture"], np.int64)
    res = _resolver(doc)
    fc = faith_of_culture(gods, ago)
    cmap: dict = {}
    cul = np.array([cmap.setdefault(int(dc[d]), res(int(dc[d]), ago)) if dc[d] >= 0 else -1 for d in dem], np.int64)
    fa = np.full(g.n, -1, np.int64)
    peopled = np.zeros(g.n, bool)
    peopled[cells] = True
    f_of = np.array([fc.get(int(c), -1) for c in cul], np.int64) if len(cul) else np.zeros(0, np.int64)
    o = np.argsort(f_of, kind="stable")  # (a cell shared by cultures of several faiths: the highest faith id drawn last wins; stable)
    fa[cells[o]] = f_of[o]
    return fa, peopled, ago
