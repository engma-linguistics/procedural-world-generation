"""Earth L6: a text map of the annual surface current and the gyre anomaly in a lat/lon window.
usage: curmap.py LAT0 LAT1 LON0 LON1 [k=v,...]   (lon in 0..360; each column 2.5 deg, each row 2.5 deg)
Per bin: the poleward current (dm/s, sea mean) / the gyre anomaly raw0 - t_eq (C); L land, W wall land."""
import sys, os
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, WT)
from planet import climate, vegetation
import numpy as np
from planet.grid import build_grid
from tools import earth_data
grid = build_grid(6); d = earth_data.earth_on_grid(grid)
lat, lon = grid.lat, grid.lon; land = earth_data.land_of(d)
a0, a1, l0, l1 = (float(x) for x in sys.argv[1:5])
arg = sys.argv[5] if len(sys.argv) > 5 else ""
climate.TUNE.update({k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))})
cap = {}
orig = climate.sea_surface
def spy(*a, **kw):
    r = orig(*a, **kw)
    if kw.get("share") is None and a[0].n == grid.n:
        cap["raw0"] = r[0]; cap["t_eq"] = a[2]; cap["cur"] = kw["cur"]
    return r
climate.sea_surface = spy
_st = climate._stommel
def spy_st(F, *a):
    cap["solve"] = a[3]
    return _st(F, *a)
climate._stommel = spy_st
vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))
G = climate._geom(grid)
cur = cap["cur"]; pole = (cur * G["north"]).sum(1) * np.sign(lat); east = (cur * G["east"]).sum(1)
gy = cap["raw0"] - cap["t_eq"]; wall = ~cap["solve"]
lon360 = np.where(lon < 0, lon + 360, lon)
cols = np.arange(l0, l1, 2.5)
print("lat \\ lon " + "".join(f"{c:>10.1f}" for c in cols))
for a in np.arange(a1, a0, -2.5):
    row = []
    for c in cols:
        m = (lat < a) & (lat >= a - 2.5) & (lon360 >= c) & (lon360 < c + 2.5)
        s = m & ~land
        if not m.any(): row.append(" " * 10); continue
        if s.sum() < 0.5 * m.sum():
            row.append(f"{'W' if (m & wall).any() else 'L':>10}"); continue
        row.append(f"{10 * pole[s].mean():+4.0f}{10 * east[s].mean():+3.0f}/{gy[s].mean():+2.0f}".rjust(10))
    print(f"{a - 2.5:6.1f}    " + "".join(row))
print("cell: poleward dm/s, east dm/s / gyre anomaly C")
