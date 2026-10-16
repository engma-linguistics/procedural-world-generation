"""Arid (Koppen B) share of land over a run, every 20 Myr (the envelope test's L5 worlds)."""
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
GROUP = np.array([k[1][0] for k in climate.KOPPEN])
sim = Simulation(build_grid(level), seed, Params(flora_end=320.0), 2.0)
out = []
while sim.t < myr - 1e-9:
    sim.run(sim.t + 20)
    if sim.t >= 100:
        land = sim.w_elev > 0
        out.append(100 * (GROUP[sim.snapshot().koppen[land]] == "B").mean())
print(planet.__file__, "dry % every 20 Myr from 100:", " ".join(f"{x:.0f}" for x in out),
      f"| mean {np.mean(out):.1f}")
