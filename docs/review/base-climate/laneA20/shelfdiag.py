"""Earth L6: per sea box, where the overturning's and the gyres' heat goes: the inflow's share of the surface
water and its temperature, the route's transport, sea depth, the surface current, and the SST's parts (t_eq, the
gyre carry raw0 - t_eq, moc heat), against the observed annual air.
usage: shelfdiag.py ['k=v,...'] ...  (WT=<tree>)"""
import sys, os, io, contextlib
WT = os.environ.get("WT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")))
sys.path.insert(0, WT)
from planet import climate, vegetation, ocean  # planet before numpy
import numpy as np
from planet.grid import build_grid
from tools import earth_data
from tools.earth_data import cell_areas

grid = build_grid(6)
d = earth_data.earth_on_grid(grid)
w = cell_areas(grid)
lat, lon = grid.lat, grid.lon
land = earth_data.land_of(d)
sea = ~land
BOX = {"NE Atl 45-55N 25-6W": (45, 55, -25, -6), "Rockall 55-62N 20-8W": (55, 62, -20, -8),
       "North Sea 51-58 0-8E": (51, 58, 0, 8), "N North Sea 58-61": (58, 61, -2, 5),
       "Biscay 43-48": (43, 48, -6, -1), "Channel/Irish 49-55 11-3W": (49, 55, -11, -3),
       "Baltic 54-66 10-30E": (54, 66, 10, 30), "Norw coast 62-70 0-15E": (62, 70, 0, 15),
       "Barents 70-78 20-55E": (70, 78, 20, 55), "Yellow/ECS 25-41 117-128": (25, 41, 117, 128),
       "Kuroshio 30-40 130-145": (30, 40, 130, 145), "Gulf of Maine": (40, 45, -71, -65),
       "Pat shelf -52..-38": (-52, -38, -68, -56), "Bass/Tasman -45..-35": (-45, -35, 145, 160)}
cap = {}
_solve = ocean.solve


def spy_solve(*a, **k):
    r = _solve(*a, **k)
    cap["oc"] = r
    return r


ocean.solve = spy_solve
_ss = climate.sea_surface


def spy_ss(*a, **kw):
    r = _ss(*a, **kw)
    if kw.get("share") is None and "raw0" not in cap:
        cap["raw0"], cap["t_eq"] = r[0], a[2]
    if kw.get("share") is not None:
        cap["t_in"] = kw["t_in"]
    return r


climate.sea_surface = spy_ss


def wm(f, m):
    return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12))


obs = d.get("obs_t_ann", d.get("obs_temp"))
for arg in sys.argv[1:] or [""]:
    tune = {k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))}
    old = dict(climate.TUNE); climate.TUNE.update(tune)
    cap.clear()
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
    finally:
        climate.TUNE.clear(); climate.TUNE.update(old)
    oc = cap["oc"]
    depth = np.maximum(-d["elev"], 0)
    print(f"### {arg or 'default'}")
    print("box | n | depth med | t_eq | raw0-t_eq | moc heat | share | t_in-t_eq | inflow | cur m/s | sst | obs air ann | sst-obs")
    for k, (a0, a1, l0, l1) in BOX.items():
        m = sea & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
        mo = m & np.isfinite(obs) if obs is not None else m
        ob = wm(obs, mo) if obs is not None else np.nan
        print(f"{k} | {m.sum()} | {np.median(depth[m]):.0f} | {wm(cap['t_eq'], m):.1f} | {wm(cap['raw0'] - cap['t_eq'], m):+.1f} | "
              f"{wm(c['moc_heat'], m):+.1f} | {wm(oc['share'], m):.2f} | {wm(cap['t_in'] - cap['t_eq'], m):+.1f} | "
              f"{wm(c['moc_inflow'], m):.4f} | {wm(np.linalg.norm(c['current'], axis=1), m):.2f} | {wm(c['sst'], m):.1f} | "
              f"{ob:.1f} | {wm(c['sst'], m) - ob:+.1f}", flush=True)
