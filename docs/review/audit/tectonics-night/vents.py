"""PW-338: hotspot vents' recorded floor and top against the cells they sit on.

    uv run python docs/review/audit/tectonics-night/vents.py <repo> <level> <seed> <myr>

Pooled over keyframe-like samples every 20 Myr after 50 Myr: vents (hotspot
kind) by setting, the median of floor - ground (ground: min elevation over
the vent's cell and neighbours, w_elev), and the share whose floor sits
> 1 km below that ground, or whose top is below the ground.
"""
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation, volcanism  # noqa: E402

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
sim = Simulation(build_grid(level), seed, Params(flora_end=myr), 2.0)
g = sim.grid
rows = []


def on(s):
    if s.t <= 50 or abs(s.t / 20 - round(s.t / 20)) > 1e-6:
        return
    vs = [v for v in s.volcanoes if v["kind"] == volcanism.VENT]
    if not vs:
        return
    cells = g.locate(np.array([v["pos"] for v in vs]))
    for v, c in zip(vs, cells):
        c = int(c)
        ground = float(s.w_elev[np.append(g.nbr_idx[g.nbr_off[c]:g.nbr_off[c + 1]], c)].min())
        rows.append((v["floor"] - ground, v["top"] - float(s.w_elev[c]), ground > 0, s.t - v["born"]))


sim.run(myr, on)
a = np.array(rows)
for name, m in (("all", np.ones(len(a), bool)), ("ground above sea", a[:, 2] > 0), ("at sea", a[:, 2] == 0)):
    if not m.any():
        continue
    d, top = a[m, 0], a[m, 1]
    print(f"{name:17s} n {m.sum():5d}  floor - ground median {np.median(d):7.0f} m, floor > 1 km below ground "
          f"{(d < -1000).mean() * 100:5.1f}%, top below its cell {(top < 0).mean() * 100:5.1f}%")
