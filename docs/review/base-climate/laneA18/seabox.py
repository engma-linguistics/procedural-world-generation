"""Earth L6: per sea box, the parts of the sea's warmest month: annual SST, the summer / winter half-swings
_sea_half gives (its own and the land part), land_air, step 2's chill, and t_warm vs observed.
usage: seabox.py ['k=v,...'] ...   (WT=<tree> to probe another tree; step-1 trees return one half)"""
import sys, os, io, contextlib
WT = os.environ.get("WT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")))
sys.path.insert(0, WT)
from planet import climate, vegetation  # planet before numpy
import numpy as np
from planet.grid import build_grid
from tools import earth_data
from tools.earth_data import cell_areas

grid = build_grid(6)
d = earth_data.earth_on_grid(grid)
w = cell_areas(grid)
lat, lon = grid.lat, grid.lon
land = earth_data.land_of(d)
seam = ~land & np.isfinite(d["obs_t_warm"])
BOX = {"NE Atl 45-55N": (45, 55, -25, -6), "Bay Biscay-N Sea": (43, 58, -6, 8), "North Sea 51-58 0-8E": (51, 58, 0, 8),
       "Biscay 43-48": (43, 48, -6, -1), "W Atl 35-45N": (35, 45, -72, -55), "E China Sea": (25, 33, 122, 130),
       "Gulf Mex": (22, 29, -95, -82), "Labrador Sea": (52, 62, -60, -45), "S Atl off Pat": (-52, -40, -64, -56),
       "Tasman": (-45, -35, 150, 165), "Agulhas": (-40, -30, 15, 35)}
cap = {}
orig = climate._sea_half


def spy(*a, **k):
    r = orig(*a, **k)
    cap.setdefault("land_air", a[3])
    cap.setdefault("halves", r)
    return r


climate._sea_half = spy
_ss = climate.sea_surface


def spy_ss(*a, **kw):
    r = _ss(*a, **kw)
    if kw.get("share") is None and "raw0" not in cap:
        cap["raw0"], cap["t_eq"] = r[0], a[2]
    return r


climate.sea_surface = spy_ss


def wm(f, m):
    return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12))


for arg in sys.argv[1:] or [""]:
    tune = {k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))}
    old = dict(climate.TUNE); climate.TUNE.update(tune)
    cap.clear()
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
    finally:
        climate.TUNE.clear(); climate.TUNE.update(old)
    hs = cap["halves"]
    s_h, w_h = (hs, hs) if not isinstance(hs, tuple) else hs
    hk = climate.TUNE["hk"]
    chill = 0.5 * hk * (w_h - s_h)
    print(f"### {arg or 'default'}  (first-call halves; hk {hk})")
    print("obs keys:", [k for k in d if "sst" in k or "sea" in k])
    print("box | t_eq | raw0-t_eq | moc heat | upwelling | cur m/s | sst | half s / w | chill | land_air | t_warm mod/obs (bias) | t_cold mod/obs | half-swing mod/obs")
    for k, (a0, a1, l0, l1) in BOX.items():
        m = seam & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
        print(f"{k} | {wm(cap['t_eq'], m):.1f} | {wm(cap['raw0'] - cap['t_eq'], m):+.1f} | {wm(c['moc_heat'], m):+.1f} | "
              f"{wm(c['upwelling'], m):.1f} | {wm(np.linalg.norm(c['current'], axis=1), m):.2f} | {wm(c['sst'], m):.1f} | {wm(s_h, m):.1f} / {wm(w_h, m):.1f} | {wm(chill, m):.1f} | "
              f"{wm(cap['land_air'], m):.2f} | {wm(c['t_warm'], m):.1f}/{wm(d['obs_t_warm'], m):.1f} "
              f"({wm(c['t_warm'] - d['obs_t_warm'], m):+.1f}) | {wm(c['t_cold'], m):.1f}/{wm(d['obs_t_cold'], m):.1f} | "
              f"{wm(c['t_warm'] - c['t_cold'], m) / 2:.1f}/{wm(d['obs_t_warm'] - d['obs_t_cold'], m) / 2:.1f}", flush=True)
