"""Run to t and show the worst crust spike and its neighbours (thickness,
cover, elevation, subsidence term, plate, continent)."""
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
sets = dict(a.split("=") for a in sys.argv[5:])
sim = Simulation(build_grid(level), seed, Params(flora_end=myr, **{k: float(v) for k, v in sets.items()}), 2.0)
g = sim.grid
hist = []


def on_step(s):
    i = int(np.argmax(s.w_elev))
    hist.append((s.t, i, s.w_elev[i], s.w_thick[i], s.w_cover[i], s.dyn[i]))


sim.run(myr, on_step)
for h in hist[-12:]:
    print("t %.0f top cell %d elev %.0f thick %.1f cover %.1f dyn %.0f" % h)
i = int(np.argmax(sim.w_elev))
nb = g.neighbors[i]
for c in [i, *nb]:
    print(f"cell {c}: thick {sim.w_thick[c]:.1f} cover {sim.w_cover[c]:.1f} elev {sim.w_elev[c]:.0f} "
          f"dyn {sim.dyn[c]:.0f} plate {sim.owner[c]} cont {sim.w_cont[c]} rock {sim.w_rock[c]} bnd {sim.w_boundary[c]}")
