"""Shared fixtures. Simulations are slow-ish, so the common ones are built
once per test session and reused (tests must not modify them). Plain
helpers are in helpers.py."""

import pytest

from planet.grid import build_grid

from helpers import run_sim


def pytest_addoption(parser):
    parser.addoption("--update-golden", action="store_true",
                     help="rewrite tests/golden/*.json from the current code (for commits meant to change outputs)")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: envelope tests on level-5 worlds (~1 min); skip with -m 'not slow'")


@pytest.fixture(scope="session")
def sim4():
    """Level 4 (2.5k cells), seed 1, 300 Myr: small but has seen rifting,
    collisions, a few climate updates."""
    return run_sim()


@pytest.fixture(scope="session")
def sim4_60():
    """Level 4, seed 1, 60 Myr: the golden-output case."""
    return run_sim(myr=60)


@pytest.fixture(scope="session")
def grid4():
    return build_grid(4)
