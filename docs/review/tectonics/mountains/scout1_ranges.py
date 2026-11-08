"""Count mountain ranges: connected land regions above H km (cell means), by size class.
usage: ranges.py earth | RUN_DIR [at_myr ...]"""
import sys
from pathlib import Path

import numpy as np

from planet import timeline as T
from planet.grid import shared_grid

MAIN = Path("/home/daniel/personal/repos/procedural-world-generation")
CELL_KM2 = {6: 120.0 ** 2, 7: 60.0 ** 2}


def count(g, e, lv, H):
    lab, n = g.components(e > H * 1000)
    if not n:
        return []
    size = np.bincount(lab[lab >= 0]) * CELL_KM2[lv]
    top = np.zeros(n)
    np.maximum.at(top, lab[lab >= 0], e[lab >= 0])
    return sorted(zip(size, top), reverse=True)


def show(name, g, e, lv):
    out = [name]
    for H in (1.5, 2.0, 3.0):
        rs = count(g, e, lv, H)
        big = [r for r in rs if r[0] >= 50e3]   # >= 50,000 km2 (Alps ~200k km2 of mountains; a single L6 cell is 14,400)
        out.append(f">{H}km: {len(big)} ranges>=50k km2 (areas k km2: {', '.join(f'{a/1e3:.0f}' for a, _ in big[:8])})")
    print(" | ".join(out))


if __name__ == "__main__":
    a = sys.argv[1]
    if a == "earth":
        for lv in (6, 7):
            d = np.load(MAIN / f"data/earth/L{lv}.npz")
            e = np.where(d["surface"] > 0, d["elev"].astype(float), -1.0)
            e = np.where(d["ice"] > 10, -1.0, e)  # ice-free land only
            show(f"Earth L{lv}", shared_grid(lv), e, lv)
    else:
        r, arr = T.load_frames(Path(a), ["elevation"])
        lv = r["meta"]["level"]
        g = shared_grid(lv)
        ts = np.array([f["t"] for f in r["frames"]])
        ats = [float(x) for x in sys.argv[2:]] or list(ts[:: max(1, len(ts) // 12)])
        for at in ats:
            i = int(np.argmin(abs(ts - at)))
            show(f"{Path(a).name} L{lv} t={ts[i]:.0f}", g, T.frame(r, arr, "elevation", i).astype(float), lv)
