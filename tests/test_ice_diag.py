"""The opt-in ice diagnostics (tectonics/diag.py, PW-555) only read the run, and the whole-history ice
criteria (tools/ice_criteria.py) judge spells as documented."""

import numpy as np

from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet.tectonics.diag import Recorder
from tools import ice_criteria as C


def _run(diag: bool, myr=24.0):
    sim = Simulation(build_grid(4), 1, Params(flora_end=myr, climate_offset=-6.0), 2.0)
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
    # the target's terms add up (drift + CO2 as counted + ice albedo + offset)
    assert abs(st["drift"] + st["co2_term"] + st["albedo_term"] + st["offset"] - st["target"]) < 0.01
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
