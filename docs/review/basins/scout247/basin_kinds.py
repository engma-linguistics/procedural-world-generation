"""What the inland-draining land's sinks sit in (read-only): for each frame, the sinks' catchment area split by the
sink cell's setting. Settings (first match): pit = thin continent (< 30 km) or ocean crust cut off on land;
moat = thick crust (> 45 km) within ~2 cells; rift = rift_strain > 0.05; arid plain = Koppen B; plain = the rest."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from planet.geo import is_land
from planet.grid import build_grid
from planet import timeline as T
from tools import health as Hh
from tools.scorecard import GROUP

root_dir, rid, every = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
names = ("elevation", "ice", "climate", "downstream", "lake_kind", "crust", "crust_thickness", "rift_strain")
run, arr = T.load_frames(root_dir / "runs" / rid, names)
grid = build_grid(run["meta"]["level"])
tot = {}
nfr = 0
for i, fr in enumerate(run["frames"]):
    t = fr["stats"]["t"]
    if t < 50 or i % every:
        continue
    L = {k: np.asarray(T.frame(run, arr, k, i, grid)) for k in names}
    elev = L["elevation"].astype(float)
    land = is_land(elev, grid=grid); free = land & (L["ice"] <= 0)
    down = L["downstream"].astype(np.int64)
    end = Hh.drain_ends(down, land)
    real = Hh.real_hollows(grid, elev, L["lake_kind"])
    inland = land[end] & real[end] & free
    thick = L["crust_thickness"].astype(float); cont = L["crust"] > 0
    near = (thick > 45) & cont
    for _ in range(2):
        near = near | np.maximum.reduceat(near[grid.nbr_idx].astype(np.int8), grid.nbr_off[:-1]).astype(bool)
    arid = GROUP[L["climate"]] == "B"
    kind = np.full(grid.n, "plain", dtype=object)
    kind[arid] = "arid plain"
    kind[L["rift_strain"].astype(float) > 0.05] = "rift"
    kind[near] = "moat/intermontane"
    kind[(~cont) | (thick < 30)] = "pit (thin/ocean crust)"
    k_end = kind[end]
    nf = free.sum()
    row = {}
    for kk in ("pit (thin/ocean crust)", "moat/intermontane", "rift", "arid plain", "plain"):
        v = 100 * (inland & (k_end == kk)).sum() / nf
        row[kk] = v
        tot[kk] = tot.get(kk, 0) + v
    nfr += 1
    print(f"t={t:.0f} inland {100*inland.sum()/nf:.1f}: " + ", ".join(f"{k} {v:.1f}" for k, v in row.items()), flush=True)
print(f"{rid} MEAN: " + ", ".join(f"{k} {v/nfr:.2f}" for k, v in tot.items()))
