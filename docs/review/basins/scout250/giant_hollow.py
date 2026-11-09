"""PW-054 scout 250: for each frame's giant lake (> 1 Mkm2), would _bed keep its hollow without the dry rule?
Depth of the filled hollow under the lake (priority flood to its spill) and its rim-to-middle slope against
MIN_DEPTH / MIN_SLOPE. Read-only. Usage: giant_hollow.py DATA_ROOT RUN_ID"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from planet.geo import is_land
from planet.grid import build_grid
from planet import timeline as T, kernels, hydrology as Hy
from tools.health import EARTH_KM2

root_dir, rid = Path(sys.argv[1]), sys.argv[2]
names = ("elevation", "lake_depth", "lake_kind", "precipitation")
run, arr = T.load_frames(root_dir / "runs" / rid, names)
grid = build_grid(run["meta"]["level"])
ck = EARTH_KM2 / grid.n
for i, fr in enumerate(run["frames"]):
    L = {k: np.asarray(T.frame(run, arr, k, i, grid), float) for k in names}
    land = is_land(L["elevation"], grid=grid)
    lake = land & (L["lake_depth"] > 0)
    lab, k = grid.components(lake)
    if not k:
        continue
    sz = np.bincount(lab[lab >= 0])
    b = int(sz.argmax())
    if sz[b] * ck < 1e6:
        continue
    m = lab == b
    e = L["elevation"]
    filled = kernels.priority_flood(e, ~land, grid.nbr_off, grid.nbr_idx, 0.0)[0]
    hol = land & (filled > e + 0.01)
    hl, _ = grid.components(hol)
    ids = np.unique(hl[m & hol])
    h = np.isin(hl, ids) & hol
    depth = (filled - e)[h].max() if h.any() else 0.0
    area = h.sum() * ck
    slope = depth / np.sqrt(area / np.pi) if area else 0.0
    kept_by_bed = depth >= Hy.MIN_DEPTH and slope >= Hy.MIN_SLOPE
    kinds = np.bincount(L["lake_kind"][m].astype(int), minlength=4)[1:]
    print(f"t={fr['stats']['t']:.0f} lake {sz[b]*ck/1e6:.2f} Mkm2 kinds {kinds} rain {L['precipitation'][m].mean():.0f} | "
          f"hollow {area/1e6:.2f} Mkm2, {depth:.0f} m deep, {slope:.3f} m/km: _bed keeps it: {kept_by_bed}", flush=True)
