"""Sensitivity of a frame's biggest lake to open-water evaporation: python evsens.py <code> <run dir> t [t...]"""
import sys
sys.path.insert(0, sys.argv[1])
import planet  # noqa
from pathlib import Path
import numpy as np
from planet import timeline as T, hydrology
from planet.geo import R_KM

rd = Path(sys.argv[2])
for ts in sys.argv[3:]:
    sim = T.replay(rd, float(ts), log=lambda *a: None)
    g = sim.grid
    ck = 4 * np.pi * R_KM ** 2 / g.n / 1e6
    bed = sim.bed()
    land = bed > 0
    out = []
    for f in (1.0, 0.85, 0.7):
        c = {"runoff": sim.runoff, "aet": sim.aet, "lake_evap": f * sim.lake_evap}
        flow, down, lk = hydrology.rivers_and_lakes(g, bed, c, np.where(land, sim.ice, 0.0))
        lab, k = g.components(lk["wet"] & land)
        cnt = np.bincount(lab[lab >= 0])
        j = cnt.argmax()
        kind = np.bincount(lk["kind"][lab == j], minlength=4)
        out.append(f"x{f}: {cnt[j] * ck:.2f} Mkm2 {'open' if kind[1] > kind[2] else 'closed'}, lakes {lk['wet'][land].sum() * ck:.2f}, "
                   f"inland {100 * lk['endorheic'][land].mean():.1f}%")
    m = lab == j
    print(f"t={ts} P {np.median(sim.precip[m]):.0f}: " + " | ".join(out))
