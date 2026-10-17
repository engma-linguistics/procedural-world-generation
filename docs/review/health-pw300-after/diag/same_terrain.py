"""python same_terrain.py <code dir> seed t0 t1 every: on each frame's own terrain, rivers and lakes with
the run's valley memory and without it (the old model): biggest lake, lakes, inland."""
import sys
sys.path.insert(0, sys.argv[1])
import planet  # noqa
import numpy as np
from planet import hydrology
from planet.geo import R_KM
from planet.grid import build_grid
from planet.tectonics import Params, Simulation

seed, t0, t1, ev = int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
g = build_grid(6)
sim = Simulation(g, seed, Params(flora_end=500.0), 2.0)
ck = 4 * np.pi * R_KM ** 2 / g.n / 1e6


def stats(lk, land):
    wet = lk["wet"] & land
    lab, k = g.components(wet)
    big, kind = 0.0, "-"
    if k:
        cnt = np.bincount(lab[lab >= 0]); j = cnt.argmax(); big = cnt[j] * ck
        kk = np.bincount(lk["kind"][lab == j], minlength=4); kind = "open" if kk[1] > kk[2] else "closed"
    P = E = 0
    if k:
        P, E = np.median(sim.precip[lab == j]), np.median(sim.lake_evap[lab == j])
    return f"big {big:.2f} {kind:6s} P {P:.0f} E {E:.0f} lakes {wet.sum() * ck:.2f} (open {(wet & (lk['kind'] == 1)).sum() * ck:.2f} closed {(wet & (lk['kind'] == 2)).sum() * ck:.2f}) inland {100 * lk['endorheic'][land].mean():4.1f}%"


t = t0
while t <= t1 + 1e-6:
    sim.run(t)
    bed = sim.bed()
    c = {"runoff": sim.runoff, "aet": sim.aet, "lake_evap": sim.lake_evap}
    land = sim.land()
    ice = np.where(bed > 0, sim.ice, 0.0)
    out = []
    for v in (sim.valley(), None):
        _, _, lk = hydrology.rivers_and_lakes(g, bed, c, ice, valley=v)
        out.append(stats(lk, land))
    print(f"s{seed} t={t:g} memory: {out[0]} | none: {out[1]}", flush=True)
    t += ev
