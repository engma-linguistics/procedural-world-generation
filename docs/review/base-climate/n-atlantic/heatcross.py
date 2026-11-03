"""Lane 142 (PW-1381): the overturning inflow's heat transport across latitudes, Earth L6 (the overturning is
solved on moc_level). For each route edge p -> i crossing a latitude northward, Q x rho c x (t_in - T_sink), with
T_sink the Q-weighted inflow temperature where it sinks. Against RAPID 26.5 N (1.33 PW, Johns et al. 2011) and
OSNAP ~53-60 N (0.45 PW, Lozier et al. 2019). Usage: heatcross.py [k=v ...] (TUNE overrides)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import numpy as np
from planet import climate, ocean
from planet.grid import build_grid
from tools import earth_data

for a in sys.argv[1:]:
    k, v = a.split("=")
    climate.TUNE[k] = float(v)
rec = {}
orig_route, orig_along = ocean._route, ocean._along
def spy_route(order, par, sinking):
    rec["sinking"], rec["par"], rec["order"] = sinking.copy(), par.copy(), order.copy()
    return orig_route(order, par, sinking)
def spy_along(order, par, Q, tgt, x0, rate, dil):
    out = orig_along(order, par, Q, tgt, x0, rate, dil)
    if "t_in" not in rec or rec.get("_n", 0) % 2 == 0:
        rec["t_in"], rec["Q"] = out.copy(), Q.copy()
    rec["_n"] = rec.get("_n", 0) + 1
    return out
ocean._route, ocean._along = spy_route, spy_along
g = build_grid(6)
d = earth_data.earth_on_grid(g)
c = climate.compute(g, d["elev"].astype(float), 0.0, 23.4, d["ice"].astype(float))
gc = build_grid(int(climate.TUNE["moc_level"]))
lat, lon = gc.lat, gc.lon
par, Q, t, sk = rec["par"], rec["Q"], rec["t_in"], rec["sinking"]
atl = (lon > -100) & (lon < 30)
sink_cells = (sk > 1e-3) & atl & (lat > 0)
T_s = float((sk * t)[sink_cells].sum() / sk[sink_cells].sum())
print(f"N Atlantic sinking {sk[sink_cells].sum():.2f} Sv, its water {T_s:.2f} C")
i = np.flatnonzero((par >= 0) & atl)
p = par[i]
for L in (26.5, 35, 45, 55, 60, 65):
    cr = (lat[p] < L) & (lat[i] >= L)
    pw = float((Q[i][cr] * climate.RHO_C_SEA * (t[i][cr] - T_s)).sum() / 1e15)
    sv = float(Q[i][cr].sum() / 1e6)
    tm = float((Q[i][cr] * t[i][cr]).sum() / max(Q[i][cr].sum(), 1e-9))
    print(f"{L:5.1f} N: inflow {sv:6.2f} Sv at {tm:5.2f} C -> {pw:.3f} PW above the sinking water")
