"""Earth L6: what sets the SH gyres' extent. The annual wind's zonal-mean east part and the zonal-mean curl
forcing F by latitude (sea), per basin; which land is a wall for the gyres near NZ / Tasmania; psi along the
Australian east coast and at NZ."""
import sys, os
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, WT)
from planet import climate, vegetation
import numpy as np
from planet.grid import build_grid
from planet.geo import R_KM
from tools import earth_data
from tools.earth_data import cell_areas
grid = build_grid(6); d = earth_data.earth_on_grid(grid); w = cell_areas(grid)
lat, lon = grid.lat, grid.lon; land = earth_data.land_of(d)
cap = {}
orig = climate.currents
def spy(g, ocean, wind_v, tune=None):
    if g.n == grid.n: cap["v"] = wind_v.copy(); cap["ocean"] = ocean.copy()
    return orig(g, ocean, wind_v, tune)
climate.currents = spy
_st = climate._stommel
def spy_st(F, *a):
    psi = _st(F, *a)
    cap["F"], cap["psi"], cap["solve"] = F, psi, a[3]
    return psi
climate._stommel = spy_st
c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
G = climate._geom(grid)
ocean = cap["ocean"]
ue = (cap["v"] * G["east"]).sum(1) * climate.U_REF
F, psi, solve = cap["F"], cap["psi"], cap["solve"]
lon360 = np.where(lon < 0, lon + 360, lon)
def wm(f, m): return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12)) if m.any() else float("nan")
basins = {"all": (0, 360), "S Pac 160E-70W": (160, 290), "S Atl 60W-20E": (300, 380), "Indian 20-115E": (20, 115)}
print("lat  | zonal-mean annual u (m/s) and curl forcing F (x1e3) on sea, per basin")
for a0 in range(-20, -72, -4):
    m0 = ocean & (lat < a0) & (lat >= a0 - 4)
    row = []
    for k, (l0, l1) in basins.items():
        L = np.where(lon360 < l0, lon360 + 360, lon360) if l1 > 360 else lon360
        m = m0 & (L >= l0) & (L < l1)
        row.append(f"{k}: u {wm(ue, m):+5.1f} F {1e3 * wm(F, m):+6.2f}")
    print(f"{a0 - 4:4d}..{a0:4d} | " + " | ".join(row))
for a0 in range(20, 72, 4):
    m = ocean & (lat >= a0) & (lat < a0 + 4)
    print(f"{a0:4d}..{a0 + 4:4d} | all: u {wm(ue, m):+5.1f} F {1e3 * wm(F, m):+6.2f}")
# walls near NZ / Tasmania
lab, nl = climate._components(grid, ~ocean)
sizes = np.bincount(lab[lab >= 0], minlength=max(nl, 1)) * (4 * np.pi * R_KM**2 / grid.n)
for name, (a0, a1, l0, l1) in {"NZ": (-48, -34, 165, 179), "Tasmania": (-44, -40, 144, 149)}.items():
    m = ~ocean & (lat >= a0) & (lat < a1) & (lon360 >= l0) & (lon360 < l1)
    ids = np.unique(lab[m])
    print(name, [(int(i), round(float(sizes[i]))) for i in ids], "wall cells:", int((m & ~solve).sum()), "of", int(m.sum()))
print("psi (x1e3) on sea along 150-157E by lat; and at 170-180E")
for a0 in range(-24, -50, -3):
    m1 = ocean & (lat < a0) & (lat >= a0 - 3) & (lon360 >= 150) & (lon360 < 157)
    m2 = ocean & (lat < a0) & (lat >= a0 - 3) & (lon360 >= 180) & (lon360 < 200)
    m3 = ocean & (lat < a0) & (lat >= a0 - 3) & (lon360 >= 230) & (lon360 < 260)
    print(f"  {a0 - 3}..{a0}: W Tasman {1e3 * wm(psi, m1):+7.2f}  E of NZ {1e3 * wm(psi, m2):+7.2f}  mid-Pac {1e3 * wm(psi, m3):+7.2f}")
