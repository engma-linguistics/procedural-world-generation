"""The coarser nested grid's climate (planet/nest.py, PW-247) and the run's climate cadence (earth.climate_cadence)."""

import numpy as np
import pytest

from planet import climate, nest
from planet.grid import build_grid
from planet.ocean import cell_area_km2
from planet.tectonics import Simulation, earth
from planet.tectonics.params import Params

from helpers import run_sim
from test_golden import sim_digest


def test_restrict_keeps_area_means_and_prolong_is_linear(grid4):
    s = nest.step(grid4)
    c = s["coarse"]
    assert c.level == 3 and np.array_equal(s["p0"][:c.n], np.arange(c.n))
    f = grid4.centers[:, 0] + 2.0
    r = nest._restrict(s, f)
    a4, a3 = cell_area_km2(grid4), cell_area_km2(c)
    assert abs((a4 * f).sum() / a4.sum() - (a3 * r).sum() / a3.sum()) < 2e-3
    assert np.allclose(nest._restrict(s, np.full(grid4.n, 7.0)), 7.0)
    # a linear field comes back to within its curvature over a cell
    back = nest._prolong(s, c.centers[:, 0] + 2.0)
    assert np.abs(back - f).max() < 0.02


def test_coarse_climate_is_close_to_the_native_one(sim4_60):
    s, g = sim4_60, sim4_60.grid
    e = s.w_elev
    land = e > 0
    ice = np.where(land, s.ice, 0.0)
    a = climate.compute(g, e, s.dT, s.params.tilt, ice)
    b = nest.climate_coarse(g, 3, e, s.dT, s.params.tilt, ice)
    for k in ("temp", "t_warm", "t_cold", "precip", "runoff", "sst"):
        assert b[k].shape == a[k].shape, k
    assert b["wind_jul"].shape == (g.n, 3) and np.abs((b["wind_jul"] * g.centers).sum(1)).max() < 1e-9
    w = cell_area_km2(g) * land
    assert abs(((a["temp"] - b["temp"]) * w).sum() / w.sum()) < 1.0
    # (plumbing, not accuracy: L3's ~500 km cells rain ~20% less on L4's land; L6 on L7 is measured in
    # docs/review/speed/README.md)
    assert abs((b["precip"] * w).sum() / (a["precip"] * w).sum() - 1) < 0.35
    assert b["rain_state"]["vap"].shape[-1] == build_grid(3).n


def test_cadence_ramps_to_climate_every_before_the_finish_window_and_comes_early_when_dT_moves():
    p = Params(run_end=1000.0)
    sim = Simulation.__new__(Simulation)
    sim.params = p
    for t, k in ((0, 8), (650, 8), (700, 8), (900, 8), (965, 4), (979, 4), (980, 2), (989, 2)):
        sim.t = float(t)
        assert earth.climate_cadence(sim) == k, t
    # the adaptive part: early once dT moved climate_adapt_dT since the last update
    sim.t, sim.climate_t, sim.precip, sim.dT = 102.0, 96.0, np.zeros(1), 0.5
    sim.climate_in = {"dT": 0.0}
    assert not earth.climate_due(sim)
    sim.dT = -1.2
    assert earth.climate_due(sim)
    sim.params = Params(run_end=1000.0, climate_every=4.0, climate_every_max=4.0, climate_ramp_fine=0.0)
    for t in (0.0, 985.0):
        sim.t = t
        assert earth.climate_cadence(sim) == 4  # (main's fixed 4 Myr before PW-247)


def test_fine_stage_updates_every_step_in_the_last_10_myr_before_the_finish_window():
    """The ramp's fine end (owner 10-29): 8 -> 4 -> 2 Myr, so every 2 Myr step from 980 to the window at 990
    gets its own climate; the 4 Myr stage from 960 and the 8 Myr one before it update on their multiples."""
    sim = Simulation.__new__(Simulation)
    sim.params = Params(run_end=1000.0, climate_adapt_dT=0.0)
    sim.precip, sim.climate_in, sim.dT = np.zeros(1), None, 0.0
    sim.climate_t, ups = 950.0, []
    for t in np.arange(952.0, 992.0, 2.0):
        sim.t = float(t)
        if earth.climate_due(sim):
            ups.append(int(t))
            sim.climate_t = sim.t
    assert ups == [952, 960, 964, 968, 972, 976, 980, 982, 984, 986, 988, 990]


