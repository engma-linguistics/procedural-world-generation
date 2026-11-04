"""The scholars' horizon by splits and regular correspondences (families.horizon_from, strict_shares): a synthetic world of
three families with known split ages, words replaced and sound laws applied at known rates; no stored run is read."""
from __future__ import annotations

import math

import numpy as np

from planet.language import families as FA
from planet.language.percepts import from_ipa

C_ = list("ptkbdgmnslrwjfvhz")
V_ = list("aeiou")
SEGS = {x: from_ipa(x)[0] for x in C_ + V_}
NC = 100
CONCEPTS = [f"c{i}" for i in range(NC)]  # the scored list
POOL = [f"x{i}" for i in range(250)]  # the rest of the vocabulary, where correspondences are also counted
KEEP = 0.75  # per kyr per line: share of core words not replaced
STEP = 0.5


class _L:
    def __init__(self, id, parent, born, people="human"):
        self.id, self.parent, self.born_kyr, self.died_kyr, self.deme, self.people = id, parent, born, None, 1, people
        self.words, self.roots = {}, {}


def _word(rng):
    return tuple(rng.choice(C_) if k % 2 == 0 else rng.choice(V_) for k in range(2 * int(rng.integers(2, 4))))


def _world(seed=0, top=16.0, splits_per_family=25):
    """Three families from protos at `top` kyr; each family buds splits_per_family lects at ages spread over (0, top); every
    STEP each line replaces each word with probability 1 - KEEP**STEP (a new root) and, with probability 0.5, applies one
    regular sound law (a segment to another of its class) to all its words."""
    rng = np.random.default_rng(seed)
    lects, nroot = [], [0]

    def new_root():
        nroot[0] += 1
        return nroot[0]
    for f in range(3):
        p = _L(f"f{f}", None, top)
        for c in CONCEPTS + POOL:
            p.words[c], p.roots[c] = _word(rng), new_root()
        fam = [p]
        ages = np.sort(rng.uniform(0.25, top - 0.5, splits_per_family))[::-1]
        births = {round(float(a) / STEP) * STEP: k for k, a in enumerate(ages)}
        t = top
        while t > 0:
            t = round(t - STEP, 6)
            for l in fam:
                for c in CONCEPTS + POOL:
                    if rng.random() > KEEP ** STEP:
                        l.words[c], l.roots[c] = _word(rng), new_root()
                if rng.random() < 0.5:
                    cls = C_ if rng.random() < 0.7 else V_
                    a, b = rng.choice(cls, 2, replace=False)
                    l.words = {c: tuple(b if x == a else x for x in w) for c, w in l.words.items()}
            if t in births and t > 0:
                par = fam[int(rng.integers(len(fam)))]
                ch = _L(f"f{f}.{births[t]}", par.id, t)
                ch.words, ch.roots = dict(par.words), dict(par.roots)
                fam.append(ch)
        lects += fam
    return lects


def _form(l, c):
    w = l.words.get(c)
    return tuple(SEGS[x] for x in w) if w else None


def test_split_horizon_near_saturation():
    lects = _world()
    by = {l.id: l for l in lects}
    out = FA.horizon_from(lects, by, CONCEPTS, _form, lambda l, c: l.roots.get(c), people="human", seed=1, pool=POOL)
    # the expected true share across a split t kyr old is KEEP**(2t): the scholars should go blind between the ages where 15%
    # and 3% (SPLIT_EXCESS) of the words survive (3.3-6.1 kyr here); a measure reading chance lookalikes would see past it
    def age(share):
        return math.log(share) / (2 * math.log(KEEP))
    h = out["horizon_kyr"]
    assert h is not None and age(0.15) <= h <= age(FA.SPLIT_EXCESS), (h, out["recovery_by_bin"])
    curve = out["recovery_by_bin"]
    assert curve[0]["recovered"] >= 0.5 and curve[-1]["recovered"] < 0.5
    assert out["cross_family"]["strict"] < out["cross_family"]["loose"] < 0.15
    assert out["sisters"]["strict"] > 0.3


def _lect(id, words):
    l = _L(id, None, 1.0)
    l.words = dict(zip(CONCEPTS, words))
    return l


