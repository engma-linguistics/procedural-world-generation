"""Shared fixtures. Simulations are slow-ish, so the common ones are built
once per test session and reused (tests must not modify them)."""

import numpy as np
import pytest

from planet.grid import build_grid
from planet.tectonics import Params, Simulation


def pytest_addoption(parser):
    parser.addoption("--update-golden", action="store_true",
                     help="rewrite tests/golden/*.json from the current code (for commits meant to change outputs)")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: envelope tests on level-5 worlds (~1 min); skip with -m 'not slow'")


def run_sim(level=4, seed=1, myr=300.0, **params):
    sim = Simulation(build_grid(level), seed, Params(**params), 2.0)
    sim.run(myr)
    return sim


@pytest.fixture(scope="session")
def sim4():
    """Level 4 (2.5k cells), seed 1, 300 Myr: small but has seen rifting,
    collisions, a few climate updates."""
    return run_sim()


@pytest.fixture(scope="session")
def grid4():
    return build_grid(4)


def continental_volume(sim):
    return float((sim.w_thick * sim.w_cont).sum()) / sim.scale**2
