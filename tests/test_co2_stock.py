"""CO2 as a stock against a reference kept after the spin-up (planet/tectonics/earth.py, PW-558/559/576)."""

import numpy as np

from planet.tectonics import earth


def test_stock_settles_where_the_sink_takes_up_the_source():
    """With the rates held, the stock settles where w x co2_law(X) takes up the source, on bare ground
    (X^0.5), planted (GEOCARB's saturating (2X / (1 + X))^0.4) and mixed."""
    for bare in (1.0, 0.0, 0.4):
        for s, w in [(1.0, 1.0), (1.0, 0.5), (2.0, 1.0), (0.7, 1.3), (1.0, 0.85)]:
            if bare == 0.0 and s / w >= 2.0**earth.WEATHER_FERT:
                continue  # (fully planted, the CO2 law saturates at 2^0.4: only warmth balances it; below)
            c = 0.0
            for _ in range(200):
                c = earth.co2_stock(c, s, w, 2.0, bare)
            assert np.isclose(w * earth.co2_law(np.exp(c), bare), s, rtol=1e-6)
    c = 0.0
    for _ in range(50):
        c = earth.co2_stock(c, 4.0, 1.0, 50.0, 1.0)
    assert np.isclose(c, np.log(16.0), atol=1e-6)  # bare: X = (s / w)^2
    c = earth.co2_stock(0.0, 1.0, 0.5, 50.0, 0.0)  # planted, sink beyond the law's reach: CO2 keeps rising
    assert earth.co2_stock(c, 1.0, 0.5, 50.0, 0.0) > c > 2.0


def test_co2_law():
    """1 at the balance; bare ground's log-slope 0.5, planted 0.2 there and falling toward 0 at high CO2."""
    for bare in (0.0, 0.3, 1.0):
        assert np.isclose(earth.co2_law(1.0, bare), 1.0)
    assert np.isclose(earth.co2_slope(1.0, 1.0), 0.5)
    assert np.isclose(earth.co2_slope(1.0, 0.0), 0.2)
    assert earth.co2_slope(10.0, 0.0) < 0.05
    x = 3.0
    num = (np.log(earth.co2_law(x * 1.001, 0.3)) - np.log(earth.co2_law(x / 1.001, 0.3))) / (2 * np.log(1.001))
    assert np.isclose(earth.co2_slope(x, 0.3), num, rtol=1e-4)


def test_stock_piles_up_while_the_sink_is_gone():
    """With no weathering, the outgassing adds s / CO2_TAU of the reference stock per Myr (no ceiling)."""
    c = earth.co2_stock(0.0, 1.0, 0.0, 10.0)
    assert np.isclose(np.exp(c), 1.0 + 10.0 / earth.CO2_TAU, rtol=1e-6)
    c2 = earth.co2_stock(c, 1.0, 0.0, 10.0)
    assert c2 > c


def test_stock_is_stable_at_long_steps():
    """Backward Euler: no overshoot past the steady state at any step length."""
    for bare in (1.0, 0.0):
        eq = 0.0
        for _ in range(400):
            eq = earth.co2_stock(eq, 1.0, 0.3, 50.0, bare)
        for dt in (0.1, 2.0, 50.0):
            c = earth.co2_stock(0.0, 1.0, 0.3, dt, bare)
            assert 0.0 < c <= eq + 1e-9


def test_plants_weather_faster():
    """Bare ground 1, fully planted ground PLANT_WEATHER (from NPP_WEATHER up)."""
    f = earth.plant_factor(np.array([0.0, 0.5 * earth.NPP_WEATHER, earth.NPP_WEATHER, 3 * earth.NPP_WEATHER]))
    assert np.allclose(f, [1.0, 0.5 * (1 + earth.PLANT_WEATHER), earth.PLANT_WEATHER, earth.PLANT_WEATHER])


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
    g = 3.0 / np.log(2.0)
    assert earth.co2_term(P, 50.0) < g * (earth.CO2_LOG + earth.CO2_SAT) + 1e-9  # the maximum greenhouse
    assert earth.co2_term(P, -50.0) > -g * earth.CO2_MAX - 1e-9
    assert np.isclose(at(0.9e5), 3.0 * np.log2(0.9e5 / climate.PCO2_REF))  # logarithmic up to ~0.1 bar (v1-finish-14)
    assert at(1e6) < 3.0 * np.log2(1e6 / climate.PCO2_REF) - 1.0


def test_references_are_kept_after_the_spin_up():
    """The source and sink references stop learning at REF_FREEZE (set once, PW-576)."""
    from planet.grid import build_grid
    from planet.tectonics import Params, Simulation
    s = Simulation(build_grid(3), 1, Params(), 2.0)
    s.run(earth.REF_FREEZE + 2)
    ref = s.refs.copy()
    s.run(s.t + 20)
    assert np.array_equal(s.refs, ref)
