"""The PNG of lineages/faithmap.py (PW-1358): the grid lookup under each pixel is thumbs._cells, which reaches the server, so this read-out
sits apart from faithmap (which gods, cuisine and tongues read faiths from) to keep the server out of the peoples' code hash (PW-1582)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ..images import hex_rgb, png_bytes
from .faithmap import LAND, NOFAITH, SEA, _load, cell_faiths


def render(run_dir: Path, gods: dict, frame: int, width: int = 1024, only: int | None = None) -> bytes:
    """The PNG; only: one faith in colour, the other faiths' cells pale."""
    from .. import timeline as T
    from ..thumbs import _cells
    run, arr, _ = _load(Path(run_dir))
    fa, peopled, _ = cell_faiths(run_dir, gods, frame)
    elev = np.asarray(T.frame(run, arr, "elevation", frame), float)
    ice = np.asarray(T.frame(run, arr, "ice", frame), float)
    cols = np.zeros((len(elev), 3), np.uint8)
    land = elev >= 0
    cols[:] = SEA
    cols[land] = LAND
    cols[land & (ice > 0)] = (120, 130, 140)
    cols[peopled & (fa < 0)] = NOFAITH
    pal = {f["id"]: hex_rgb(f["color"]) for f in (gods.get("faiths") or {}).get("list", [])}
    for f in np.unique(fa[fa >= 0]):
        cols[fa == f] = pal.get(int(f), (255, 0, 255)) if only is None or int(f) == only else (96, 100, 106)
    idx, valid = _cells(run["meta"]["level"], "equirect", width)
    img = cols[idx]
    return png_bytes(np.concatenate([img, np.where(valid, 255, 0).astype(np.uint8)[..., None]], -1))
