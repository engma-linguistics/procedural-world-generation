"""Sea level follows the ocean basins against a fixed reference
(planet/tectonics/earth.py, PW-288)."""

import numpy as np

from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet.tectonics import earth
from planet.tectonics.isostasy import RHO_MANTLE, RHO_WATER


def test_basin_term_is_measured_against_the_starting_floor():
    """depth_ref is the first step's mean floor depth and never moves; the
    basin term is (rho_m - rho_w) / rho_m of the smoothed floor's shallowing
    (the water's own load sinks the floor by the rest), softly limited."""
    s = Simulation(build_grid(4), 1, Params(heat_start=1.0), 2.0)
    s.run(2)
    ref = s.depth_ref
    seen = []
    for _ in range(40):
        s.step()
        assert s.depth_ref == ref
        rise = (RHO_MANTLE - RHO_WATER) / RHO_MANTLE * (s.depth_ridge - ref)
        assert np.isclose(s.sea_tect, earth.SEA_TECT_MAX * np.tanh(rise / earth.SEA_TECT_MAX))
        seen.append(rise)
    assert max(abs(x) for x in seen) > 1.0  # (the floor did change)
    assert abs((RHO_MANTLE - RHO_WATER) / RHO_MANTLE - 0.69) < 0.01


def test_starting_ocean_is_the_models_steady_state(grid4):
    """Setup's ocean is a steady-state one with the model's own mean depth
    (PW-293): mean age OCEAN_MAX_AGE / 3 on every seed (ranked over the
    ocean's cells, so the continent can't take a biased share of it)."""
    from planet.tectonics import setup
    for seed in (1, 2, 3):
        s = Simulation(grid4, seed, Params(heat_start=1.0), 2.0)
        ocean = ~s.w_cont
        assert abs(s.w_age[ocean].mean() - setup.OCEAN_MAX_AGE / 3) < 0.05
        assert s.w_age[ocean].max() < setup.OCEAN_MAX_AGE


def test_sea_level_starts_at_zero_and_stays_near_it(grid4):
    """A fresh run's basin term starts at 0 and, over its first 300 Myr
    (the starting supercontinent's breakup highstand included), averages
    near 0 over a few seeds: sea level 0 is the model's own mean ocean
    (PW-293; with the old 60 Myr start these seeds averaged +73..+102 m)."""
    means = []
    for seed in (1, 2, 3):
        s = Simulation(grid4, seed, Params(heat_start=1.0), 2.0)
        s.step()
        assert abs(s.sea_tect) < 1.0
        st = [s.sea_tect]
        for _ in range(149):
            s.step()
            st.append(s.sea_tect)
        means.append(np.mean(st))
    assert abs(np.mean(means)) < 50, means
    assert all(abs(m) < 120 for m in means), means


def test_starting_continents_ride_inside_plates():
    """Either start puts each continent whole on one plate, with plate
    boundaries in the ocean (PW-328: the scattered start cut its continents
    along random plate boundaries, so they collided instead of drifting and
    the starting ocean hardly renewed)."""
    g = build_grid(5)
    a, b = g.edges[:, 0], g.edges[:, 1]
    for start in ("scattered", "supercontinent"):
        for seed in (1, 2):
            s = Simulation(g, seed, Params(start=start), 2.0)
            cont, own = s.w_cont, s.owner
            lab, nl = g.components(cont)
            for i in range(nl):
                assert len(np.unique(own[lab == i])) == 1
            bd = own[a] != own[b]
            assert not (bd & cont[a] & cont[b]).any()
            # (a boundary meets a coast only where two continents face each other across a narrow sea)
            assert (bd & (cont[a] | cont[b])).sum() < 0.05 * bd.sum()
            assert all(s.plates.owned[k].any() for k in np.flatnonzero(s.plates.alive))
