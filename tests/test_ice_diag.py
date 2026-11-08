"""The opt-in ice diagnostics (tectonics/diag.py, PW-555) only read the run, and the whole-history ice
criteria (tools/ice_criteria.py) judge spells as documented."""

import numpy as np

from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet.tectonics.diag import Recorder
from tools import ice_criteria as C


def _run(diag: bool, myr=24.0):
    sim = Simulation(build_grid(4), 1, Params(run_end=myr, climate_offset=-6.0, finish_window=0.0), 2.0)
    if diag:
        sim.diag = Recorder(fields=True)
    sim.run(myr, (lambda s: s.diag.step(s)) if diag else None)
    return sim


def test_diag_is_read_only_and_records():
    a, b = _run(False), _run(True)
    for k in ("w_elev", "ice", "temp", "precip", "flow"):
        assert np.array_equal(getattr(a, k), getattr(b, k)), k
    assert (a.dT, a.sea_level, a.co2, a.drift) == (b.dT, b.sea_level, b.co2, b.drift)
    d = b.diag
    assert len(d.steps) == 12 and len(d.updates) == len(d.fields["t"]) >= 6
    st = d.steps[-1]
    assert abs(st["sea_ice"] + st["sea_tect"] - st["sea_level"]) < 0.02
    # the target's terms add up (CO2 as counted + ice albedo + star + CH4/N2O + offset)
    # (the drift is on the carbon source, PW-819: not a temperature term)
    assert abs(st["co2_term"] + st["albedo_term"] + st["star"] + st["ghg"] + st["offset"] - st["target"]) < 0.01
    s = a.stats()
    assert s["sea_ice_m"] == round(a.sea_ice, 1) and s["sea_tect_m"] == round(a.sea_tect, 1)
    up = [u for u in d.updates if u["sheets"]]
    if up:  # (6 C colder at L4: usually some ice)
        u = up[-1]
        assert u["budget"]["net"] == round(u["budget"]["acc"] - u["budget"]["melt"] - u["budget"]["sea"], 4) or \
            abs(u["budget"]["net"] - (u["budget"]["acc"] - u["budget"]["melt"] - u["budget"]["sea"])) < 1e-3
        assert sum(sh["vol_m"] for sh in u["sheets"]) + u["other"]["vol_m"] == \
            __import__("pytest").approx(-u["sea_ice"], rel=0.02, abs=0.5)


def _track(sea_ice, iced_land, dT=None):
    t = np.arange(len(sea_ice)) * C.EVERY + C.EVERY
    dT = np.zeros(len(t)) if dT is None else dT
    return {"steps": [{"t": float(a), "sea_ice": float(b), "sea_tect": 0.0, "dT_end": float(c), "iced_land": float(e)}
                      for a, b, c, e in zip(t, sea_ice, dT, iced_land)]}


def test_criteria_spells_and_bars():
    n = 250  # 1 Gyr of climate updates, t = 4..1000 Myr
    si, il = np.zeros(n), np.full(n, 0.03)  # (mountain ice on 3% of the land: not an icehouse)
    si[100:130] = -60.0  # an icehouse 404-520 Myr ...
    si[110] = 0.0  # ... with a 4 Myr flicker inside (joined) ...
    si[111:121] = -300.0  # ... and a deep era 448-484 Myr
    r = C.evaluate(_track(si, il), spinup=100.0)
    assert r["icehouse"]["eras"] == 1 and r["icehouse"]["longest"] == 120.0
    assert r["deep"]["longest"] == 40.0 and r["pass"], r["fails"]
    si[30:60] = -40.0  # a second icehouse 124-240 Myr
    r = C.evaluate(_track(si, il), spinup=100.0)
    assert r["icehouse"]["gaps"] == [160.0] and r["pass"]
    # too little time in an icehouse fails the share
    r = C.evaluate(_track(np.where(np.arange(n) == 200, -60.0, 0.0), il), spinup=100.0)
    assert any("icehouse" in f for f in r["fails"])
    # ... but only on a window long enough to hold an ice age (PW-709): a 500 Myr run isn't judged on the floor
    r = C.evaluate(_track(np.zeros(125), il[:125]), spinup=100.0)
    assert r["pass"] and not r["icehouse"]["floor_judged"], r["fails"]
    r = C.evaluate(_track(np.full(125, -60.0), il[:125]), spinup=100.0)  # the cap is judged on any window
    assert any("icehouse" in f for f in r["fails"])
    # a deep era that never ends fails the new bar; the old bar sees only depth
    si[150:] = -200.0
    r = C.evaluate(_track(si, il), spinup=100.0)
    assert not r["pass"] and any("deep era" in f for f in r["fails"]) and r["old"]["pass"]


def test_ice_terms_icehouse_glacial_max_frozen_over():
    """The owner's three ice terms (2026-10-30, PW-1091): frozen over is 40%+ of the land under ice."""
    si = np.array([0.0, -30.0, -60.0, -10.0])
    warm = C.ice_terms(si, np.array([0.02, 0.05, 0.1, 0.03]))
    assert warm["icehouse"] and not warm["glacial_max"] and not warm["frozen_over"]
    lgm = C.ice_terms(si, np.array([0.02, 0.25, 0.1, 0.03]))
    assert lgm["glacial_max"] and not lgm["frozen_over"]
    peak = C.ice_terms(si, np.array([0.02, 0.3, 0.4, 0.03]))  # (40% at a moment, not at the end: reported, PW-1425)
    assert not peak["frozen_over"] and peak["frozen_peak"] and peak["glacial_max"] and peak["land_ice_peak"] == 40.0
    frozen = C.ice_terms(si, np.array([0.02, 0.3, 0.4, 0.41]))
    assert frozen["frozen_over"] and frozen["frozen_end_n"] == 2
    assert C.ice_terms(np.zeros(4), None)["never_ice"] and C.ice_terms(si, None)["frozen_over"] is None


def test_frozen_peak_counts_only_under_a_near_final_star():
    """Owner 2026-10-30 (PW-1142): the hard window is where the star's forcing is within FINAL_STAR_C of the finish's
    and within the run's last FINAL_MYR, whichever starts later; the window's peak is reported (frozen_peak), earlier
    frozen spells too (frozen_over_any); frozen over itself is the end (PW-1425)."""
    t = np.arange(300.0, 1001.0, 4.0)
    star = -11.0 * (1000.0 - t) / 1000.0  # (brightening to 0 at the end: within 2 C from ~818 Myr)
    hard, start, which = C.hard_window(t, star)
    assert which == "star" and 815 < start < 822 and hard[-1] and not hard[0]
    hard, start, which = C.hard_window(t, None)  # (no star recorded: the last 300 Myr)
    assert which == "last 300 Myr" and start == 700.0
    hard, start, which = C.hard_window(t, np.zeros_like(t))  # (a steady star: the last 300 Myr is narrower)
    assert which == "last 300 Myr" and start == 700.0
    si = np.full(len(t), -30.0)
    il = np.full(len(t), 0.1)
    il[(t >= 600) & (t < 640)] = 0.45  # a dim-star frozen spell
    terms = C.ice_terms(si, il, hard=C.hard_window(t, star)[0])
    assert not terms["frozen_over"] and not terms["frozen_peak"] and terms["frozen_over_any"]
    il[-3:] = 0.42  # frozen at the end, under a near-final star
    terms = C.ice_terms(si, il, hard=C.hard_window(t, star)[0])
    assert terms["frozen_over"] and terms["frozen_peak"] and terms["frozen_over_any"] and terms["frozen_end_n"] == 3
