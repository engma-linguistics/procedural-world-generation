"""PW-680 option C: the bed's true lag (the code's own discrete relaxation replayed on the per-frame grounded load)
against the test's tolerance term, on sim4 made 8 C colder. usage: lagcheck.py PACE (1.0 = main, 0.8 = PW-636)"""
import math
import os
import sys

os.environ.setdefault("NUMBA_NUM_THREADS", "4")
sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "tests")]
import numpy as np

from planet import vegetation as V

pace = float(sys.argv[1])
if pace != 1.0:
    def gw(plants_from, end):
        span = max(end - plants_from, 1e-6)
        d = end - max(16.0, 0.05 * span)
        s = max(d - plants_from, 0.0)
        return [(plants_from + 0.6 * f * s, min(plants_from + 1.3 * f * s, d)) if f > 0 else (plants_from, plants_from)
                for f in (pace * g[2] for g in V.GROUPS)]
    V.group_windows = gw
from helpers import run_sim

from planet import timezoom as Z
from planet.tectonics.isostasy import ice_load
from planet.timezoom import params as P

src = Z.source_from_sim(run_sim())
src["dT"] -= 8.0
EV = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
r = Z.simulate(src, kyr=40, step=0.5, every=EV)
s, g, p = r["state"], src["grid"], Z.TZParams()
H0 = np.maximum(np.asarray(src["ice"], float), 0.0)
flt = 1 - P.RHO_I / P.RHO_W
H = np.where(s["bed"] + s["H"] > s["sl"] + flt * s["H"], s["H"], 0.0)
want = src["elev"] + ice_load(g, H0, p.iso_ratio, p.flex_km) - ice_load(g, H, p.iso_ratio, p.flex_km)
grew = H > H0 + 500
bed = s["bed"] + s["cut"] - s["till"] - s["rock_iso"]
t = [f["t"] for f in r["frames"]]
v = [f["stats"]["ice_volume_mkm3"] for f in r["frames"]]
# the test's own tolerance (on 2 kyr frames, as the test runs it)
t2, v2 = t[::int(round(2.0 / EV))], v[::int(round(2.0 / EV))]
lag = (v2[-1] - np.interp(t2[-1] - p.iso_tau, t2, v2)) / max(v2[-1] - v2[0], 1e-9)
dip = np.median((H - H0)[grew]) * p.iso_ratio
tol = (0.05 + max(lag, 0.0)) * dip + 20
err = np.abs(bed - want)[grew]
# replay: e_n = (e_{n-1} + dL_n)(1 - a), L = load of the frame's grounded ice (frame n = the state after step n-1)
ice = np.asarray(r["data"]["ice"], float)
a = 1 - math.exp(-EV / p.iso_tau)  # (approximate when EV > the 0.5 kyr step)
L = [ice_load(g, ice[k], p.iso_ratio, p.flex_km) for k in range(len(ice))]
e = np.zeros(g.n)
for k in range(1, len(ice)):
    e = (e + (L[k] - L[k - 1])) * (1 - a)
ex = e[grew]
k3 = int(round(p.iso_tau / EV))
prox = (L[-1] - L[-1 - k3])[grew]
grown = (L[-1] - L[0])[grew]
print(f"pace {pace}: frames {len(t)}, grew {grew.sum()} cells; dip median {dip:.1f} m; global lag share {lag:.3f}")
print(f"  median |bed-want| {np.median(err):.1f}  tol {tol:.1f}  (5% {0.05 * dip:.1f} + lag {max(lag, 0) * dip:.1f} + 20)")
print(f"  replayed lag on grew cells: median {np.median(ex):.1f}, mean {ex.mean():.1f}")
print(f"  per-cell load grown over the last iso_tau: median {np.median(prox):.1f}; its share of the cell's grown load:"
      f" median {np.median(prox / np.maximum(grown, 1e-9)):.3f}")
print(f"  bed - want on grew cells: median {np.median((bed - want)[grew]):.1f}; minus the replayed lag:"
      f" median |.| {np.median(np.abs((bed - want)[grew] - ex)):.1f}")
print(f"  ice volume: t0 {v[0]:.3f}, t-3 kyr {v[-1 - k3]:.3f}, end {v[-1]:.3f}")
