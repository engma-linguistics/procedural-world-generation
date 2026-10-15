"""Sediment is lighter than crust and compacts with depth
(planet/tectonics/isostasy.py)."""

import numpy as np

from planet.tectonics import isostasy as I


def test_density_compacts_with_depth():
    rho = I.sediment_density(np.array([0.0, 1, 3, 10]))
    assert np.all(np.diff(rho) > 0) and 2.0 <= rho[0] <= 2.2 and 2.5 <= rho[-1] <= 2.65
    assert rho[-1] < I.RHO_CONT


def test_filling_deep_water_takes_about_three_times_its_depth():
    c = np.linspace(0, 40, 4001)
    no = np.zeros_like(c, bool)
    rise = I.ISO_SEA * c + I.sediment_lift(no, np.zeros_like(c), c)  # m the floor rises
    need = c[np.searchsorted(rise, 5000.0)]
    assert 2.5 <= need / 5.0 <= 3.5, need  # Earth ~3x; crust density would need 5x


def test_marginal_iso_is_the_slope_of_the_lift():
    c = np.array([0.5, 2.0, 8.0])
    for cont in (False, True):
        m = np.full(3, cont)
        r = np.zeros(3)
        h = 1e-4
        slope = (I.sediment_lift(m, r, c + h) - I.sediment_lift(m, r, c - h)) / (2 * h) + I.iso_rate(m, r)
        assert np.allclose(slope, I.sediment_iso(m, r, c), rtol=1e-6)


# Glacial isostasy (PW-189)
def _cap(grid, lat0, h):
    """h m of ice on every cell poleward of lat0 (north)."""
    return np.where(grid.lat >= lat0, h, 0.0)


def test_a_big_sheet_sinks_its_bed_about_0_28_of_its_thickness():
    from planet.grid import build_grid
    g = build_grid(5)
    ice = _cap(g, 60.0, 3000.0)  # ~3000 km across
    d = I.ice_load(g, ice)
    middle = g.lat > 80
    assert 780 <= d[middle].mean() <= 880, d[middle].mean()  # PW-189: ~800-900 m under 3 km
    # flexure spreads it: the rim sinks less than its ice alone would, the ground just outside a little
    rim = (g.lat >= 60) & (g.lat < 62)
    assert d[rim].mean() < 0.9 * I.ICE_SINK * 3000
    out = (g.lat < 58) & (g.lat > 54)
    assert 0 < d[out].mean() < 300
    # total (area x depth) kept
    assert abs(d.sum() / (I.ICE_SINK * ice).sum() - 1) < 0.02


def test_a_small_cap_barely_dents_the_crust():
    from planet.grid import build_grid
    g = build_grid(6)
    one = np.zeros(g.n)
    one[np.argmax(g.lat)] = 2000.0  # a single ~110 km cell
    assert I.ice_load(g, one).max() < 0.5 * I.ICE_SINK * 2000


def test_land_view_keeps_the_surface():
    e, ice, low = I.land_view(np.array([-300.0, 200.0, -50.0]), np.array([2500.0, 1000.0, 0.0]))
    assert list(low) == [True, False, False]
    assert e[0] == I.BED_FLOOR and ice[0] == 2500 - 300 - I.BED_FLOOR
    assert e[1] == 200 and ice[1] == 1000 and e[2] == -50
