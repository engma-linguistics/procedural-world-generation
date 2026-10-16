"""How much continental crust cleanup_ghosts stacks (instead of deleting),
against the continents' volume (PW-046)."""
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402
from planet.tectonics import simulation as S  # noqa: E402

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
tot = {"ghost": 0.0, "resolve_stack": 0.0}
orig = S.cleanup_ghosts


def wrapped(*a):
    stacked = a[-1]
    s0 = stacked.sum()
    r = orig(*a)
    tot["ghost"] += stacked.sum() - s0
    tot["resolve_stack"] += s0
    return r


S.cleanup_ghosts = wrapped
sim = Simulation(build_grid(level), seed, Params(flora_end=myr), 2.0)
v0 = float((sim.w_thick * sim.w_cont).sum())
sim.run(myr)
print(f"stacked by resolve {tot['resolve_stack']:.0f} km-cells, by ghosts {tot['ghost']:.0f} "
      f"({tot['ghost'] / v0 * 100:.2f}% of the start volume)")
