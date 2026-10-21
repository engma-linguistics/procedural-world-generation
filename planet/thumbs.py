"""Small equirectangular previews of runs, time zooms and worlds for the
viewer's start screen and navigator (GET /api/thumb?kind=run|world&id=...).

Zooms have a preview.png of their own. Thumbnails are drawn once and cached
under <data root>/.thumbs/ (a changed file gets a new name: its mtime is in
it), so a gallery of fifty planets costs one pass.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from . import store as S
from .images import write_png

W, H = 192, 96
CACHE = ".thumbs"
_idx: dict = {}  # (level) -> nearest-cell map


def _hex(c: str) -> tuple:
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _cells(level: int) -> np.ndarray:
    """Cell index under each thumbnail pixel (kept for the next thumbnail of that level)."""
    if level not in _idx:
        from .grid import build_grid
        from .world import nearest_cell_map
        _idx[level] = nearest_cell_map(build_grid(level), W, H)
    return _idx[level]


def _lerp(stops, v):
    """Piecewise-linear colour of values v (array) through [(value, (r, g, b)), ...]."""
    xs = [s[0] for s in stops]
    return np.stack([np.interp(v, xs, [s[1][c] for s in stops]) for c in range(3)], -1)


OCEAN = [(-6000, (10, 28, 62)), (-2500, (24, 62, 112)), (0, (70, 130, 185))]
LAND = [(0, (86, 130, 70)), (800, (150, 140, 90)), (2500, (130, 105, 80)), (5000, (235, 235, 235))]


def elevation_image(elev: np.ndarray) -> np.ndarray:
    land = elev >= 0
    img = np.where(land[..., None], _lerp(LAND, elev), _lerp(OCEAN, elev))
    return img.astype(np.uint8)


def _render(kind: str, item_id: str) -> np.ndarray:
    from . import timeline as T
    if kind == "world":
        from .server import world_columns
        path = S.find_world(item_id)
        level = S.read_header(path, ("meta",))["meta"]["level"]
        cols = world_columns(path, ("biome", "elevation"))
        from . import climate
        pal = np.zeros((max(b[0] for b in climate.BIOMES) + 1, 3), np.uint8)
        for b in climate.BIOMES:
            pal[b[0]] = _hex(b[3])
        idx = _cells(level)
        img = pal[cols["biome"].astype(int)[idx]]
        # a little relief shading so mountains read: darken low land, lighten high
        e = cols["elevation"][idx]
        shade = np.where(e > 0, 0.85 + 0.3 * np.clip(e / 4000, 0, 1), 1.0)[..., None]
        return np.clip(img * shade, 0, 255).astype(np.uint8)
    run_dir = S.find_run(item_id)
    run, arr = T.load_frames(run_dir, ("elevation",))
    level = run["meta"]["level"]
    i = len(run["frames"]) - 1
    elev = T.frame(run, arr, "elevation", i)
    return elevation_image(np.asarray(elev, float)[_cells(level)])


def thumb(kind: str, item_id: str) -> Path | None:
    """The PNG of a run/time zoom ("run") or world, drawn if not cached; None when there is no such item
    (the caller answers 404) or it can't be drawn."""
    if kind not in ("run", "world") or not re.fullmatch(r"[0-9a-zA-Z_-]+", item_id or ""):
        return None
    item_id = item_id.removesuffix(".json")
    if not S.exists(kind, item_id):
        return None
    src = S.path_of(kind, item_id)
    if kind == "run":
        src = src / "run.json"
    out = S.root() / CACHE / f"{kind}-{item_id}-{src.stat().st_mtime_ns}.png"
    if out.exists():
        return out
    from . import api
    try:
        with api.COMPUTE:  # (the grid lookup is a parallel numba kernel: one at a time per process)
            img = _render(kind, item_id)
    except (OSError, ValueError, KeyError, SystemExit, json.JSONDecodeError):
        return None
    out.parent.mkdir(parents=True, exist_ok=True)
    for old in out.parent.glob(f"{kind}-{item_id}-*.png"):
        old.unlink(missing_ok=True)
    tmp = out.with_suffix(".tmp.png")
    write_png(tmp, img)
    tmp.replace(out)
    return out
