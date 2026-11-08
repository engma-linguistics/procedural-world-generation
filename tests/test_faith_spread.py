"""Faith spread (PW-1477) and attitudes v0 (PW-904): missionaries, rulers' push, the border shares, the temperaments."""
import numpy as np

from planet.lineages import attitudes as AT
from planet.lineages import gods as G

D = {d: i for i, d in enumerate(G.DOMAINS)}
KNOW = {"spirit_ritual", "burial"}
TEMPLE = KNOW | {"temples", "kingship"}


def sal(**kw):
    s = np.zeros(len(G.DOMAINS))
    for k, v in kw.items():
        s[D[k]] = v
    return s


S0, S1 = sal(sea=0.9, storm=0.8, hunt=0.7), sal(mountain=0.9, sky=0.8, herd=0.7)


def two(P, know0, know1, frames, contacts=None, rule_steps=None, people=("human", "human"), dt=0.5, start=10.0):
    """Two cultures for `frames` frames dt kyr apart; rule_steps(ago, prev) -> the polity steps between."""
    prev = None
    for k in range(frames):
        ago = start - k * dt
        rs = rule_steps(ago, prev) if (rule_steps and prev is not None) else ()
        P.frame(ago, {0: {"sal": S0, "know": know0, "people": people[0]}, 1: {"sal": S1, "know": know1, "people": people[1]}},
                contacts=contacts, rule_steps=rs)
        prev = ago


def first_conversion(P):
    return next((e for e in P.events if e["kind"] == "conversion"), None)


def test_spread_times_are_centuries_for_missionaries_and_millennia_otherwise():
    assert G.TAU_MISSION < 0.5 and 1.0 <= G.TAU_CONVERT <= 5.0 and G.TAU_FORCED < 0.1 < G.TAU_TOLERANT  # (was 30 kyr: PW-1477)


def test_a_missionary_faith_wins_a_less_organised_neighbour_within_centuries():
    waits = []
    for seed in range(12):
        P = G.Pantheons(seed=seed)
        two(P, KNOW, TEMPLE, 2, contacts={(0, 1)})
        P.faiths[P.faith_of[1]].missionary = P.faiths[P.faith_of[1]].decided = True
        two(P, KNOW, TEMPLE, 12, contacts={(0, 1)}, start=9.0)
        e = first_conversion(P)
        waits.append(9.0 - e["ago_kyr"] if e else 99.0)
    assert np.median(waits) < 1.0  # (a link's mean wait is TAU_MISSION / receptiveness: centuries)


def test_an_ordinary_faith_spreads_slowly_and_never_to_an_equal():
    P = G.Pantheons(seed=3)
    two(P, TEMPLE, TEMPLE, 40, contacts={(0, 1)})
    assert P.counts["conversions"] == 0  # (equally organised: no one leaves their faith)


def test_a_faith_founded_this_frame_does_not_convert_before_its_founding():
    P = G.Pantheons(seed=1)
    two(P, KNOW, TEMPLE, 2, contacts={(0, 1)})
    spec = {"id": "a1", "name": "X", "gods": [{"name": "Y", "domains": ["sun"]}], "spreads": True, "missionary": True}
    P.frame(8.0, {0: {"sal": S0, "know": KNOW, "people": "human"}, 1: {"sal": S1, "know": TEMPLE, "people": "human"}}, contacts={(0, 1)}, found=[(1, spec)])
    f = spec["faith"]
    assert all(e[0] <= 8.0 + 1e-9 for e in P.faiths[f].events)


def test_a_harsh_ruler_converts_its_subjects_far_faster_than_a_tolerant_one():
    def wait(tol, seed, missionary=True):
        P = G.Pantheons(seed=seed)
        two(P, KNOW, KNOW, 2)
        P.faiths[P.faith_of[1]].missionary = P.faiths[P.faith_of[1]].decided = missionary
        P.att.x[1] = np.array([tol, 0.5])
        P.att.off[1] = np.array([tol - P.att._base("human")[0], 0.0])  # (hold the ruler's tolerance where it is)
        steps = lambda ago, prev: [(round(a, 3), [(1, [(0, 1.0)], False)]) for a in np.arange(ago, prev - 1e-9, 0.1)]  # noqa: E731
        two(P, KNOW, KNOW, 20, rule_steps=steps, start=9.0)
        e = first_conversion(P)
        return (9.0 - e["ago_kyr"]) if e else 99.0, e
    harsh = [wait(0.0, s)[0] for s in range(10)]
    mild = [wait(1.0, s)[0] for s in range(10)]
    assert np.median(harsh) < 0.2 < np.median(mild)
    ethnic = [wait(0.0, s, missionary=False)[0] for s in range(10)]
    assert np.median(ethnic) > 2 * np.median(harsh)  # (a ruler of a faith that seeks no converts pushes it far less: ETHNIC_RULE)
    _, e = wait(0.0, 0)
    assert e["how"] == "rulers" and e["ruler_tolerance"] <= 0.3


def test_border_shares_weigh_the_pull():
    # cells 0-1-2-3 in a line; culture 5 holds 0, 1, 2 and culture 6 holds 3: 5's border to 6 is one edge of its one outer edge
    src = np.array([0, 1, 1, 2, 2, 3])
    dst = np.array([1, 0, 2, 1, 3, 2])
    w = G.touch(4, np.array([0, 1, 2, 3]), np.array([5, 5, 5, 6]), src, dst, 10)
    assert set(w) == {(5, 6)} and w[(5, 6)] == (1.0, 1.0)
    w = G.touch(5, np.array([0, 1, 2, 3]), np.array([5, 5, 5, 6]), np.concatenate([src, [3, 4]]), np.concatenate([dst, [4, 3]]), 10)
    assert w[(5, 6)][1] == 0.5  # (6 also borders empty land: half its border faces 5)


