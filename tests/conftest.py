"""Shared fixtures. Simulations are slow-ish, so the common ones are built
once per test session and reused (tests must not modify them). Plain
helpers are in helpers.py."""

import os

# Small kernels: 4 numba threads take the same wall time as 16 or 48 (~4.7 min
# on the Threadripper) for a third of the CPU (most of it was spinning
# threads). Before planet is imported; outputs don't depend on it.
os.environ.setdefault("NUMBA_NUM_THREADS", "4")

import pytest  # noqa: E402

from planet.grid import build_grid  # noqa: E402

from helpers import run_sim  # noqa: E402
import seeds  # noqa: E402


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
def sources4(tmp_path_factory):
    """The time zoom's sources (timezoom.source_from_sim) of the L4 300 Myr runs of seeds.SEEDS4 (sim4's
    world and 23 others), built once per session for the multi-seed tests: [(seed, source)]."""
    return seeds.shared(tmp_path_factory, "sources4",
                        lambda: list(zip(seeds.SEEDS4, seeds.pool_map(seeds.source4, seeds.SEEDS4))))


@pytest.fixture(scope="session")
def sim4_60():
    """Level 4, seed 1, 60 Myr: the golden-output case."""
    return run_sim(myr=60)


@pytest.fixture(scope="session")
def grid4():
    return build_grid(4)


@pytest.fixture
def data_root(tmp_path, monkeypatch):
    """A temporary data root (store.root()) for tests that write runs, worlds or zooms."""
    from planet import store
    monkeypatch.setattr(store, "_root", tmp_path)
    return tmp_path
