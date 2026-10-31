"""Niche learning (PW-1155): fixed body limits (spec limits, never), a cultural preference that widens at a pressed frontier, and the
record of learned country for the demes."""

from __future__ import annotations

import numpy as np
import pytest

from planet import store as S
from planet.lineages import recent as R
from planet.lineages import spec as SP
from planet.lineages import history as H
from planet.lineages.history import habitat as HB
from planet.lineages.history import params as PM
from planet.lineages.history.tags import _tags

from test_lineages import _fake_timezoom


@pytest.fixture
def faketz(tmp_path):
    old = S.root()
    tz = _fake_timezoom(tmp_path)
    yield tz
    S.set_root(old)


def _tree(**extra):
    # (a narrow-niche people alone on the world: cool forest folk; a megafauna kind; a cold-limited, sea-bound kind)
    return SP.parse({"meta": {"name": "n", "seed": 2}, "lineage": [
        {"id": "elf", "origin": "root", "at": "36 kyr", "temp_c": [10, 16], "rain_mm": [100, 9000], "prefers": ["forest"], "density": 2,
         **extra},
        {"id": "wyrm", "origin": "root", "at": "36 kyr", "temp_c": [0, 30], "rain_mm": [100, 9000], "megafauna": True},
        {"id": "turtle", "origin": "root", "at": "36 kyr", "temp_c": [18, 26], "rain_mm": [100, 9000], "traits": ["swims", "coastal"],
         "limits": {"cold_c": 1}, "never": [{"what": "coast", "is": "absent"}, {"what": "polar"}]},
        {"id": "hatchling", "parents": ["turtle"], "at": "20 kyr", "limits": {"heat_c": 2}}]})


def test_limits_and_never_parse_inherit_validate_and_round_trip():
    t = _tree()
    tu, ha = t.lines["turtle"], t.lines["hatchling"]
    assert tu.limits == {"cold_c": 1.0} and ("coast", "absent") in tu.never and ("polar", "present") in tu.never
    assert ha.limits == {"cold_c": 1.0, "heat_c": 2.0} and ha.never == tu.never  # (the body is inherited, a child adds its own)
    back = SP.parse(SP.to_raw(t))
    assert back.lines["hatchling"].limits == ha.limits and back.lines["turtle"].never == tu.never
    for bad in ({"limits": {"wings": 1}}, {"limits": {"cold_c": -1}}, {"never": [{"what": "lava"}]}, {"never": [{"what": "coast", "is": "maybe"}]}):
        with pytest.raises(ValueError):
            _tree(**bad)
    assert HB.learns(t.lines["elf"]) and not HB.learns(t.lines["wyrm"])  # (megafauna keep to their lane)
    assert not HB.learns(SP.parse({"meta": {"name": "x"}, "lineage": [
        {"id": "a", "origin": "root", "at": "1 kyr", "limits": {"learn": 0}}]}).lines["a"])


def test_body_limits_are_wider_than_the_preference_and_never_is_hard(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    env = ps.fields(0.0, variability=False)
    t = _tree()
    g = ps.grid
    tags = _tags(g, env, False)
    elf, tu = t.lines["elf"], t.lines["turtle"]
    K0, T = HB.capacity(elf, env, tags), HB.tolerance(elf, env, tags)
    land = tags["land"]
    assert (T[land] >= K0[land] - 1e-9).all()  # (the body allows at least what the culture prefers)
    assert (T[land] > 0.3).sum() > 1.5 * (K0[land] > 0.3).sum()  # (and more: the margins the culture can learn)
    Tt = HB.tolerance(tu, env, tags)
    assert (Tt[land & ~tags["coast"]] == 0).all()  # (never away from the coast)
    temp = env["temperature"]
    assert (Tt[land & (temp < 18 - 1 - 4)] == 0).all()  # (an ectotherm: 1 C below its comfort, plus the soft edge, and no further)
    assert (HB.never_ok(tu, env, tags)[land & ~tags["coast"]] == 0).all()


def test_a_pressed_people_learns_its_margins_slowly_and_megafauna_never(faketz, monkeypatch):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    t = _tree()
    monkeypatch.setattr(PM, "LEARN", False)
    h0 = H.History(t, ps, 1)
    r0 = h0.run()
    assert not h0._L  # (off: nothing learned, the habitat as the tree gives it)
    monkeypatch.setattr(PM, "LEARN", True)
    h1 = H.History(t, ps, 1)
    r1 = h1.run()
    e = h1.idx["elf"]
    assert e in h1._L and h1.idx["wyrm"] not in h1._L
    L = h1._L[e]
    K0, T = h1._learn_in[e]
    held = r1["present"][e] >= H.EST
    learned = held & (L >= PM.LEARNED_MIN) & (K0 < 0.3)
    assert learned.any()  # (the elves live on country their culture alone would not have them in)
    assert held.sum() > (r0["present"][h0.idx["elf"]] >= H.EST).sum()
    assert (L <= 1.0).all() and (L >= 0).all()
    assert r1["frames"][-1]["peoples_learned"].max() > 0 and "learned" in r1["frames"][-1]["stats"]
    tu = h1.idx["turtle"]
    assert not (r1["present"][tu] >= H.EST)[~h1._tags_now["coast"] & h1._tags_now["land"]].any()  # (the sea folk stay on the coast)