def test_temperaments_follow_the_tree_and_cultures_of_one_people_differ():
    human = {"traits": ["agricultural", "cosmopolitan"], "demography": {"insularity": 0.3}}
    elf = {"traits": ["insular"], "demography": {"insularity": 0.7}}
    dwarf = {"traits": ["mountain"], "demography": {"insularity": 0.75, "contest": 1.5}}
    orc = {"traits": ["nomadic", "hardy"], "demography": {"insularity": 0.5}}
    th, te, td, to = (AT.temperament(x) for x in (human, elf, dwarf, orc))
    assert th[0] > to[0] > te[0] > td[0] - 0.05
    assert td[1] > to[1] > th[1] and te[1] == th[1]
    A = AT.Attitudes({"human": human}, seed=1)
    for c in range(20):
        A.ensure(c, "human")
    for k in range(40):
        A.step(10.0 - 0.5 * k, 0.5 if k else 0.0, {c: "human" for c in range(20)}, {}, set())
    tol = np.array([A.get(c)[0] for c in range(20)])
    assert tol.std() > 0.03 and abs(tol.mean() - th[0]) < 0.15  # (one people, many temperaments, about its own)
    tr = A.track[0]
    assert len(tr) >= 20 and max(t[1] for t in tr) - min(t[1] for t in tr) > 0.05  # (it moves over centuries)


def test_conquest_raises_aggression_and_wide_rule_tolerance():
    A = AT.Attitudes({}, seed=2)
    A.ensure(0, "x")
    A.ensure(1, "x")
    t0 = A.target(0, 3, False).copy()
    A.won(0)
    A.ruled(0, 10)
    t1 = A.target(0, 3, False)
    assert t1[1] - t0[1] > 0.1 and t1[0] > t0[0]
    assert A.target(1, 3, True)[0] < A.target(1, 3, False)[0]  # (a missionary faith: a little less tolerant)


# ---- minority faiths (PW-1489)
def _ok(P):
    for c, s in P.comp.items():
        assert abs(sum(s.values()) - 1.0) < 1e-9 and s[P.faith_of[c]] >= 0.5 - 1e-9  # (its faith is the majority)


def test_a_pressed_culture_gains_a_minority_up_to_the_plateau_and_a_conversion_leaves_a_remnant_that_fades():
    grew = faded = 0
    for seed in range(8):
        P = G.Pantheons(seed=seed)
        P.frame(10.0, {0: {"sal": S0, "know": KNOW, "people": "human"}, 1: {"sal": S1, "know": TEMPLE, "people": "human"}})
        f1 = P.faith_of[1]
        P.faiths[f1].missionary = P.faiths[f1].decided = True
        seen_minor, flipped = [], None
        for k in range(1, 80):
            P.frame(10.0 - 0.05 * k, {0: {"sal": S0, "know": KNOW, "people": "human"}, 1: {"sal": S1, "know": TEMPLE, "people": "human"}}, contacts={(0, 1)})
            _ok(P)
            if P.faith_of[0] != f1:
                seen_minor.append(P.comp[0].get(f1, 0.0))
            elif flipped is None:
                flipped = dict(P.comp[0])
        assert max(seen_minor, default=0.0) <= G.SHARE_PLATEAU + 1e-9  # (converts, but at most a tenth before the take-off)
        grew += max(seen_minor, default=0.0) > G.SHARE_SEED
        if flipped is not None:
            assert flipped[f1] >= 0.5 and len(flipped) == 2  # (the conversion: the newcomer passes half, the old faith stays)
            faded += P.comp[0][f1] > flipped[f1]  # (the remnant fades: its own faith and its neighbour of that faith win it over)
    assert grew >= 2 and faded >= 2


def test_minorities_do_not_change_the_majority_history():
    def hist(track):
        P = G.Pantheons(seed=5)
        if not track:
            P._shares = lambda *a, **k: None  # (no share bookkeeping at all)
        two(P, KNOW, TEMPLE, 2, contacts={(0, 1)})
        P.faiths[P.faith_of[1]].missionary = P.faiths[P.faith_of[1]].decided = True
        two(P, KNOW, TEMPLE, 30, contacts={(0, 1)}, start=9.0, dt=0.2)
        return P.fhist, [e for e in P.events if e["kind"] == "conversion"]
    a, b = hist(True), hist(False)
    assert a == b and a[1]  # (no extra random draws: the conversions are today's)


def test_daughters_carry_minorities_and_merges_pool_them_by_land():
    P = G.Pantheons(seed=0)
    two(P, KNOW, KNOW, 2)
    f0, f1 = P.faith_of[0], P.faith_of[1]
    P.comp[0] = {f0: 0.8, f1: 0.2}
    P.split(2, 0, 8.0)
    assert P.comp[2] == {f0: 0.8, f1: 0.2}
    P.cells.update({0: 30, 1: 10})
    P.merge(1, 0, 8.0)  # (1, all f1, merges into 0: 30 cells at 80/20 and 10 at 0/100)
    assert abs(P.comp[0][f1] - 0.4) < 1e-9 and P.faith_of[0] == f0
    P.cells.update({0: 10, 2: 90})
    P.comp[2] = {f1: 1.0}
    P._join(2, f1, 7.5)
    P.merge(2, 0, 7.0)  # (a larger culture of another faith: the survivor's faith keeps half)
    _ok(P)
    assert P.share_counts["merge_capped"] == 1
    assert P.shares_doc(0)[0][0] == f0
