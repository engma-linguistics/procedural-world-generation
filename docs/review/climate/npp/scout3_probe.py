"""Scout 217 (PW-1517): the rainforest tree's (TrBE) carbon budget on Earth's observed climate, split into leaf and wood
maintenance respiration and growth respiration, for comparison with Chambers et al. 2004's measured components (Manaus).

PLANET_DATA=<main repo> uv run python docs/review/climate/npp/scout3_probe.py [--rw-x 1.0] [--eps-x 1.0] [--box wet|all]
(needs a real data/earth directory in the checkout: copy it in, never symlink.)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

WT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(WT))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import store as S, vegetation as V, world as W  # noqa: E402
from tools.earth_data import earth_on_grid, earth_clouds, cell_areas  # noqa: E402
from tools import veg_check as VC  # noqa: E402
from tools.soil_check import geology  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--rw-x", type=float, default=1.0, help="x TrBE's wood respiration rate rw")
ap.add_argument("--eps-x", type=float, default=1.0, help="x TrBE's light-use efficiency")
ap.add_argument("--rl-x", type=float, default=1.0, help="x TrBE's leaf respiration rate rl")
ap.add_argument("--box", default="wet", choices=["wet", "all"])
a = ap.parse_args()
i = V.IDX["TrBE"]
V._KP[i, 10] *= a.rw_x
V._KP[i, 0] *= a.eps_x
V._KP[i, 9] *= a.rl_x
kp = V._KP[i]
w = W.load(S.find_world("506694"))
g, L = w["grid"], w["layers"]
obs = {**earth_on_grid(g), **earth_clouds(g)}
v = VC.run(g, L, obs, geology(g, L))
s, pot, sm = v["s"], v["pot"], v["sm"]
land = v["land"] & (L["ice"] <= 0)
P, T = s["precip"], s["temp"]
if a.box == "wet":
    m = land & (T > 22) & (P > 2000) & pot["ok"][i]
else:
    m = land & (T > 18) & (P > 1500) & pot["ok"][i]
area = cell_areas(g)[m]


def wm(x):
    return float((x[m] * area).sum() / area.sum())


lai = pot["lai"][i]
gpp, npp = pot["gpp"][i], pot["npp"][i]
# the kernel's respiration terms (planet/vegetation.py::_year), month by month on the cell's temperature
rl, rw, kn = kp[9], kp[10], kp[20]
dg = np.clip(s["tg"] - kp[19], -V.ACCLIM_SPAN, V.ACCLIM_SPAN)
acc = V.RESP_ACCLIM * dg
days = np.asarray(V._DAYS, float)
q = sum(2.0 ** ((s["t"][mm] - 20.0 - acc) / 10.0) * days[mm] / 30.4 for mm in range(12))  # sum of monthly Q10 factors
leaf = (1.0 - np.exp(-kn * lai)) / kn if kn > 0 else lai
r_leaf0, r_wood0 = rl * leaf * q, rw * q
rm = gpp - npp / 0.75  # the kernel's maintenance after its CO2 supply factor (NPP = 0.75 (GPP - Rm))
fac = rm / np.maximum(r_leaf0 + r_wood0, 1e-9)
r_leaf, r_wood = r_leaf0 * fac, r_wood0 * fac
rg = gpp - rm - npp
par = s["par"].sum(0)
ra = wm(gpp - npp)
print(f"box {a.box} rl x{a.rl_x} rw x{a.rw_x} eps x{a.eps_x}: cells {m.sum()}  T {wm(T):.1f} C  P {wm(P):.0f} mm  PAR {wm(par):.0f} MJ/m2/yr  "
      f"LAI {wm(lai):.2f}  q10-sum {wm(q):.2f} (12 = a year at 20 C)  acclim shift {wm(acc):.2f} C")
print(f"GPP {wm(gpp):.0f}  NPP {wm(npp):.0f}  NPP/GPP {wm(npp) / wm(gpp):.3f}  supply factor {wm(fac):.3f}")
print(f"Rm leaf {wm(r_leaf):.0f}  Rm wood+root {wm(r_wood):.0f}  Rg {wm(rg):.0f}  Ra {ra:.0f}")
print(f"Ra shares: leaf maint {wm(r_leaf) / ra:.2f}  wood+root maint {wm(r_wood) / ra:.2f}  growth {wm(rg) / ra:.2f}")
print(f"cell NPP (mixed stand) {wm(sm['npp']):.0f}  TrBE cover {wm(v['eq']['nu'][i]):.2f}")
areas = cell_areas(g) * 6371.0 ** 2
box2 = land & (T >= 18) & (T < 32) & (P >= 2500) & (g.lat > -60)
box3 = land & (T >= 18) & (T < 32) & (P >= 1500) & (P < 2500) & (g.lat > -60)


def mean2(mm):
    return float((sm["npp"] * areas)[mm].sum() / areas[mm].sum())


print(f"land NPP {float((sm['npp'] * areas * 1e6)[land].sum() / 1e15):.1f} Pg C/yr  npp_check boxes: T18-32 P2500+ "
      f"{mean2(box2):.0f}  T18-32 P1500-2500 {mean2(box3):.0f}  forest {float(areas[land & (sm['tree'] >= 0.6)].sum() / 1e6):.1f} Mkm2")
