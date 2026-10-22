"""The summer AET/PET the temperature curve stands for: Earth L6, the climate without the energy split, ice-free land
20-60 deg (as cloud_ref); and per box, with LE/SWg."""
import sys
sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-abbf08ba762366c44")
import numpy as np
from planet import climate, vegetation
from planet.grid import build_grid
from tools import earth_data
from tools.earth_data import cell_areas
if "split" not in sys.argv:
    climate._summer_split = lambda lat, *a, **k: np.zeros(len(lat))
grid = build_grid(6)
d = earth_data.earth_on_grid(grid)
w = cell_areas(grid)
lat, lon = grid.lat, grid.lon
land = earth_data.land_of(d)
bare = land & (d["ice"] <= 0)
north = lat >= 0
c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
sm = np.where(north, 0, 1)
i = np.arange(grid.n)
r = c["aet_half"][sm, i] / np.maximum(c["pet_half"][sm, i], 1e-9)
B = {"SE USA": (30, 37, -95, -77), "Great Lakes": (40, 50, -95, -75), "Labrador": (52, 62, -80, -56),
     "HB lowlands": (50, 60, -95, -80), "Keewatin": (58, 68, -105, -85), "Alaska": (60, 70, -165, -140),
     "W Europe": (45, 55, -5, 10), "Sahara": (18, 30, -10, 30), "Patagonia": (-55, -40, -76, -65)}


def wm(f, m):
    return float((f[m] * w[m]).sum() / w[m].sum())


for k, (a0, a1, l0, l1) in B.items():
    m = bare & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
    print(f"{k:12s} AET/PET {wm(r, m):.2f}  PETs {wm(c['pet_half'][sm, i], m):5.0f}  AETs {wm(c['aet_half'][sm, i], m):5.0f}  Tw {wm(c['t_warm'], m):.1f}")
for a0, a1 in ((20, 60), (0, 70)):
    m = bare & (np.abs(lat) >= a0) & (np.abs(lat) <= a1)
    print(f"land {a0}-{a1}: AET/PET {wm(r, m):.3f}  AET {wm(c['aet_half'][sm, i], m):.0f}  PET {wm(c['pet_half'][sm, i], m):.0f}")
