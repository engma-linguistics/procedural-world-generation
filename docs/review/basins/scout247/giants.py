"""Giant lakes (> 1 Mkm2) of a run's frames: kind, rain on them, ice next to them, depth. Read-only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from planet.geo import is_land
from planet.grid import build_grid
from planet import timeline as T
from tools.health import EARTH_KM2

root_dir, rid = Path(sys.argv[1]), sys.argv[2]
names = ("elevation", "ice", "lake_depth", "lake_kind", "precipitation")
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
    nb = np.zeros(grid.n, bool)
    for _ in range(2):
        m2 = m | nb
        nb = np.maximum.reduceat(m2[grid.nbr_idx].astype(np.int8), grid.nbr_off[:-1]).astype(bool) & ~m
    kinds = np.bincount(L["lake_kind"][m].astype(int), minlength=4)
    print(f"t={fr['stats']['t']:.0f} {sz[b]*ck/1e6:.2f} Mkm2 kinds(open,closed,pan)={kinds[1:]} rain {L['precipitation'][m].mean():.0f} mm "
          f"depth med {np.median(L['lake_depth'][m]):.0f} m, ice on shore {100*(L['ice'][nb] > 0).mean():.0f}%", flush=True)
