"""Small Equal Earth previews of runs, time zooms and worlds for the viewer's start
screen and navigator (GET /api/thumb?kind=run|world&id=...; PW-546). `proj=equirect&w=512`
gives a plain lat/lon texture for the start screen's globe picker.

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
from .images import hex_rgb, ramp_colour, write_png

W = 192
CACHE = ".thumbs"
PROJECTIONS = {"equal-earth": "ee", "equirect": "eq"}  # name -> short tag in the cache file name
WIDTHS = (192, 512, 1024)
_idx: dict = {}  # (level, projection, width) -> (nearest-cell map, valid mask)


def _cells(level: int, proj: str, width: int):
    """Cell index under each thumbnail pixel and which pixels lie inside the map outline
    (kept for the next thumbnail of that level)."""
    key = (level, proj, width)
    if key not in _idx:
        from .grid import build_grid
        from .projection import Projection, pixel_grid
        pg = pixel_grid(Projection(proj), width)
        idx = build_grid(level).locate(pg["pts"]).reshape(pg["height"], pg["width"])
        _idx[key] = (idx, pg["valid"])
    return _idx[key]


OCEAN = [(-6000, (10, 28, 62)), (-2500, (24, 62, 112)), (0, (70, 130, 185))]
LAND = [(0, (86, 130, 70)), (800, (150, 140, 90)), (2500, (130, 105, 80)), (5000, (235, 235, 235))]


def elevation_image(elev: np.ndarray) -> np.ndarray:
    land = elev >= 0
    img = np.where(land[..., None], ramp_colour(elev, LAND), ramp_colour(elev, OCEAN))
    return img.astype(np.uint8)


def _render(kind: str, item_id: str, proj: str, width: int) -> np.ndarray:
    from . import timeline as T
    if kind == "world":
        from .server import world_columns
        path = S.find_world(item_id)
        level = S.read_header(path, ("meta",))["meta"]["level"]
        cols = world_columns(path, ("biome", "elevation"))
        from . import climate
        pal = np.zeros((max(b[0] for b in climate.BIOMES) + 1, 3), np.uint8)
        for b in climate.BIOMES:
            pal[b[0]] = hex_rgb(b[3])
        idx, valid = _cells(level, proj, width)
        img = pal[cols["biome"].astype(int)[idx]]
        # a little relief shading so mountains read: darken low land, lighten high
        e = cols["elevation"][idx]
        shade = np.where(e > 0, 0.85 + 0.3 * np.clip(e / 4000, 0, 1), 1.0)[..., None]
        return _rgba(np.clip(img * shade, 0, 255).astype(np.uint8), valid)
    run_dir = S.find_run(item_id)
    run, arr = T.load_frames(run_dir, ("elevation",))
    level = run["meta"]["level"]
    i = len(run["frames"]) - 1
    elev = T.frame(run, arr, "elevation", i)
    idx, valid = _cells(level, proj, width)
    return _rgba(elevation_image(np.asarray(elev, float)[idx]), valid)


def _rgba(img: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """The picture with everything outside the map outline transparent."""
    return np.concatenate([img, np.where(valid, 255, 0).astype(np.uint8)[..., None]], -1)


def thumb(kind: str, item_id: str, proj: str = "equal-earth", width: int = W) -> Path | None:
    """The PNG of a run/time zoom ("run") or world, drawn if not cached; None when there is no such item
    (the caller answers 404) or it can't be drawn."""
    if proj not in PROJECTIONS or width not in WIDTHS:
        return None
    if kind not in ("run", "world") or not re.fullmatch(r"[0-9a-zA-Z_-]+", item_id or ""):
        return None
    item_id = item_id.removesuffix(".json")
    if not S.exists(kind, item_id):
        return None
    src = S.path_of(kind, item_id)
    if kind == "run":
        src = src / "run.json"
    tag = f"{PROJECTIONS[proj]}{width}"  # (an old thumbnail without it is never served again)
    out = S.root() / CACHE / f"{kind}-{item_id}-{tag}-{src.stat().st_mtime_ns}.png"
    if out.exists():
        return out
    from . import api
    try:
        with api.COMPUTE:  # (the grid lookup is a parallel numba kernel: one at a time per process)
            img = _render(kind, item_id, proj, width)
    except (OSError, ValueError, KeyError, SystemExit, json.JSONDecodeError):
        return None
    out.parent.mkdir(parents=True, exist_ok=True)
    for old in (*out.parent.glob(f"{kind}-{item_id}-{tag}-*.png"), *out.parent.glob(f"{kind}-{item_id}-[0-9]*.png")):
        old.unlink(missing_ok=True)
    tmp = out.with_suffix(".tmp.png")
    write_png(tmp, img)
    tmp.replace(out)
    return out
