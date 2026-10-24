"""CO2 as a stock against a reference kept after the spin-up (planet/tectonics/earth.py, PW-558/559/576)."""

import numpy as np

from planet.tectonics import earth


def test_stock_settles_on_the_ratio_rule():
    """With the rates held, the stock settles where weathering x X^WEATHER_CO2 takes up the source."""
    for s, w in [(1.0, 1.0), (1.0, 0.5), (2.0, 1.0), (0.7, 1.3)]:
        c = 0.0
        for _ in range(200):
            c = earth.co2_stock(c, s, w, 2.0)
        assert np.isclose(c, np.log(s / w) / earth.WEATHER_CO2, atol=1e-6)


def test_stock_piles_up_while_the_sink_is_gone():
    """With no weathering, the outgassing adds s / CO2_TAU of the reference stock per Myr (no ceiling)."""
    c = earth.co2_stock(0.0, 1.0, 0.0, 10.0)
    assert np.isclose(np.exp(c), 1.0 + 10.0 / earth.CO2_TAU, rtol=1e-6)
    c2 = earth.co2_stock(c, 1.0, 0.0, 10.0)
    assert c2 > c


def test_stock_is_stable_at_long_steps():
    """Backward Euler: no overshoot past the steady state at any step length."""
    eq = np.log(1 / 0.3) / earth.WEATHER_CO2
    for dt in (0.1, 2.0, 50.0):
        c = earth.co2_stock(0.0, 1.0, 0.3, dt)
        assert 0.0 < c <= eq + 1e-9


def test_forcing_levels_off_smoothly():
    """co2_term reads the stock as pCO2 against the climate model's dT = 0 (climate.PCO2_REF): the planet's
    balance (stock 0, climate.PCO2_BALANCE) is a doubling above it (PW-559 B)."""
    from planet import climate

    class P:
        co2_sensitivity = 3.0
    at = lambda ppm: earth.co2_term(P, np.log(ppm / climate.PCO2_BALANCE))  # the term at a pCO2
    assert np.isclose(climate.pco2(0.0), climate.PCO2_BALANCE)
    assert abs(at(climate.PCO2_REF)) < 1e-12
    assert np.isclose(at(2 * climate.PCO2_REF), 3.0, rtol=0.01)  # co2_sensitivity per doubling (PW-646)
    assert np.isclose(earth.co2_term(P, 0.0), 3.0 * np.log2(climate.PCO2_BALANCE / climate.PCO2_REF), rtol=0.01)
    assert earth.co2_term(P, 50.0) < 3.0 / np.log(2.0) * earth.CO2_MAX + 1e-9
    assert at(climate.PCO2_REF / np.e) == -at(climate.PCO2_REF * np.e)


def test_references_are_kept_after_the_spin_up():
    """The source and sink references stop learning at REF_FREEZE (set once, PW-576)."""
    from planet.grid import build_grid
    from planet.tectonics import Params, Simulation
    s = Simulation(build_grid(3), 1, Params(), 2.0)
    s.run(earth.REF_FREEZE + 2)
    ref = s.refs.copy()
    s.run(s.t + 20)
    assert np.array_equal(s.refs, ref)
