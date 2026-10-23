"""Earth L6: text maps around NW Europe (2 deg bins) of the SST's parts: sst - obs annual air, moc heat, the
inflow's share, raw0 - t_eq (the gyre carry), and the sea depth. usage: eumap.py ['k=v,...'] [region]
region: eu (default: 40-72N 30W-35E), asia (25-45N 115-145E)"""
import sys, os, io, contextlib
WT = os.environ.get("WT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")))
sys.path.insert(0, WT)
from planet import climate, vegetation, ocean  # planet before numpy
import numpy as np
from planet.grid import build_grid
from tools import earth_data

grid = build_grid(6)
d = earth_data.earth_on_grid(grid)
lat, lon = grid.lat, grid.lon
sea = ~earth_data.land_of(d)
cap = {}
_solve = ocean.solve
ocean.solve = lambda *a, **k: cap.setdefault("oc", _solve(*a, **k))
_ss = climate.sea_surface


def spy_ss(*a, **kw):
    r = _ss(*a, **kw)
    if kw.get("share") is None and "raw0" not in cap:
        cap["raw0"], cap["t_eq"] = r[0], a[2]
    return r


climate.sea_surface = spy_ss
arg = sys.argv[1] if len(sys.argv) > 1 else ""
reg = sys.argv[2] if len(sys.argv) > 2 else "eu"
R = {"eu": (40, 72, -30, 36), "asia": (24, 46, 114, 146)}[reg]
tune = {k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))}
climate.TUNE.update(tune)
with contextlib.redirect_stderr(io.StringIO()):
    c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
F = {"sst - obs air": c["sst"] - d["obs_temp"], "moc heat": c["moc_heat"], "share x10": 10 * cap["oc"]["share"],
     "raw0 - t_eq": cap["raw0"] - cap["t_eq"], "depth/100 m": np.maximum(-d["elev"], 0) / 100}
for name, f in F.items():
    print(f"## {name} ({arg or 'default'}); rows lat (N first), cols lon {R[2]}..{R[3]} by 3 deg; '.' land")
    for a in range(R[1], R[0], -2):
        row = []
        for o in range(R[2], R[3], 3):
            m = (lat >= a - 2) & (lat < a) & (lon >= o) & (lon < o + 3)
            ms = m & sea & np.isfinite(f)
            row.append("   ." if ms.sum() < max(1, m.sum() // 2) else f"{np.mean(f[ms]):4.0f}")
        print(f"{a:3d} " + "".join(row))
