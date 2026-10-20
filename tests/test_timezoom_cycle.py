"""The time zoom's ice-age cycle (planet/timezoom/cycle.py, PW-440): its state machine on a made-up sea
level, and on sim4's icehouse moment (level 4, fast): out of the way between ice ages, and an ending
melts the ice back faster than without it."""

import numpy as np
import pytest

from planet import orbit as O, timezoom as Z
from planet.timezoom.cycle import BETWEEN, BUILDING, ENDING, Cycle

STEP = 0.5


def _cycle(**kw):
    p = Z.TZParams(**kw)
    c = Cycle(p, STEP, 600.0, 23.44, O.orbit_phases(p, 0, earth=True), scale_m=70.0)
    c.setup(65.0)
    return c, p


def _feed(c, sl, until=None):
    """Step the cycle through sl (m per step, continuing its step count); stop early at mode `until`."""
    for x in sl:
        c.step(len(c.modes), float(x))
        if c.modes[-1] == until:
            break
    return np.array(c.modes)


def test_ending_needs_big_ice_and_a_sunshine_peak():
    """A slow build: building starts at a low of the summer sun, the ending only once the extra ice
    passes end_min AND the sun beats the bar (which falls with the glacial's age); then hysteresis: it
    runs on through small regrowth until the ice is back near the interglacial level."""
    c, p = _cycle()
    n = int(400 / STEP)
    t = np.arange(n) * STEP
    sl = -0.8 * t  # 0.8 m/kyr of growth: no ending can come before end_min x 70 m = 28 m, at 35 kyr
    modes = _feed(c, sl, until=ENDING)
    assert modes[0] == BETWEEN and BUILDING in modes and modes[-1] == ENDING
    e = c.endings[0]
    i = int(round(e["t"] / STEP))
    assert e["extra_m"] >= p.end_min * 70.0 - 1e-6
    assert c.q[i] >= c.q_lo  # (the bar never falls below bar_lo)
    assert not e["backstop"]
    # hysteresis: from the glacial's level the ice melts, regrows 10 m, melts on: still one ending
    lvl = sl[i]
    back = np.concatenate([np.linspace(lvl, lvl * 0.6, 20), np.linspace(lvl * 0.6, lvl * 0.7, 10),
                           np.linspace(lvl * 0.7, 0, 30)])
    modes = _feed(c, back)
    tail = modes[i:]
    assert len(c.endings) == 1 and tail[0] == ENDING and tail[-1] == BETWEEN and (np.diff(tail) <= 0).all()
    assert c.endings[0]["kyr"] < 30.0
    assert c.backstops == 0


def test_no_ending_without_big_ice():
    """Ice that stays under end_min never ends by the sun; past backstop x glacial_kyr the next peak
    ends it (counted)."""
    c, p = _cycle()
    n = int(560 / STEP)
    sl = -np.minimum(np.arange(n) * STEP * 0.5, 20.0)  # 20 m of extra ice at most (< 28 m)
    _feed(c, sl)
    assert c.backstops >= 1 and all(x["backstop"] for x in c.endings)
    assert all(x["age_kyr"] > p.backstop * p.glacial_kyr for x in c.endings)


def test_off_or_between_is_unchanged():
    c, _ = _cycle(cycle="off")
    _feed(c, -np.arange(400) * 0.5)
    assert set(c.modes) == {BETWEEN} and c.r == 0.0 and c.boost(1.8, -100.0) == 1.0
    assert c.co2_target(-1.0, -100.0) == -1.0


@pytest.fixture(scope="module")
def icehouse(sim4):
    """sim4's moment 8 C colder, 240 kyr with and without the cycle."""
    src = Z.source_from_sim(sim4)
    src["dT"] = src["dT"] - 8.0
    return [Z.simulate(src, kyr=240, step=STEP, every=10.0, params=Z.TZParams(cycle=c)) for c in ("on", "off")]


def test_cycle_stays_out_of_the_way_until_an_ending(icehouse):
    """Between ice ages and while building, the time zoom is exactly as without the cycle."""
    on, off = icehouse
    ends = on["cycle"]["endings"]
    assert ends, "no ending: the test moment no longer glaciates enough"
    i = int(round(ends[0]["t"] / STEP))
    assert np.array_equal(on["series"][:i], off["series"][:i])
    assert not np.array_equal(on["series"], off["series"])


def test_ending_melts_back_faster(icehouse):
    """In the 20 kyr after they start, endings give back more ice than the same sunshine peaks do
    without the cycle."""
    on, off = icehouse
    d = []
    for e in on["cycle"]["endings"]:
        i, j = int(round(e["t"] / STEP)), int(round((e["t"] + 20) / STEP))
        if j < len(on["series"]):
            d.append((on["series"][j, 1] - on["series"][i, 1]) - (off["series"][j, 1] - off["series"][i, 1]))
    print("ending rise vs no cycle, m:", np.round(d, 1))
    assert d and np.mean(d) > 2.0
