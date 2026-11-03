"""Lane 150 (PW-1411): the overturning on its own grid (moc_level) around the Nordic seas, Earth L6.
Spies on the last ocean.overturning call and prints, per coarse cell in 55-82 N, 45 W-25 E: the winter density at
moc_z minus the deep water's, the sinking (Sv), whether the inflow is shut out (strait lid / ice lid), the transport
through the cell (Sv), the inflow's temperature and the latitude's t_eq. Usage: nordmap.py [k=v ...]"""
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
orig_ov, orig_route, orig_along = ocean.overturning, ocean._route, ocean._along


def spy_ov(cg, sea, rho_w, rho_a, sst, sss, t_eq, fresh, cur, tune, lid=None, depth=None, ice_lid=None):
    out = orig_ov(cg, sea, rho_w, rho_a, sst, sss, t_eq, fresh, cur, tune, lid, depth, ice_lid)
    rec.update(cg=cg, sea=sea, rho_w=rho_w, sst=sst, sss=sss, t_eq=t_eq, lid=lid, depth=depth, ice_lid=ice_lid,
               out=out)
    return out


def spy_route(order, par, sink):
    T = orig_route(order, par, sink)
    rec["par"], rec["Tr"] = par.copy(), T.copy()
    return T


def spy_along(order, par, Q, tgt, x0, rate, dil):
    x = orig_along(order, par, Q, tgt, x0, rate, dil)
    if not dil.any():
        rec["tin_route"] = x.copy()
    return x


ocean.overturning, ocean._route, ocean._along = spy_ov, spy_route, spy_along
g = build_grid(6)
d = earth_data.earth_on_grid(g)
c = climate.compute(g, d["elev"].astype(float), 0.0, 23.4, d["ice"].astype(float))
cg = rec["cg"]
o = rec["out"]
lat, lon = cg.lat, cg.lon
print("sites", o["sites"])
m = rec["sea"] & (lat > 55) & (lat < 82) & (lon > -45) & (lon < 25)
il = rec["ice_lid"] if rec["ice_lid"] is not None else np.zeros(cg.n, bool)
print(" lat   lon | depth | rho_w-deep | sss  | sst  | sink Sv | lid ice | Tr Sv | t_in | t_eq | from")
for i in np.flatnonzero(m)[np.lexsort((lon[m], -lat[m]))]:
    p = rec["par"][i]
    fr = f"{lat[p]:.0f},{lon[p]:.0f}" if p >= 0 else "-"
    print(f"{lat[i]:5.1f} {lon[i]:6.1f} | {rec['depth'][i]:5.0f} | {rec['rho_w'][i] - o['rho_deep'][i]:+6.3f} | "
          f"{rec['sss'][i]:.2f} | {rec['sst'][i]:5.2f} | {o['sinking'][i]:6.2f} | {int(rec['lid'][i])}   "
          f"{int(il[i])}   | {rec['Tr'][i]:5.2f} | {rec['tin_route'][i]:5.2f} | {rec['t_eq'][i]:5.2f} | {fr}")

# Summary: where the North Atlantic's sinking sits, and the inflow across the Greenland-Scotland ridge (rough
# line: north of 66 N west of 14 W, of 63.5 N from 14 to 8 W, of 62 N east of 8 W) and its heat above the water
# that sinks north of it (Tsubouchi et al. 2021: 305 +- 26 TW into the Nordic seas and Arctic).
sea = rec["sea"]
sk, Tr, par, tin = o["sinking"], rec["Tr"], rec["par"], rec["tin_route"]
atl = (lon > -100) & (lon < 60) & (lat > 40)
nord = sea & atl & (((lat >= 66) & (lon > -40)) | ((lat >= 63.5) & (lon > -14)) | ((lat >= 62) & (lon > -8)))
lab = sea & atl & ~nord & (lon < -45)
irm = sea & atl & ~nord & (lon >= -45)
for nm, r in (("Labrador (W of 45 W)", lab), ("Irminger / Iceland basin", irm), ("Nordic seas, Barents, Arctic", nord)):
    print(f"sinking {nm}: {sk[r].sum():.2f} Sv")
T_n = float((sk * tin)[nord].sum() / max(sk[nord].sum(), 1e-9))
i = np.flatnonzero(nord & (par >= 0))
i = i[~nord[par[i]]]
Qx = Tr[i]
print(f"across the ridge: {Qx.sum():.2f} Sv at {(Qx * tin[i]).sum() / max(Qx.sum(), 1e-9):.2f} C; the water sinking "
      f"north of it {T_n:.2f} C -> {(Qx * 1e6 * climate.RHO_C_SEA * (tin[i] - T_n)).sum() / 1e12:.0f} TW")
for k in i[np.argsort(-Qx)][:6]:
    print(f"  {lat[par[k]]:.1f},{lon[par[k]]:.1f} -> {lat[k]:.1f},{lon[k]:.1f}: {Tr[k]:.2f} Sv at {tin[k]:.2f} C")
