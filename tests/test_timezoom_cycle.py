"""The glacial index (planet/timezoom/cycle.py, PW-471): its shape on the planet's own orbit, and the
time zoom's response to it on sim4's icehouse moment (level 4, fast)."""

import numpy as np
import pytest

from planet import orbit as O, timezoom as Z
from planet.timezoom.cycle import BETWEEN, BUILDING, ENDING, Index, cooling

import seeds

STEP = 0.5
NO_ORBIT = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean")


def _index(seed=None, tilt=23.44, lat=65.0, kyr=1500.0, **kw):
    p = Z.TZParams(**kw)
    ph = O.orbit_phases(p, 0, earth=True) if seed is None else O.orbit_phases(p, seed, earth=False)
    return Index(p, STEP, int(kyr / STEP), tilt, ph, lat), p


@pytest.mark.parametrize("seed, tilt, lat", [(None, 23.44, 65.0), (11400, 23.4, 63.0), (2620, 23.4, -60.0),
                                             (3500, 20.0, 58.0), (5260, 28.0, 55.0)])
def test_index_is_a_100_kyr_sawtooth(seed, tilt, lat):
    """On Earth's orbit and seeded ones: cycles of ~100 kyr (80-120 on Earth's; a seeded orbit sometimes
    skips a precession peak), each a slow build (> 60 kyr) and a fast
    ending (end_kyr), between 0 and 1; the start is an interglacial."""
    ix, p = _index(seed, tilt, lat)
    s = ix.summary()
    assert ix.I[0] == 0.0 and ix.I.min() >= 0.0 and ix.I.max() <= 1.0
    assert len(s["endings"]) >= 12 and s["backstops"] == 0
    c = np.array(s["cycle_kyr"])
    assert 90.0 <= np.median(c) <= 115.0 and c.min() >= 80.0 and c.max() <= (120.0 if seed is None else 140.0), c
    for e in s["endings"][:-1]:
        assert e["age_kyr"] > 60.0 and e["I"] >= p.end_min
        assert e["kyr"] <= p.end_kyr + STEP
    # the shape: I rises in small steps and falls in big ones (1/end_kyr per kyr)
    d = np.diff(ix.I)
    assert d.max() < 0.25 * STEP / p.end_kyr * 4 and np.isclose(d.min(), -STEP / p.end_kyr)
    assert (d[ix.modes[1:] == BUILDING] >= 0).all() and (ix.I[ix.modes == BETWEEN] == 0).all()


def test_endings_come_at_sunshine_peaks():
    """An ending starts when I is high and the summer sun beats a bar that falls with the glacial's age
    (Huybers 2011), within the planet's own percentiles."""
    ix, p = _index()
    for e in ix.endings:
        assert ix.q_lo - 1e-9 <= e["bar"] <= ix.q_hi + 1e-9 and e["sun"] >= e["bar"] and not e["backstop"]
        i = int(round(e["t"] / STEP))
        assert ix.modes[i] == BUILDING and ix.modes[i + 1] == ENDING


def test_no_orbit_or_off_means_no_ice_age():
    """An orbit with no swing never builds (all its percentiles are one value); index=off neither."""
    ix, _ = _index(**NO_ORBIT)
    assert (ix.I == 0).all() and not ix.endings
    ix, _ = _index(index="off")
    assert (ix.I == 0).all() and not ix.builds


def test_cooling_is_planet_relative():
    """glacial_cool at Earth's share of land poleward of the snowline, in proportion, capped; or by hand."""
    p = Z.TZParams()
    assert cooling(p, p.glacial_f) == pytest.approx(p.glacial_cool)
    assert cooling(p, 0.5 * p.glacial_f) == pytest.approx(0.5 * p.glacial_cool)
    assert cooling(p, 0.0) == 0.0 and cooling(p, 10 * p.glacial_f) == pytest.approx(p.glacial_cap * p.glacial_cool)
    assert cooling(Z.TZParams(glacial_dt=2.0), p.glacial_f) == 2.0


@pytest.fixture(scope="module")
def icehouse(sim4):
    """sim4's moment as _icehouse makes it."""
    return _icehouse(Z.source_from_sim(sim4))


def _icehouse(src):
    """A moment 4 C colder, 200 kyr with the index (6 C at a glacial maximum, by hand: L4's planet is
    small) and without it; the plants local only, so dT_global is the index's alone."""
    src = dict(src)
    src["dT"] = src["dT"] - 4.0
    kw = dict(veg="local", phases="0,90,0,90")
    return [Z.simulate(src, kyr=200, step=STEP, every=2.0, params=Z.TZParams(index=i, glacial_dt=6.0, **kw))
            for i in ("on", "off")]


def test_zoom_climate_follows_the_index(icehouse):
    """dT_global = -I x the glacial cooling (no CO2 or ice-albedo feedback of the zoom's own)."""
    on, off = icehouse
    dT = np.array([f["stats"]["dT_global"] for f in on["frames"]])
    I = np.array([f["stats"]["glacial_index"] for f in on["frames"]])
    assert on["cycle"]["cooling_c"] == 6.0 and I.max() > 0.8
    assert np.allclose(dT, -6.0 * I, atol=0.01)
    assert all(f["stats"]["dT_global"] == 0.0 for f in off["frames"])


def test_glacials_grow_ice_and_endings_melt_it_fast(sources4):
    """The ice follows the index: lower seas at a glacial maximum than without it, and an ending gives
    back most of the glacial's extra ice within 15 kyr. On each of the L4 worlds (seeds.SEEDS4) made an
    icehouse (_icehouse), at least seeds.PASS_RATE of them (one world is a chaotic run's draw: PW-638)."""
    seeds.check_rate("glacial endings", seeds.run_case(_endings_case, sources4))


def _endings_case(src, out):
    """One world's assertions (as the single-seed test on sim4's icehouse had them); its numbers in out."""
    on, off = _icehouse(src)
    t = np.array([f["t"] for f in on["frames"]])
    sl_on = np.array([f["stats"]["sea_level_change_m"] for f in on["frames"]])
    sl_off = np.array([f["stats"]["sea_level_change_m"] for f in off["frames"]])
    e = on["cycle"]["endings"][0]
    i, j = np.searchsorted(t, e["t"]), np.searchsorted(t, e["t"] + 15.0)
    extra = sl_off[i] - sl_on[i]
    out.update(run_dT=float(src["dT"]), ending_kyr=float(e["t"]), extra_m=float(extra),
               left_m=float(sl_off[j] - sl_on[j]))
    assert extra > 10.0
    assert sl_off[j] - sl_on[j] < 0.5 * extra
