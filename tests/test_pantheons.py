"""Regional pantheons v0 (PW-1523, D68): hubs, matched seats, patrons; a read-out that never changes the gods or faiths."""
import numpy as np

from planet.lineages import gods as G
from planet.lineages import pantheons as PN

D = {d: i for i, d in enumerate(G.DOMAINS)}
TEMPLE = {"spirit_ritual", "burial", "temples", "kingship"}


def sal(**kw):
    s = np.zeros(len(G.DOMAINS))
    for k, v in kw.items():
        s[D[k]] = v
    return s


LAND = sal(sea=0.9, storm=0.8, hunt=0.7, harvest=0.65, war=0.6)
NEAR = {0: np.array([1.0, 0.0, 0.0]), 1: np.array([0.99, 0.1, 0.0]), 2: np.array([0.99, -0.1, 0.0]), 3: np.array([0.0, 1.0, 0.0])}
PEOPLE = {0: "human", 1: "elf", 2: "elf", 3: "orc"}


class Open(PN.Regional):
    def __init__(self, seed=0, shut=()):
        super().__init__(seed)
        self.shut = set(shut)

    def openness(self, P, c):  # (the accessor lane 219 may override; here every culture is open but `shut`)
        return 0.0 if c in self.shut or P.faiths[P.faith_of[c]].missionary else 0.9


def run(regional=None, frames=120, missionary=None, urban=None):
    P = G.Pantheons(seed=3)
    P.regional = regional
    contacts = {(0, 1): (0.4, 0.5), (0, 2): (0.3, 0.5), (1, 2): (0.2, 0.2)}
    for k in range(frames):
        ago = 12.0 - 0.1 * k
        cs = {c: {"sal": LAND, "know": TEMPLE, "people": PEOPLE[c]} for c in NEAR}
        where = {c: (10, NEAR[c] * 10) for c in NEAR}
        P.frame(ago, cs, contacts=contacts, where=where, urban=urban if urban is not None else {0: 0.2})
        if k == 1 and missionary is not None:
            P.faiths[P.faith_of[missionary]].missionary = P.faiths[P.faith_of[missionary]].decided = True
    return P


def _hist(P):
    return (P.fhist, [e for e in P.events if e["kind"] == "conversion"], [(b.id, b.status, round(float(b.ind), 9), b.w.round(9).tolist()) for b in P.beings])


def test_pantheons_do_not_change_the_gods_or_faiths():
    a, b = run(Open()), run(None)
    assert _hist(a) == _hist(b)  # (its own random stream; nothing written back)
    assert a.regional.pans  # (and it did something)


def test_a_mixed_town_gathers_a_pantheon_whose_seats_join_peoples_and_spare_their_patrons():
    P = run(Open())
    R = P.regional
    pan = R.pans[0]
    assert pan["hub"] == 0 and pan["kind"] == "city" and 3 not in pan["reach"]  # (the far culture is out of reach: PANTHEON_KM)
    seats = [s for s in R.seats if s["ended"] is None and s["members"]]
    assert seats
    pat = set(pan["patrons"].values())
    for s in seats:
        assert len({PEOPLE[c] for c in s["members"]}) >= 2  # (a seat joins peoples)
        for c, b in s["members"].items():
            assert b.how in ("adopted", "joint") or PN._root(P, b) not in pat  # (a people's own god is never matched away)
            assert G.DOMAINS[int(np.argmax(b.w))] == s["domain"]
    docs = [G.being_doc(P, b) for b in P.beings]
    out = R.finish(P, [{"name": f"c{c}", "people": PEOPLE[c]} for c in NEAR], docs)
    assert out["summary"]["living"] == 1 and any(d["seat"] is not None for d in docs)


def test_no_towns_no_rulers_no_pantheon():
    P = run(Open(), urban={})
    assert not P.regional.pans


def test_a_faith_that_refuses_other_gods_keeps_its_cultures_out():
    P = run(Open(), missionary=1)
    R = P.regional
    assert all(1 not in s["members"] for s in R.seats)
    assert all(1 not in p["reach"] for p in R.pans)


def test_a_closed_hub_ends_its_pantheon_at_once():
    R = Open()
    P = run(R, frames=80)
    assert R.pans and R.pans[0]["ended"] is None
    R.shut.add(0)
    cs = {c: {"sal": LAND, "know": TEMPLE, "people": PEOPLE[c]} for c in NEAR}
    P.frame(3.9, cs, contacts={(0, 1): (0.4, 0.5)}, where={c: (10, NEAR[c] * 10) for c in NEAR}, urban={0: 0.2})
    assert R.pans[0]["ended"] is not None and all(s["ended"] is not None for s in R.seats)
