"""Where closed-basin area is lost (PW-054 scout 247), read-only.

Per frame:  A = % ice-free land whose water passes through any terrain hollow (priority-flood fill > 1 m)
            B = ... through a hollow the lakes keep (hydrology._bed: MIN_DEPTH 20 m, MIN_SLOPE 0.1 m/km)
            C = inland_pct (health's measure: water really ends on land)
plus aridity (Koppen B share) of each, hollow depth of the kept hollows.

usage: hollows.py ROOT RUN_ID [every_n_frames]      or     hollows.py earth LEVEL
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from planet import hydrology as Hy, kernels
from planet.geo import is_land
from planet.grid import build_grid
from planet import timeline as T
from tools import health as Hh
from tools.scorecard import GROUP


def passes(grid, h, land):
    """% cells whose drainage path (priority-flood over h) passes through a hollow of h, and the hollows."""
    sea = ~land
    filled, down, order = kernels.priority_flood(h, sea, grid.nbr_off, grid.nbr_idx, 0.01)
    return filled, down, order


def through(hollow, down, order):
    p = hollow.copy()
    for i in order:  # outlet -> headwater
        d = down[i]
        if d >= 0 and p[d]:
            p[i] = True
    return p


def measure(grid, elev, free, arid, inland=None):
    land = is_land(elev, grid=grid)
    filled, down, order = passes(grid, elev.astype(float), land)
    raw_h = land & (filled - elev > 1.0)
    A = through(raw_h, down, order)
    bed = Hy._bed(grid, elev.astype(float), ~land, Hy.MIN_DEPTH, Hy.MIN_SLOPE)
    f2, d2, o2 = passes(grid, bed, land)
    kept = land & (f2 - bed > 1.0)
    B = through(kept, d2, o2)
    nf = max(1, free.sum())
    out = {"A": 100 * (A & free).sum() / nf, "B": 100 * (B & free).sum() / nf,
           "A_hollow": 100 * (raw_h & free).sum() / nf, "B_hollow": 100 * (kept & free).sum() / nf,
           "arid_land": 100 * (arid & free).sum() / nf,
           "arid_in_B": 100 * (arid & B & free).sum() / max(1, (B & free).sum()),
           "B_of_arid": 100 * (arid & B & free).sum() / max(1, (arid & free).sum())}
    if inland is not None:
        out["arid_in_C"] = 100 * (arid & inland & free).sum() / max(1, (inland & free).sum())
        out["C_of_arid"] = 100 * (arid & inland & free).sum() / max(1, (arid & free).sum())
        out["C_of_B_wet"] = 100 * (inland & B & ~arid & free).sum() / max(1, (B & ~arid & free).sum())
        out["C_of_B_arid"] = 100 * (inland & B & arid & free).sum() / max(1, (B & arid & free).sum())
    # kept hollow depth: per hollow component, spill - floor
    lab, k = grid.components(kept)
    if k:
        dep = np.zeros(k); np.maximum.at(dep, lab[lab >= 0], (f2 - bed)[lab >= 0])
        area = np.bincount(lab[lab >= 0], minlength=k)
        out["n_hollows"] = int(k); out["hollow_depth_med_m"] = float(np.median(dep))
        out["hollow_depth_areawt_m"] = float((dep * area).sum() / area.sum())
    return out


def fmt(d):
    return " ".join(f"{k}={v:.1f}" if isinstance(v, float) else f"{k}={v}" for k, v in d.items())


if sys.argv[1] == "earth":
    from tools.earth_data import earth_on_grid  # noqa
    lvl = int(sys.argv[2])
    grid = build_grid(lvl)
    d = earth_on_grid(grid)
    elev = d["elev"].astype(float); ice = d["ice"].astype(float)
    land = is_land(elev, grid=grid); free = land & (ice <= 0)
    arid = np.asarray([str(GROUP[int(c)]) == "B" if c >= 0 else False for c in d["obs_koppen"]])
    print(f"EARTH L{lvl}", fmt(measure(grid, elev, free, arid)))
    sys.exit()

root, rid = Path(sys.argv[1]), sys.argv[2]
every = int(sys.argv[3]) if len(sys.argv) > 3 else 25
run, arr = T.load_frames(root / "runs" / rid, ("elevation", "ice", "climate", "downstream", "lake_kind"))
grid = build_grid(run["meta"]["level"])
rows = []
for i, fr in enumerate(run["frames"]):
    t = fr["stats"]["t"]
    if t < 50 or i % every:
        continue
    L = {k: T.frame(run, arr, k, i, grid) for k in ("elevation", "ice", "climate", "downstream", "lake_kind")}
    elev = np.asarray(L["elevation"], float)
    land = is_land(elev, grid=grid); free = land & (np.asarray(L["ice"]) <= 0)
    arid = GROUP[np.asarray(L["climate"])] == "B"
    down = np.asarray(L["downstream"]).astype(np.int64)
    end = Hh.drain_ends(down, land)
    real = Hh.real_hollows(grid, elev, np.asarray(L["lake_kind"]))
    inland = land[end] & real[end]
    m = measure(grid, elev, free, arid, inland)
    m["C"] = 100 * (inland & free).sum() / max(1, free.sum())
    rows.append(m)
    print(f"{rid} t={t:.0f}", fmt(m), flush=True)
keys = rows[0].keys()
print(f"{rid} MEDIAN", fmt({k: float(np.median([r[k] for r in rows if k in r])) for k in keys}))
