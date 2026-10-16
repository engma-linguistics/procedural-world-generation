"""python capture_fresh.py LEVEL OUTDIR: a fresh simulation's first step (its climate update) with
climate._rain and timezoom_kernels.climate_step captured (as capture.py), for L8 sizes."""
import os, sys, pickle, time
sys.path.insert(0, os.path.dirname(__file__)); import env  # noqa
import numpy as np
from planet import climate, timezoom_kernels as TK, timeline as T
from planet.grid import build_grid
from planet.tectonics.simulation import Simulation
import capture_lib as CL

lvl, outdir = int(sys.argv[1]), sys.argv[2]
os.makedirs(outdir, exist_ok=True)
CL.install(outdir, lvl)
t0 = time.perf_counter()
g = build_grid(lvl)
sim = Simulation(g, 3199, T.make_params({}), 2.0)
print("init", round(time.perf_counter() - t0, 1), flush=True)
sim.step()
print("step", round(time.perf_counter() - t0, 1), flush=True)
