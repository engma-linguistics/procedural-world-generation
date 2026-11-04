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


def test_starvation_law():
    """PW-1227: below the vegetation's CO2 floor the weathering sink's plants starve by the model's own C3
    quantum yield; at and above it nothing changes."""
    from planet import climate, vegetation
    fl = vegetation.CO2_FLOOR
    assert np.isclose(fl, 123.74, atol=0.01)
    t = np.array([0.0, 10.0, 20.0, 30.0])
    assert np.all(vegetation.starvation(t, fl)[0] == 1.0) and np.all(vegetation.starvation(t, 600.0)[0] == 1.0)
    assert np.allclose(vegetation.starvation(t, fl * 0.999)[0], 1.0, atol=0.01)  # continuous at the floor
    ratio = vegetation._q3(t, 0.7 * 60.0) / vegetation._q3(t, 0.7 * fl)
    assert np.allclose(vegetation.starvation(t, 60.0)[0], np.maximum(ratio, 0.0))
    assert np.all(vegetation.starvation(t[1:], 20.0)[0] == 0.0)  # below the compensation point (14 ppm Ci)
    assert vegetation.starvation(0.0, 20.0)[0] > 0.0  # (lower in the cold: 0 C's is ~10 ppm)
    # the law: unchanged at and above the floor, continuous through it, its slope consistent with it
    starve = (np.array([0.5, 0.47]), np.array([12.0, 22.0]))
    xf = fl / climate.PCO2_BALANCE
    for x in (xf, 0.5, 1.0, 3.0):
        assert earth.co2_law(x, 0.03, starve) == earth.co2_law(x, 0.03)
        assert earth.co2_slope(x, 0.03, starve) == earth.co2_slope(x, 0.03)
    assert np.isclose(earth.co2_law(xf * 0.9999, 0.03, starve), earth.co2_law(xf, 0.03), rtol=1e-3)
    for x in (0.2, 0.1, 0.07):
        h = 1e-5
        num = (np.log(earth.co2_law(x * np.exp(h), 0.03, starve))
               - np.log(earth.co2_law(x * np.exp(-h), 0.03, starve))) / (2 * h)
        assert np.isclose(earth.co2_slope(x, 0.03, starve), num, rtol=1e-4)
        assert earth.co2_law(x, 0.03, starve) < earth.co2_law(x, 0.03)
    # with the plants' enhancement all gone, planted ground weathers 1 / PLANT_WEATHER of its planted rate
    assert np.isclose(earth.co2_law(0.02, 0.0, (np.array([1.0]), np.array([25.0]))),
                      (2 * 0.02 / 1.02) ** earth.WEATHER_FERT / earth.PLANT_WEATHER)
    # the stock settles where the starving law takes up the source
    c = np.log(0.1)
    for _ in range(50):
        c = earth.co2_stock(c, 0.2, 1.0, 2.0, 0.03, starve=starve)
    assert np.isclose(earth.co2_law(np.exp(c), 0.03, starve), 0.2, rtol=1e-6)


def test_starvation_lane94_offline_table():
    """Lane 94's offline closed loop for draw l6fix 639472 over 930-1000 Myr (docs/review/v1-cut/
    co2-crash-diagnosis.md s2): source ln -1.29, the sink's other parts ln -0.04, its net climate gain 0.044 per C,
    the episode's 3.9 C of dT per e-fold of CO2, from X 1.06; bare share 3%. The planted cells as two temperatures
    that give the diagnosis's sink-weighted starvation (3% at 35 ppm, 13% at 50). Its table: 38 ppm as the run
    is, 73 ppm with the plants starving (no C4 rescue), 84 with that and the design gain 0.070."""
    from planet import climate, vegetation
    starve = (np.array([0.3, 0.7]) * 0.97, np.array([12.0, 20.5]))
    for ppm, share in ((35.0, 0.03), (50.0, 0.13)):
        q = float((starve[0] * vegetation.starvation(starve[1], ppm)[0]).sum() / 0.97)
        assert abs(q - share) < 0.005
    x0 = 1.06

    def end_ppm(gain, sv):
        def f(u):
            return (-0.04 + gain * 3.9 * (u - np.log(x0)) + 1.29
                    + np.log(earth.co2_law(np.exp(u), 0.03, sv) / earth.co2_law(x0, 0.03)))
        lo, hi = -8.0, 1.0
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
        return climate.PCO2_BALANCE * np.exp(lo)
    assert 33 < end_ppm(0.044, None) < 43  # lane 94: 38
    assert 65 < end_ppm(0.044, starve) < 82  # lane 94: 73
    assert 76 < end_ppm(0.070, starve) < 92  # lane 94: 84


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
    """Bare ground 1, ground fully under rooted plants PLANT_WEATHER, in proportion to the cover between (PW-1424 C)."""
    f = earth.plant_factor(np.array([0.0, 0.5, 1.0, 1.2]))
    assert np.allclose(f, [1.0, 0.5 * (1 + earth.PLANT_WEATHER), earth.PLANT_WEATHER, earth.PLANT_WEATHER])


def test_rooted_cover_leaves_out_mosses():
    """The weathering's plant factor reads the rooted (vascular) plants' cover: mosses and crusts don't count."""
    from planet import vegetation as V
    nu = np.zeros((V.NP, 3))
    nu[V.IDX["C3G"], 0] = 0.6
    nu[V.IDX["TeBS"], 0] = 0.3
    nu[V.IDX["Moss"], 1] = 0.9
    nu[V.IDX["TeBS"], 2], nu[V.IDX["C3G"], 2] = 0.7, 0.4  # (a sum over 1 is capped)
    assert np.allclose(V.rooted_cover(nu), [0.9, 0.0, 1.0])


def test_sink_reference_is_one_yardstick_after_the_spin_up():
    """PW-1424 A: after REF_FREEZE the sink's reference is the source's over exp(YARDSTICK[level]), whatever was
    learnt; up to it the learnt pair."""
    class G:
        level = 6

    class S:
        grid = G
        refs = np.array([100.0, 40.0])
        t = earth.REF_FREEZE
    assert np.allclose(earth.references(S), [100.0, 40.0])
    S.t = earth.REF_FREEZE + 2.0
    assert np.allclose(earth.references(S), [100.0, 100.0 * np.exp(-earth.YARDSTICK[6])])
    assert np.allclose(S.refs, [100.0, 40.0])  # (the learnt pair is kept)
    G.level = 8  # (a level without its own: the nearest's)
    assert np.isclose(earth.references(S)[1], 100.0 * np.exp(-earth.YARDSTICK[7]))
    G.level = 3
    assert np.isclose(earth.references(S)[1], 100.0 * np.exp(-earth.YARDSTICK[6]))


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


def test_sink_is_continuous_into_the_finish_window():
    """The sink's erosion supply is kept per step of dt by the step it was eroded in (earth.erode): the first
    0.5 Myr finish-window step must not read the last 2 Myr step's erosion x dt / dt_now = 4 (lane 67: a 4.3x
    sink for one step crashed every run's CO2 to 3-50 ppm at the window's start)."""
    from helpers import run_sim

    s = run_sim(level=4, seed=2, myr=32.0, run_end=44.0)  # (the window starts at 34)
    s.step()
    assert s.dt_now == 2.0 and abs(s.t - 34.0) < 1e-9
    before = s.rates[1]
    s.step()
    assert s.dt_now == 0.5
    assert 0.7 < s.rates[1] / before < 1.4
