"""Sediment is lighter than crust and compacts with depth
(planet/tectonics/isostasy.py)."""

import importlib

import numpy as np

# (planet.tectonics.isostasy the attribute is the function; this is the module)
I = importlib.import_module("planet.tectonics.isostasy")


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
        slope = (I.sediment_lift(m, r, c + h) - I.sediment_lift(m, r, c - h)) / (2 * h) + I.isostasy(m, r)
        assert np.allclose(slope, I.sediment_iso(m, r, c), rtol=1e-6)
