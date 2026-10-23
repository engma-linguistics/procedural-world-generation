"""Earth L6, the SH western boundary currents (PW-594): per box (sea), the SST's parts (t_eq, gyre+upwelling
anomaly raw0 - t_eq, moc heat, sst), annual / warmest-month sea air vs NCEP, the current's speed and poleward part,
the summer wind; and a profile along each SH east coast (sea cells within 2 hops of land) by 2.5 deg of latitude.
usage: wbc.py 'k=v,...'  (TUNE overrides)"""
import sys, os
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, WT)
from planet import climate, vegetation  # planet before numpy (BLAS caps)
import numpy as np
from planet.grid import build_grid
from tools import earth_data
from tools.earth_data import cell_areas
grid = build_grid(int(os.environ.get("LV", "6"))); d = earth_data.earth_on_grid(grid); w = cell_areas(grid)
lat, lon = grid.lat, grid.lon; land = earth_data.land_of(d)
cap = {}
orig = climate.sea_surface
def spy(*a, **kw):
    r = orig(*a, **kw)
    if kw.get("share") is None and a[0].n == grid.n:
        cap["raw0"] = r[0]; cap["t_eq"] = a[2]; cap["cur"] = kw["cur"]
    return r
climate.sea_surface = spy
_oa = climate._air_temps
def spy_air(*a, **kw):
    if kw["grid"].n == grid.n: cap["vs"] = kw["v_sum"]
    return _oa(*a, **kw)
climate._air_temps = spy_air
arg = sys.argv[1] if len(sys.argv) > 1 else ""
climate.TUNE.update({k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))})
c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
G = climate._geom(grid)
sea = ~land & np.isfinite(d["obs_temp"])
def wm(f, m): return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12)) if m.any() else float("nan")
gy = cap["raw0"] - cap["t_eq"]; cur = cap["cur"]
spd = climate.speed(cur); pole = (cur * G["north"]).sum(1) * np.sign(lat)  # poleward part
T, O = c["temp"], d["obs_temp"]
ws = climate.speed(cap["vs"]) * climate.U_REF
lon360 = np.where(lon < 0, lon + 360, lon)
B = {"Tasman 35-45S": (-45, -35, 150, 165), "Tasman 30-35S": (-35, -30, 150, 160), "Agulhas 30-40S": (-40, -30, 15, 35),
     "Agulhas Ret 38-45S": (-45, -38, 15, 45), "Brazil 25-35S": (-35, -25, -55, -40), "S Atl off Pat": (-52, -40, -64, -56),
     "SE Pac off Chile": (-52, -38, -85, -76), "S Indian 40-50": (-50, -40, 40, 100), "Gulf Str 35-45N": (35, 45, -72, -55),
     "Kuroshio 30-40N": (30, 40, 130, 150), "NE Atl 45-55N": (45, 55, -25, -6), "NE Pac 40-50": (40, 50, -150, -125)}
print("box: t_eq gyre moc sst | air mod obs bias | Tw mod obs bias | cur m/s poleward | summer wind m/s")
for k, (a0, a1, l0, l1) in B.items():
    L = lon360 if l1 > 180 else lon
    m = sea & (lat >= a0) & (lat < a1) & (L >= l0) & (L < l1)
    print(f"{k:>18}: {wm(cap['t_eq'], m):5.1f}{wm(gy, m):+5.1f}{wm(c['moc_heat'], m):+5.1f}{wm(c['sst'], m):5.1f} |"
          f" {wm(T, m):5.1f}{wm(O, m):5.1f}{wm(T - O, m):+5.1f} | {wm(c['t_warm'], m):5.1f}{wm(d['obs_t_warm'], m):5.1f}"
          f"{wm(c['t_warm'] - d['obs_t_warm'], m):+5.1f} | {wm(spd, m):4.2f} {wm(pole, m):+5.2f} | {wm(ws, m):4.1f}")
coast = np.zeros(grid.n, bool)
for _ in range(2):
    nb = np.add.reduceat((land | coast)[grid.nbr_idx].astype(int), grid.nbr_off[:-1]) > 0
    coast = coast | (~land & nb)
P = {"E Australia": (150, 160), "SE Africa": (25, 40), "E S America": (-60, -38)}
print("\ncoastal profile (sea within 2 hops of land): lat | gyre  sst  air-obs  Tw-obs | cur poleward")
for k, (l0, l1) in P.items():
    print(k)
    for a0 in np.arange(-25, -50, -2.5):
        m = coast & sea & (lat < a0) & (lat >= a0 - 2.5) & (lon >= l0) & (lon < l1)
        if m.sum() < 1: continue
        print(f"  {a0 - 2.5:6.1f}..{a0:6.1f}: {wm(gy, m):+5.1f} {wm(c['sst'], m):5.1f} {wm(T - O, m):+5.1f} "
              f"{wm(c['t_warm'] - d['obs_t_warm'], m):+5.1f} | {wm(spd, m):4.2f} {wm(pole, m):+5.2f}  n={m.sum()}")
