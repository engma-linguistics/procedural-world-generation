"""Sea level follows the ocean basins against a fixed reference
(planet/tectonics/earth.py, PW-288)."""

import numpy as np
import pytest

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
        assert np.isclose(s.sea_tect - s.sea_cont - s.sea_sed, earth.SEA_TECT_MAX * np.tanh(rise / earth.SEA_TECT_MAX))
        seen.append(rise)
    assert max(abs(x) for x in seen) > 1.0  # (the floor did change)
    assert abs((RHO_MANTLE - RHO_WATER) / RHO_MANTLE - 0.69) < 0.01


def test_water_the_continents_give_up_raises_the_sea(grid4):
    """PW-980: the ocean's water is conserved. The sea the start's continents hold is the reference (0 at the
    first step); continents that rise out of it give their water to the basins, which rise by 0.69 of its
    depth over the ocean, and continents that sink take it back. An ice age's drained shelves don't count."""
    s = Simulation(grid4, 1, Params(heat_start=1.0), 2.0)
    s.step()
    w = earth.ocean_area(s.grid)
    assert s.cont_water_ref is not None
    s.cont_water_ref = None  # (taken again at this moment: the reference is what the continents hold then)
    assert abs(earth.continent_water(s, w)) < 1e-9 and s.cont_water_ref > 0
    held = s.cont_water_ref
    sub = s.w_cont & (s.w_elev + s.sea_ice < 0)
    assert sub.any()
    up = s.w_elev.copy()
    s.w_elev = np.where(sub, -s.sea_ice, up)  # every drowned continental cell brought up to the (ice-free) shore
    ocean = float(((s.w_elev + s.sea_ice < 0) * w).sum() / w.sum())
    assert np.isclose(earth.continent_water(s, w), (RHO_MANTLE - RHO_WATER) / RHO_MANTLE * held / ocean)
    s.w_elev = np.where(s.w_cont, up - 100.0, up)  # sunk by 100 m: the sea falls
    assert earth.continent_water(s, w) < 0.0
    s.w_elev, s.sea_ice = up + 50.0, s.sea_ice - 50.0  # 50 m more ice: the same water at the ice-free level
    assert abs(earth.continent_water(s, w)) < 1e-9


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


@pytest.mark.slow
def test_sea_level_starts_at_zero_and_reads_high_in_the_warm_up(grid4):
    """A fresh run's basin term starts at 0. Sea level 0 is the model's long-run ocean (mean floor depth
    after the 300 Myr warm-up, PW-549), so the warm-up itself, the starting supercontinent's breakup with
    its young floor, reads a highstand: the basin term over the first 300 Myr averages above 0 on a few
    seeds, but by less than a Cretaceous (+250 m). (With PW-293's 48 Myr start, measured over that
    breakup, these averaged near 0 and the later, older ocean read -100..-350 m.) The per-seed band is
    judged over ten seeds at the ~70% acceptance rule: one L4 seed's warm-up is a fragile fixture."""
    means = []
    for seed in range(1, 11):
        s = Simulation(grid4, seed, Params(heat_start=1.0), 2.0)
        s.step()
        assert abs(s.sea_tect) < 1.0
        st = [s.sea_tect]
        for _ in range(149):
            s.step()
            st.append(s.sea_tect)
        means.append(np.mean(st))
    # Owner 10-30: floor -30 m, not 0. The ten-seed mean wanders about +-15 m around ~+5 m between
    # near-null climate changes (lane 57 bisect), so a floor at 0 sat inside the chaos.
    assert -30 < np.mean(means) < 150, means
    assert np.mean([-50 < m < 200 for m in means]) >= 0.7, means


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


def test_sediment_moved_off_a_shelf_onto_the_ocean_floor_keeps_the_sea(grid4):
    """PW-950 lane 100e: the ocean's water is conserved when sediment moves. Carried from a drowned continental
    cell onto the ocean floor, the shelf holds more water (continent_water falls) and the floor's cover keeps as
    much out (floor_sediment_water rises), so the sea moves only by the two crusts' different isostatic lift of
    the same volume. Before the floor's part was counted, the sea fell by the whole of the shelf's extra water."""
    from planet.tectonics.isostasy import elevation, sediment_km
    s = Simulation(grid4, 1, Params(heat_start=1.0), 2.0)
    s.step()
    w = earth.ocean_area(s.grid)
    assert s.sed_water_ref is not None
    s.cont_water_ref = s.sed_water_ref = None  # (references taken at this moment)
    assert abs(earth.continent_water(s, w)) < 1e-9 and abs(earth.floor_sediment_water(s, w)) < 1e-9
    e = s.w_elev + s.sea_ice
    sed0 = sediment_km(s.w_cover, s.w_extra)
    a = int(np.flatnonzero(s.w_cont & (e < -1500) & (sed0 > 1.0))[0])  # a drowned continental cell with cover
    b = int(np.flatnonzero(~s.w_cont & (e < -3000))[0])  # deep ocean floor
    da = 1.0  # km of cover taken off a
    db = da * w[a] / w[b]  # the same volume laid on b
    thick, cover = s.w_thick.copy(), s.w_cover.copy()
    thick[a] -= da
    cover[a] -= da
    thick[b] += db
    cover[b] += db
    elev = elevation(thick, s.w_age, s.w_cont, s.w_rock, s.datum(), sediment_km(cover, s.w_extra))
    drop, rise = e[a] - (elev[a] + s.sea_ice), (elev[b] + s.sea_ice) - e[b]
    assert drop > 0 and rise > 0
    s.w_thick, s.w_cover, s.w_elev = thick, cover, elev
    cont, floor = earth.continent_water(s, w), earth.floor_sediment_water(s, w)
    ocean = float(((s.w_elev + s.sea_ice < 0) * w).sum() / w.sum())
    k = (RHO_MANTLE - RHO_WATER) / RHO_MANTLE
    assert np.isclose(cont, -k * drop * w[a] / w.sum() / ocean)
    assert np.isclose(floor, k * rise * w[b] / w.sum() / ocean)
    # (the net is only the isostatic difference of the same volume: drowned continental crust floats as in air,
    # isostasy.K_LAND, the ocean floor under water, K_SEA, so the floor gains more height than the shelf loses)
    assert np.isclose(cont + floor, k * (rise * w[b] - drop * w[a]) / w.sum() / ocean)