def test_coarse_spin_up_hands_over_to_the_run_grid_and_resumes_bit_identical():
    """An L4 run with its spin-up climate on L3: the finish window's climate is the run's own grid's (its rain
    starts from the coarse kernel's state prolonged), and a state taken in the spin-up resumes bit for bit."""
    a = run_sim(level=4, seed=2, myr=20, climate_level=3, run_end=36.0)
    assert a.rain_state["vap"].shape[-1] == build_grid(3).n
    st = a.state()
    a.run(36)
    assert a.rain_state["vap"].shape[-1] == a.grid.n and a.climate_t == a.t
    b = Simulation.from_state(a.grid, a.seed, a.params, a.dt, st)
    b.run(36)
    assert sim_digest(b) == sim_digest(a)


def test_coarse_climate_keeps_the_overturning_total(sim4_60):
    """Per-cell totals (the Sv sinking in a cell) come down as densities: the fine grid's sum is the coarse one's."""
    s, g = sim4_60, sim4_60.grid
    e = s.w_elev
    ice = np.where(e > 0, s.ice, 0.0)
    coarse = nest.chain(g, 3)[-1]["coarse"]
    a = climate.compute(coarse, *(nest._restrict(nest.step(g), f) for f in (e,)), s.dT, s.params.tilt,
                        nest._restrict(nest.step(g), ice))
    b = nest.climate_coarse(g, 3, e, s.dT, s.params.tilt, ice)
    tot_b = float(b["overturning"].sum())
    assert tot_b > 0
    assert abs(tot_b - float(a["overturning"].sum())) < 0.5 * float(a["overturning"].sum())
    # not the per-cell value copied onto 4x the cells
    assert tot_b < 2.0 * float(a["overturning"].sum())


@pytest.mark.slow
def test_the_l7_climate_is_as_arid_and_as_wet_as_its_nested_l6_climate_on_one_ground():
    """PW-1556 (guards PW-290's fix): one ground's climate computed on L7 itself and through nest.climate_coarse on
    L6 (what an L7 run's spin-up uses) gives the same arid share and land rain. A level-dependent rain change would
    pass every L6 check and ship drier L7 showcase worlds: the 10-15 kernel (6926583) made L7 +6 to +8 points more
    arid with 27% less land rain (docs/review/climate/levels/scout1.md). The ground is seed 21's unrun L7 ground
    (no tectonics, ~1 min). Tolerances from measurements (docs/review/climate/levels/pw1556.md): on today's code
    seven unrun grounds gave +1.0 to +1.7 points of Koppen B at L7 (this one +1.0) and land rain within 1.1%;
    scout 221's nine moments of five L7 runs +0.5 to +1.1 and within 2%. The test allows 2.0 points and 5%."""
    g = build_grid(7)
    sim = Simulation(g, 21, Params(run_end=1.0), 2.0)
    e = sim.w_elev
    ice = np.where(e > 0, sim.ice, 0.0)
    a = climate.compute(g, e, sim.dT, sim.params.tilt, ice)
    b = nest.climate_coarse(g, 6, e, sim.dT, sim.params.tilt, ice)
    w = cell_area_km2(g) * ((e > 0) & (ice <= 0))
    arid = [k[0] for k in climate.KOPPEN if k[1].startswith("B")]

    def share(c):
        return 100.0 * float((w * np.isin(c["koppen"], arid)).sum() / w.sum())

    def rain(c):
        return float((w * c["precip"]).sum() / w.sum())

    assert 20.0 < share(b) < 60.0  # (the ground has deserts to lose or gain)
    assert abs(share(a) - share(b)) < 2.0, (share(a), share(b))
    assert abs(rain(a) / rain(b) - 1.0) < 0.05, (rain(a), rain(b))