def test_recurrence_rejects_chance_lookalike():
    rng = np.random.default_rng(3)
    a = [_word(rng) for _ in CONCEPTS]
    b = [_word(rng) for _ in CONCEPTS]
    b[0] = ("z",) + a[0][1:]  # one lookalike: its first correspondence (x:z) occurs nowhere else
    # a sister of `a` with two regular sound laws (p > f, a > e) and 30 words replaced
    s = [tuple({"p": "f", "a": "e"}.get(x, x) for x in w) for w in a]
    for k in rng.choice(NC, 30, replace=False):
        s[k] = _word(rng)
    tab = FA.WordTable([_lect("a", a), _lect("b", b), _lect("s", s)], CONCEPTS, _form)
    lo, st = FA.strict_shares(tab, [0, 0], [1, 2])
    assert lo[0] > 0 and st[0] == 0.0  # the lookalike counts loosely, not strictly
    assert st[1] >= 0.6 and st[1] <= lo[1]  # regular correspondences survive


def _w(a, b, n, r, big=0):
    return {"from_kyr": a, "to_kyr": a + 2.0, "splits": n, "big_splits": big, "scored": "all", "recovered": r}


def test_horizon_needs_two_windows_in_a_row():
    """One unlucky window under half does not end the horizon; two in a row do (calibration.md, measures round)."""
    curve = [_w(0, 1, 10, 1.0), _w(1, 2, 10, 0.9), _w(2, 3, 10, 0.3), _w(3, 4, 10, 0.8), _w(4, 5, 10, 0.7),
             _w(5, 6, 10, 0.4), _w(6, 7, 10, 0.2), _w(7, 8, 10, 0.1)]
    rd = FA.horizon_read(curve)
    assert rd["single_window_kyr"] < 3.5  # the former rule stops at the lone bad window
    assert 5.0 <= rd["horizon_kyr"] <= 6.5 and not rd["censored"]  # the run of two starts at 5-7 kyr
    assert rd["smoothed_kyr"] is not None and rd["smoothed_kyr"] > rd["single_window_kyr"]
    # windows of under MIN_SPLITS splits are skipped; a never-failing curve is censored at its last scored window
    rd = FA.horizon_read([_w(0, 1, 10, 1.0), _w(1, 2, 2, 0.0), _w(2, 3, 10, 0.9)])
    assert rd["censored"] and rd["horizon_kyr"] == 4.0
    # a lone failing last window still counts (nothing after it to recover)
    assert FA.horizon_read([_w(0, 1, 10, 1.0), _w(1, 2, 10, 0.2)])["horizon_kyr"] < 2.5


def test_horizon_per_people_group():
    """A slow-changing people's splits stay recoverable longer than a fast one's: the group measure sees it."""
    import planet.language.families as FA2
    fast = _world(seed=2, splits_per_family=20)
    global KEEP
    old = KEEP
    try:
        KEEP = 0.93
        slow = _world(seed=3, splits_per_family=20)
    finally:
        KEEP = old
    for l in slow:
        l.id, l.parent = "s" + l.id, ("s" + l.parent) if l.parent else None
        l.people, l.gen_yr = "elf", 145.0
    for l in fast:
        l.gen_yr = 28.0
    lects = fast + slow
    by = {l.id: l for l in lects}
    out = FA2.horizon_from(lects, by, CONCEPTS, _form, lambda l, c: l.roots.get(c), people="human", seed=1, pool=POOL,
                           groups={"long_lived": lambda l: l.gen_yr >= 60})
    h, g = out["by"]["human"], out["by"]["long_lived"]
    assert g["lects"] == len(slow) and h["lects"] == len(fast)
    assert g["horizon_kyr"] > h["horizon_kyr"] or g["censored"], (h["horizon_kyr"], g["horizon_kyr"])


def test_sparse_window_widens():
    """A window with too few splits borrows from 0.5-1 kyr either side instead of being skipped (no crossing interpolated
    across an empty stretch)."""
    def row(k, rec):
        return {"kyr": k, "big": False, "recovered": rec, "share": 0.5}
    rows = [row(8.2 + 0.1 * i, True) for i in range(8)] + [row(9.5, False), row(10.4, False), row(11.6, False), row(12.3, False)]
    curve = {w["from_kyr"]: w for w in FA.recovery_curve(rows)}
    assert "widened_kyr" not in curve[8.0] and curve[8.0]["splits"] == 9
    w = curve[10.0]  # 10-12 holds two splits; widened to 9.5-12.5 it holds four, none recovered
    assert w["widened_kyr"] == [9.5, 12.5] and w["splits"] == 4 and w["recovered"] == 0.0
    h = FA.horizon_read(list(curve.values()))["horizon_kyr"]
    assert h is not None and h < 11.0
