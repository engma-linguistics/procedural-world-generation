"""Faiths that come through towns (PW-1528): inside a realm, a tolerant ruler's towns draw the realm's other faiths, which settle and spread."""
import numpy as np
import pytest

from planet.lineages import gods as G
from test_faith_spread import KNOW, S0, S1, TEMPLE


def realm(P, frames, tol_ruler, urban=None, start=10.0, dt=0.2, know=(KNOW, KNOW)):
    """Culture 1 rules all of culture 0 (and all of its own land) for `frames` frames, each frame one polity step."""
    prev = None
    for k in range(frames):
        ago = start - k * dt
        rs = [(ago, [(1, [(0, 1.0)], False, 1.0)])] if prev is not None else ()
        P.att.rel[1] = tol_ruler  # (held fixed: the test is about the ruler's tolerance, not its drift)
        P.frame(ago, {0: {"sal": S0, "know": know[0], "people": "human"}, 1: {"sal": S1, "know": know[1], "people": "human"}},
                contacts={(0, 1)}, where={0: (100, np.array([1.0, 0, 0])), 1: (100, np.array([0, 1.0, 0]))}, rule_steps=rs, step_kyr=dt, urban=urban)
        prev = ago


def test_protection_mirrors_the_rulers_push():
    assert G.protection(1.0) == pytest.approx(1.0)
    assert G.protection(0.0) == pytest.approx(G.TAU_FORCED / G.TAU_TOLERANT)
    assert G.protection(0.3) < G.protection(0.5) < G.protection(0.7) < G.protection(0.9)


def test_a_tolerant_realms_towns_draw_its_other_faiths_and_an_intolerant_ones_hardly():
    def target(tol, urban):
        P = G.Pantheons(seed=1)
        realm(P, 2, tol, {0: 0.0, 1: 0.0})
        P.att.urban = urban
        P.att.rel[0] = 0.7
        P.cells = {0: 100, 1: 100}
        t = P._towns({(0, 1): (1.0, 1.0)}, [(1, [(0, 1.0)], False, 1.0)])
        return t.get(0, {}).get(P.faith_of[1], 0.0)
    hi, lo = target(0.9, {0: 0.1, 1: 0.1}), target(0.1, {0: 0.1, 1: 0.1})
    assert hi > 0.01 and hi > 20 * lo  # (a tenth in towns, half the realm of another faith, a tolerant ruler: a few percent)
    assert target(0.9, {0: 0.0, 1: 0.1}) == 0.0  # (no towns, no door)
    assert 0 < target(0.9, {0: 0.05, 1: 0.1}) < hi  # (it grows with the town share)


def test_town_faiths_settle_and_spread_under_a_tolerant_ruler_and_leave_the_majority_history_alone():
    def run(tol, on):
        G.TOWNS_ON = on
        try:
            P = G.Pantheons(seed=0)
            realm(P, 2, tol, {0: 0.0, 1: 0.0})
            P.att.rel[0] = 0.8
            realm(P, 30, tol, {0: 0.08, 1: 0.08}, start=9.8, dt=0.2)
        finally:
            G.TOWNS_ON = True
        return P
    tol_on, tol_off = run(0.95, True), run(0.95, False)
    assert tol_on.fhist == tol_off.fhist  # (read-out only: the same draws, the same majority faiths)
    assert [e for e in tol_on.events if e["kind"] == "conversion"] == [e for e in tol_off.events if e["kind"] == "conversion"]
    f1 = tol_on.faith_of[1]
    assert tol_on.faith_of[0] != f1  # (this draw: the subject keeps its own faith; the harsh ruler converts it outright)
    got = tol_on.comp[0].get(f1, 0.0)
    assert got > tol_off.comp[0].get(f1, 0.0) + 0.005
    assert tol_on.towns_doc(0) and tol_on.towns_doc(0)[0][0] == f1
    assert sum(v for _, v in tol_on.comp[0].items()) == pytest.approx(1.0)
    assert tol_on.comp[0][tol_on.faith_of[0]] >= 0.5


def test_a_closed_faith_keeps_to_its_quarter():
    P = G.Pantheons(seed=2)
    realm(P, 2, 0.95, {0: 0.0, 1: 0.0})
    P.closed.add(P.faith_of[1])
    P.att.urban = {0: 0.1, 1: 0.1}
    P.cells = {0: 100, 1: 100}
    P._towns({(0, 1): (1.0, 1.0)}, [(1, [(0, 1.0)], False, 1.0)])
    f1 = P.faith_of[1]
    assert (0, f1) not in P.spread  # (it settles in the towns but wins no one about them)
