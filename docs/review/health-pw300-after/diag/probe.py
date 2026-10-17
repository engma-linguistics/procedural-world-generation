"""python probe.py <code dir> seed t [t..]: the biggest lake on the frame: depth profile, spill, outflow."""
import sys
sys.path.insert(0, sys.argv[1])
import planet  # noqa
import numpy as np
from planet import hydrology
from planet.geo import R_KM
from planet.grid import build_grid
from planet.tectonics import Params, Simulation

seed = int(sys.argv[2])
g = build_grid(6)
sim = Simulation(g, seed, Params(flora_end=500.0), 2.0)
ck = 4 * np.pi * R_KM ** 2 / g.n / 1e6
prev = None
for t in map(float, sys.argv[3:]):
    sim.run(t)
    bed = sim.bed()
    c = {"runoff": sim.runoff, "aet": sim.aet, "lake_evap": sim.lake_evap}
    land = sim.land()
    flow, down, lk = hydrology.rivers_and_lakes(g, bed, c, np.where(bed > 0, sim.ice, 0.0), valley=sim.valley())
    wet = lk["wet"] & land
    lab, k = g.components(wet)
    cnt = np.bincount(lab[lab >= 0]); j = cnt.argmax(); m = lab == j
    depth = lk["level"][m] - bed[m]
    lvl = np.median(lk["level"][m])
    # outflow: lake cells whose downstream is off the lake
    out = np.where(m & (down >= 0))[0]
    out = out[~m[down[out]]]
    q = hydrology.discharge(g, flow)
    o = out[np.argmax(flow[out])] if len(out) else -1
    path = []
    i = o
    while i >= 0 and len(path) < 8:
        path.append(f"{bed[i]:.0f}/{sim.valley()[i]:.0f}/i{sim.ice[i]:.0f}")
        i = down[i]
    pf, _, _ = hydrology.priority_flood(g, bed)[0], None, None
    print(f"s{seed} t={t:g} big {cnt[j] * ck:.2f} kind {np.bincount(lk['kind'][m], minlength=4)} level {lvl:.0f} "
          f"bed min {bed[m].min():.0f} depth med {np.median(depth):.0f} max {depth.max():.0f} "
          f"spill (priority flood) {np.median(pf[m]):.0f}  outlet Q {q[o] if o >= 0 else 0:.0f} m3/s "
          f"path bed/valley {' '.join(path)}  P {np.median(sim.precip[m]):.0f} crust {np.median(sim.w_thick[m]):.1f} km "
          f"ice on lake {np.mean(sim.ice[m] > 0):.2f} near {np.mean(sim.ice[np.unique(g.nbr_idx[np.concatenate([np.arange(g.nbr_off[c], g.nbr_off[c + 1]) for c in np.where(m)[0]])])] > 0):.2f}", flush=True)
    prev = sim.owner.copy()
