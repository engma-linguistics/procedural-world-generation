"""python frames.py <code dir> seed t0 t1 every [level]: biggest lake, lakes, inland per frame
(the frame's own rivers and lakes, as output.water_now routes them)."""
import sys
sys.path.insert(0, sys.argv[1])
import planet  # noqa
import inspect
import numpy as np
from planet import hydrology
from planet.geo import R_KM
from planet.grid import build_grid
from planet.tectonics import Params, Simulation

seed, t0, t1, ev = int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
lv = int(sys.argv[6]) if len(sys.argv) > 6 else 6
g = build_grid(lv)
sim = Simulation(g, seed, Params(flora_end=500.0), 2.0)
ck = 4 * np.pi * R_KM ** 2 / g.n / 1e6
has_valley = "valley" in inspect.signature(hydrology.rivers_and_lakes).parameters
t = t0
while t <= t1 + 1e-6:
    sim.run(t)
    bed = sim.bed()
    c = {"runoff": sim.runoff, "aet": sim.aet, "lake_evap": sim.lake_evap}
    kw = {}
    if has_valley:
        kw["valley"] = sim.valley()
    flow, down, lk = hydrology.rivers_and_lakes(g, bed, c, np.where(bed > 0, sim.ice, 0.0), **kw)
    land = sim.land()
    wet = lk["wet"] & land
    lab, k = g.components(wet)
    big, kind, P = 0.0, "-", 0.0
    if k:
        cnt = np.bincount(lab[lab >= 0]); j = cnt.argmax(); big = cnt[j] * ck
        m = lab == j
        kk = np.bincount(lk["kind"][m], minlength=4); kind = "open" if kk[1] > kk[2] else "closed"
        P = np.median(sim.precip[m])
    vm = float(np.median(kw["valley"][land & (kw["valley"] > 0)])) if has_valley and (kw["valley"] > 0).any() else 0
    print(f"s{seed} t={t:g} big {big:.2f} {kind} P {P:.0f} lakes {wet.sum() * ck:.2f} Mkm2 "
          f"inland {100 * lk['endorheic'][land].mean():.1f}% sea {sim.sea_level:.0f} valley_med {vm:.0f}", flush=True)
    t += ev
