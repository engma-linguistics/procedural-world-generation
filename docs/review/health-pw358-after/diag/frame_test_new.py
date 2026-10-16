"""Controlled frame test: run a seed with main's code; at each time, route rivers/lakes on the same terrain
with main's lake_evap (Oudin x 1.2) and with Penman's (PW-358, from the same climate's rh/cloud).
usage: python frame_test.py <main code dir> seed t [t...]"""
import sys
sys.path.insert(0, sys.argv[1])
import planet  # noqa  (first: thread caps)
print("code:", planet.__file__, flush=True)
import numpy as np
from planet import climate, hydrology
from planet.geo import R_KM
from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet.tectonics import earth as E

last = {}
orig = climate.compute


def rec(*a, **k):
    c = orig(*a, **k)
    last.clear()
    last.update(c)
    return c


E.climate.compute = rec

SIGMA_MJ, PSYCHRO = 4.903e-9, 0.0665
C = climate


def open_water_evap(lat, temp, t_warm, t_cold, rh_jul, rh_jan, cloud_jul, cloud_jan, tilt=23.4, u2=2.0):
    t = C.month_temps(lat, temp, t_warm, t_cold)
    ra = C.insolation(lat, tilt)
    jul = ((np.arange(12) >= 3) & (np.arange(12) <= 8))[:, None]
    rh = np.clip(np.where(jul, rh_jul, rh_jan) / 100.0, 0.0, 1.0)
    rs = ra * (0.25 + 0.5 * C.sunshine(np.where(jul, cloud_jul, cloud_jan)))
    es = 0.6108 * np.exp(17.27 * t / (t + 237.3))
    ea = rh * es
    rnl = (SIGMA_MJ * (t + 273.15) ** 4 * (0.34 - 0.14 * np.sqrt(ea))
           * (1.35 * np.clip(rs / np.maximum(0.75 * ra, 1e-9), 0, 1) - 0.35))
    rn = np.maximum((1 - 0.06) * rs - rnl, 0.0)
    delta = 4098.0 * es / (t + 237.3) ** 2
    fu = 6.43 * (1 + 0.536 * u2)
    e = (delta * rn + PSYCHRO * fu * (es - ea)) / (delta + PSYCHRO) / C.LATENT
    return (np.where(t > 0, e, 0.0) * C.MONTH_DAYS[:, None]).sum(0)


seed = int(sys.argv[2])
g = build_grid(6)
sim = Simulation(g, seed, Params(flora_end=500.0), 2.0)
ck = 4 * np.pi * R_KM ** 2 / g.n / 1e6
for ts in map(float, sys.argv[3:]):
    sim.run(ts)
    bed = sim.bed()
    land = bed > 0
    c0 = last
    pen = sim.lake_evap
    oud = np.where(land, 1.2 * c0["pet"], 0.0)
    out = []
    for name, le in (("oudin", oud), ("penman", pen)):
        c = {"runoff": sim.runoff, "aet": sim.aet, "lake_evap": le}
        flow, down, lk = hydrology.rivers_and_lakes(g, bed, c, np.where(land, sim.ice, 0.0))
        lab, k = g.components(lk["wet"] & land)
        cnt = np.bincount(lab[lab >= 0]) if (lab >= 0).any() else np.array([0])
        j = cnt.argmax()
        m = lab == j
        kind = np.bincount(lk["kind"][m], minlength=4)
        ev = np.median(le[m]) if m.any() else 0
        out.append(f"{name}: big {cnt[j] * ck:.2f} {'open' if kind[1] > kind[2] else 'closed'} E {ev:.0f} aet "
                   f"{np.median(sim.aet[m]) if m.any() else 0:.0f}, lakes {lk['wet'][land].sum() * ck:.2f}, "
                   f"inland {100 * lk['endorheic'][land].mean():.1f}%")
        if name == "oudin":
            mo = m
    print(f"s{seed} t={ts:g} P {np.median(sim.precip[mo]) if mo.any() else 0:.0f} T "
          f"{np.median(sim.temp[mo]) if mo.any() else 0:.1f}: " + " | ".join(out), flush=True)
