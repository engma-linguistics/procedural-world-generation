"""The climate's own answer to dT on fixed geography (no run, no chaos): climate.compute at dT0 - 2, dT0, dT0 + 2 on
Earth (L6) and on pickled sim moments, in the tree it runs from (cwd). Per world, per C of dT (cold side / warm side):
the ice-free land's mean temperature, the same where the land stands high (> 1000 m, where most rock erodes),
ln of the land's runoff, and a weathering-sink proxy, ln sum(relief x runoff x exp(0.09 (T - 15))) over ice-free
land, with its temperature factor alone. usage: static.py OUT.txt SOURCE.pkl ..."""
import os
import pickle
import sys

sys.path[:0] = [os.getcwd()]
os.environ.setdefault("NUMBA_NUM_THREADS", "4")
import numpy as np  # noqa: E402

from planet import climate  # noqa: E402
from planet.geo import is_land  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.timezoom.sources import source_earth  # noqa: E402

out = open(sys.argv[1], "w")
worlds = [("earth L6", source_earth(6))]
for p in sys.argv[2:]:
    s = pickle.loads(open(p, "rb").read())
    s["grid"] = build_grid(s["level"])
    worlds.append((os.path.basename(p), s))
for name, s in worlds:
    g, elev, ice, tilt, dT0 = s["grid"], np.asarray(s["elev"], float), np.asarray(s["ice"], float), s["tilt"], s["dT"]
    land = is_land(elev, ice) & (ice <= 0)
    nb = g.nbr_idx
    relief = np.maximum(np.maximum.reduceat(np.abs(elev[nb] - np.repeat(elev, np.diff(g.nbr_off))), g.nbr_off[:-1]), 1.0)
    hi = land & (elev > 1000)
    res = {}
    for d in (-2.0, 0.0, 2.0):
        c = climate.compute(g, elev, dT0 + d, tilt, ice=ice)
        T, q = c["temp"], np.maximum(c["runoff"], 0.0)
        warm = np.exp(0.09 * (T - 15.0))
        res[d] = dict(T=T[land].mean(), Thi=T[hi].mean() if hi.any() else np.nan, lq=np.log(q[land].mean()),
                      sink=np.log((relief * q * warm)[land].sum()), temp=np.log((relief * q * warm)[land].sum() / (relief * q)[land].sum()))
    line = f"{name} (dT0 {dT0:+.2f}, land {land.mean():.3f}, high {hi.mean():.3f}):"
    for k in ("T", "Thi", "lq", "sink", "temp"):
        line += f"  {k} {(res[0][k] - res[-2][k]) / 2:+.4f} / {(res[2][k] - res[0][k]) / 2:+.4f}"
    print(line, file=out, flush=True)
