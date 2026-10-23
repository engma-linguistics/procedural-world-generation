"""Earth L6: where the summer winds come from. Per box (sea cells), each hemisphere's summer: the
final wind speed, the belts alone, the belts + the 900 km land-sea part, + the big part; and per
hemisphere and season the zonal-mean meridional temperature gradient (C/1000 km) over 30-65 deg
from the first-guess t_sl and from the finished season temperatures.  usage: wdiag.py 'k=v,...'"""
import sys, os
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, WT)
import numpy as np
from planet import climate, vegetation
from planet.grid import build_grid
from tools import earth_data
from tools.earth_data import cell_areas
grid = build_grid(int(os.environ.get("LV", "6"))); d = earth_data.earth_on_grid(grid); w = cell_areas(grid)
lat, lon = grid.lat, grid.lon; land = earth_data.land_of(d)
cap = {"mw": [], "air": None}
_om = climate.monsoon_wind
def spy_mw(g, t_sl, shift, *a, **kw):
    r = _om(g, t_sl, shift, *a, **kw)
    if g.n == grid.n: cap["mw"].append((t_sl.copy(), shift, a, kw))
    return r
climate.monsoon_wind = spy_mw
_oa = climate._air_temps
def spy_air(*a, **kw):
    if kw["grid"].n == grid.n: cap["air"] = (kw["v_sum"], kw["v_win"])
    return _oa(*a, **kw)
climate._air_temps = spy_air
arg = sys.argv[1] if len(sys.argv) > 1 else ""
climate.TUNE.update({k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))})
c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
U = climate.U_REF
sea = ~land
B = {"NE Atl 45-55N": (45, 55, -25, -6), "Norw Sea 60-70": (60, 70, -5, 15), "G Alaska": (52, 60, -160, -135),
     "NE Pac 40-50": (40, 50, -150, -125), "NW Pac 35-45": (35, 45, 145, 175), "N Pac 40-50 mid": (40, 50, 170, 220),
     "S Atl off Pat": (-52, -40, -64, -56), "Tasman": (-45, -35, 150, 165), "SE Pac off Chile": (-52, -38, -85, -76),
     "Agulhas": (-40, -30, 15, 35), "S Indian 40-50": (-50, -40, 40, 100), "S Ocean 50-60": (-60, -50, -180, 180),
     "off NZ W 40-47S": (-47, -40, 160, 166)}
lon360 = np.where(lon < 0, lon + 360, lon)
def wm(f, m): return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12)) if m.any() else float("nan")
def boxm(k):
    a0, a1, l0, l1 = B[k]
    L = lon360 if l1 > 180 else lon
    return sea & (lat >= a0) & (lat < a1) & (L >= l0) & (L < l1)
# the last two monsoon_wind calls are the final (front-shifted) ones: jul, jan
(tj, sj, aj, kj), (tn, sn, an, kn) = cap["mw"][-2:]
def parts(t_sl, shift, a, kw):
    a = list(a) + [None] * 6
    front, belt, col = a[3], (1.0 if a[4] is None else a[4]), a[5]
    ex = [] if a[4] is None else [belt, col]  # (main's winds have no belt / column)
    belts = climate.wind(grid, shift, front, *ex[:1])
    small = _om(grid, t_sl, shift, a[0], 0.0, a[2], front, *ex)[0]
    full = _om(grid, t_sl, shift, a[0], a[1], a[2], front, *ex)[0]
    if isinstance(belt, np.ndarray):
        print(f"  belt N {belt[lat >= 0].mean():.2f} S {belt[lat < 0].mean():.2f}")
    return belts, small, full, climate.wind(grid, shift, None, *ex[:1])
pj, pn = parts(tj, sj, aj, kj), parts(tn, sn, an, kn)
vs, vw = cap["air"]
print("box (summer): final | belts | belts+900km | belts+900+big   (m/s)   winter final | belts without front_shift")
for k in B:
    m = boxm(k)
    p = pj if B[k][0] >= 0 else pn
    print(f"{k:>17}: {wm(climate.speed(vs) * U, m):4.1f} | {wm(climate.speed(p[0]) * U, m):4.1f} | "
          f"{wm(climate.speed(p[1]) * U, m):4.1f} | {wm(climate.speed(p[2]) * U, m):4.1f}    {wm(climate.speed(vw) * U, m):4.1f}"
          f" | {wm(climate.speed(p[3]) * U, m):4.1f}")
def grad_band(t, hemi, a0=30, a1=65):
    width = 3.0; nb = int(180 // width)
    bins = np.clip(((lat + 90) // width).astype(int), 0, nb - 1)
    zm = np.bincount(bins, t, nb) / np.maximum(np.bincount(bins, minlength=nb), 1)
    lat_c = -90 + width * (np.arange(nb) + 0.5)
    g = np.gradient(zm) / (width * 111.2) * 1000.0
    sel = (np.abs(lat_c) >= a0) & (np.abs(lat_c) <= a1) & ((lat_c > 0) == (hemi > 0))
    return float(-np.sign(hemi) * np.average(g[sel], weights=np.cos(np.radians(lat_c[sel]))))
surf = np.maximum(d["elev"], 0) + d["ice"]
t_s = climate.season_temps(grid, surf, c["t_warm"], c["t_cold"], climate.TUNE["hk"])
print("zonal-mean poleward cooling 30-65 deg, C/1000 km: [first-guess t_sl] [finished season temps]")
for nm, hemi in (("N", 1), ("S", -1)):
    print(f"  {nm}: jul {grad_band(tj, hemi):.2f} jan {grad_band(tn, hemi):.2f} | "
          f"jul {grad_band(t_s[0], hemi):.2f} jan {grad_band(t_s[1], hemi):.2f}")
print("band (sea) summer / winter speed:")
for a0 in range(-70, 75, 10):
    m = sea & (lat >= a0) & (lat < a0 + 10)
    print(f"  {a0:>4}..{a0+10:<4}: {wm(climate.speed(vs) * U, m):4.1f} {wm(climate.speed(vw) * U, m):4.1f}")
for nm, a0, a1 in (("N 40-55", 40, 55), ("S 40-55", -55, -40)):
    m = sea & (lat >= a0) & (lat < a1)
    print(f"  {nm} summer {wm(climate.speed(vs) * U, m):4.1f} winter {wm(climate.speed(vw) * U, m):4.1f}")
