"""Plain helpers shared by the tests (fixtures live in conftest.py)."""

from planet.grid import build_grid
from planet.tectonics import Params, Simulation


def run_sim(level=4, seed=1, myr=300.0, **params):
    sim = Simulation(build_grid(level), seed, Params(**params), 2.0)
    sim.run(myr)
    return sim


def continental_volume(sim):
    return float((sim.w_thick * sim.w_cont).sum()) / sim.scale**2
