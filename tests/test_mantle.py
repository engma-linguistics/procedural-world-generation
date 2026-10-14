"""The mantle field (planet/tectonics/mantle.py): cold under long-lived
trenches, warm under a parked continent, traction from warm toward cold,
plumes from warm mantle."""

import numpy as np
import pytest

from planet.grid import build_grid
from planet.tectonics import Params, Simulation, mantle


class Trenches:
    """A stand-in for motion.Boundaries: slabs sinking at `cells`."""

    def __init__(self, cells, conv=5.0):
        self.sinking = np.asarray(cells, np.int64)
        self.conv = np.full(len(cells), conv)

    def at_trenches(self, per_edge):
        return per_edge


@pytest.fixture()
def sim():
    s = Simulation(build_grid(4), 3, Params(), 2.0)
    s.mantle = np.zeros(s.grid.n)
    s.mantle_lid = np.zeros(s.grid.n)
    s.mantle_eddies = np.zeros_like(s.mantle_eddies)
    return s


def cap(sim, centre, deg):
    c = np.asarray(centre, float)
    return sim.grid.centers @ (c / np.linalg.norm(c)) > np.cos(np.radians(deg))


def test_basis_is_orthonormal(sim):
    Y, deg = mantle.basis(sim.grid)
    assert np.allclose(Y.T @ Y, np.eye(Y.shape[1]), atol=1e-9)
    assert len(deg) == (mantle.LMAX + 1) ** 2 - 1  # degrees 1..LMAX, no mean
    assert abs(mantle.smooth(sim, np.ones(sim.grid.n), 2000).max()) < 1e-9  # a constant has no anomaly


def test_cold_under_long_lived_trench(sim):
    g = sim.grid
    sim.w_cont[:] = False
    sim.w_age[:] = 100.0
    # a 3000 km trench along the equator around lon 0
    trench = np.flatnonzero((np.abs(g.lat) < 2.5) & (np.abs(g.lon) < 13))
    bd = Trenches(trench)
    for _ in range(100):  # 200 Myr
        mantle.update(sim, bd)
    under = sim.mantle[trench].mean()
    far = sim.mantle[cap(sim, [-1, 0, 0], 40)].mean()  # the other side of the planet
    assert under < -0.1 and under < far - 0.1, (under, far)
    # it relaxes once subduction stops
    for _ in range(150):
        mantle.update(sim, Trenches([]))
    assert abs(sim.mantle[trench].mean()) < 0.5 * abs(under)


def test_warm_under_parked_continent_and_faster_the_longer_it_stays(sim):
    land = cap(sim, [0, 0, 1], 35)
    sim.w_cont[:] = land
    bd = Trenches([])
    warmth = []
    for i in range(100):  # 200 Myr parked
        mantle.update(sim, bd)
        if i % 25 == 24:
            warmth.append(sim.mantle[land].mean())
    assert warmth[-1] > 0.3 and warmth[-1] > sim.mantle[~land].mean() + 0.3
    gains = np.diff([0.0] + warmth)
    assert gains[1] > gains[0]  # the lid builds up: warming speeds up at first


def test_traction_runs_from_warm_to_cold(sim):
    g = sim.grid
    hot = np.array([0.0, 0.0, 1.0])
    sim.mantle = mantle.smooth(sim, cap(sim, hot, 30).astype(float), 2500)
    sim.w_cont[:] = False
    F = mantle.traction(sim)
    ring = (g.lat > 40) & (g.lat < 60)  # flanks of the warm dome: flow points away from it (south)
    away = g.centers[ring] * 1.0
    away = away - hot  # direction away from the pole, roughly
    away -= (away * g.centers[ring]).sum(1, keepdims=True) * g.centers[ring]
    assert ((F[ring] * away).sum(1) > 0).mean() > 0.95
    # continents feel it more (keels)
    sim.w_cont[:] = True
    assert np.allclose(np.linalg.norm(mantle.traction(sim), axis=1)[ring],
                       (1 + sim.params.continental_keel) * np.linalg.norm(F[ring], axis=1))


def test_plumes_prefer_warm_mantle(sim):
    sim.mantle = mantle.smooth(sim, cap(sim, [1, 0, 0], 40).astype(float), 2500)
    sim.mantle /= sim.mantle.max()
    odds = mantle.plume_odds(sim)
    warm, cold = sim.mantle > np.quantile(sim.mantle, 0.8), sim.mantle < np.quantile(sim.mantle, 0.2)
    assert odds[warm].mean() > 2 * odds[cold].mean()


def test_eddies_wander_with_the_set_size(sim):
    rng = np.random.default_rng(0)
    rms = []
    for _ in range(300):
        mantle.stir(sim, rng)
        rms.append(np.sqrt((mantle.eddies(sim) ** 2).mean()))
    assert 0.6 * sim.params.mantle_eddies < np.mean(rms[100:]) < 1.4 * sim.params.mantle_eddies
