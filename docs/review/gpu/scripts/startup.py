"""Cold-process costs: imports, grid build, Simulation init, first steps (numba cache loading).
python startup.py LEVEL"""
import time
T0 = time.perf_counter()
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); import env  # noqa
import numpy  # noqa
t_np = time.perf_counter()
import numba  # noqa
t_nb = time.perf_counter()
from planet import timeline as T
from planet.grid import build_grid
from planet.tectonics.simulation import Simulation
t_imp = time.perf_counter()
lvl = int(sys.argv[1])
g = build_grid(lvl)
t_g = time.perf_counter()
sim = Simulation(g, 1, T.make_params({}), 2.0)
t_init = time.perf_counter()
steps = []
for _ in range(6):
    a = time.perf_counter(); sim.step(); steps.append(time.perf_counter() - a)
print(f"L{lvl}: numpy import {t_np - T0:.2f}s, numba import {t_nb - t_np:.2f}s, planet imports {t_imp - t_nb:.2f}s, "
      f"build_grid {t_g - t_imp:.2f}s, Simulation init {t_init - t_g:.2f}s, steps "
      + " ".join(f"{s:.2f}" for s in steps))
