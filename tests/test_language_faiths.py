"""Faiths in the languages (faiths & contact pass 3): god names as words with a history, liturgies frozen at the canon,
learned loans. On the synthetic tiny run of test_language_history with a hand-made gods readout."""
from __future__ import annotations

import pytest

from planet.language import faiths as FT
from planet.language import history as H
from planet.language import output as OU

from test_language_history import TinyRun


def _gods():
    def being(i, culture, dom, born, how="founded", parent=None, high=False, ind=0.5):
        return {"id": i, "label": f"god of {dom}", "culture": culture, "how": how, "parent": parent, "born_kyr": born,
                "top": [[dom, 0.8]], "first_domain": dom, "individuation": ind, "devotion": 1.0, "high": high,
                "status": "living", "name": None}
    beings = [being(0, 0, "sky", 300.0, high=True, ind=0.7), being(1, 0, "river", 300.0, ind=0.2),
              being(2, 1, "sky", 1.2, "converted", 0, high=True), being(3, 2, "fire", 300.0, high=True)]
    cultures = {"0": {"people": "human", "living": [0, 1], "faith_now": 0},
                "1": {"people": "orc", "living": [2], "faith_now": 0},
                "2": {"people": "elf", "living": [3], "faith_now": 1}}
    faiths = [{"id": 0, "name": "the sky faith of the humans", "how": "founded", "parent": None, "origin_culture": 0,
               "founded_kyr": 300.0, "core": "sky"},
              {"id": 1, "name": "the fire faith of the elves", "how": "founded", "parent": None, "origin_culture": 2,
               "founded_kyr": 300.0, "core": "fire"}]
    return {"beings": beings, "cultures": cultures, "faiths": {"list": faiths}}


class FaithRun(TinyRun):
    def __init__(self):
        super().__init__()
        self.cultures_doc = {"deme_culture": [0, 0, 1, 0, 1, 2]}
        self.__dict__["_gods_doc"] = _gods()
        self.meta["techtree"] = {"known": {"human": {"temples": [1.6, "invented", None]}}}
        self.dir = None


@pytest.fixture(scope="module")
def faith_result():
    old = (H.RATE_SCALE, H.SHIFT_K, H.WORKERS, FT.NAME_HALF_KYR, FT.LEARNED_RATE)
    H.RATE_SCALE, H.SHIFT_K, H.WORKERS = 240.0, 0.0, 1
    FT.NAME_HALF_KYR, FT.LEARNED_RATE = 1e9, 0.05   # (no renaming: the cognates stay readable; learned loans often)
    try:
        res = H.generate(None, run=FaithRun())
        doc = OU.document(res)
        res2 = H.generate(None, run=FaithRun())
        doc2 = OU.document(res2)
    finally:
        H.RATE_SCALE, H.SHIFT_K, H.WORKERS, FT.NAME_HALF_KYR, FT.LEARNED_RATE = old
    return res, doc, doc2


def _l(res):
    return {l.id: l for l in res["lects"]}


def test_plan_reads_the_readout():
    P = FT.Plan(FaithRun())
    assert P.ok
    assert P.deme_faith == {0: 0, 1: 0, 3: 0, 2: 0, 4: 0, 5: 1}
    kinds = {(d, k): kind for v in P.events.values() for d, k, kind in v}
    assert kinds[(0, 0)] == "coin" and kinds[(2, 0)] == "convert"   # (the orcs took the sky god by conversion)
    assert P.faiths[0]["canon_kyr"] is not None and P.faiths[1]["canon_kyr"] is None   # (only the humans know temples)


def test_god_names_are_inherited_words(faith_result):
    res, _doc, _ = faith_result
    L = _l(res)
    con = FT.god_concept(0)
    w0, w3 = L["d0"].lexicon.get(con), L["d3"].lexicon.get(con)
    assert w0 is not None and w3 is not None and w0.pos == "NAME"
    assert FT._coined(w0) == FT._coined(w3), "a bud inherits its parent's god name (one coinage: cognates)"
    assert any(st.process == "name:god" for st in w0.etym)
    # sound change runs over names like any word: the name's chain records it when the form moved
    assert all(st.process.split(":")[0] in ("proto", "coin", "derive", "compound", "name", "sound_change", "borrow",
                                             "shift", "taboo", "substrate", "accent", "elaborate", "renew", "nativize",
                                             "analogy", "colex", "koine") for st in w0.etym)


def test_converts_borrow_the_name(faith_result):
    res, _doc, _ = faith_result
    L = _l(res)
    w = L["d2"].lexicon.get(FT.god_concept(0))
    assert w is not None
    assert any(st.process.startswith("borrow:") for st in w.etym), "a convert takes the god's name from the converters"
    assert L["d5"].lexicon.get(FT.god_concept(3)) is not None   # (the elves name their own fire god)


def test_liturgy_and_document(faith_result):
    res, doc, doc2 = faith_result
    h = res["history"]
    assert 0 in h.liturgy and 1 not in h.liturgy
    lit = h.liturgy[0]["lect"]
    assert lit.died_kyr == h.liturgy[0]["kyr"] and lit.id not in h.lects   # (frozen: never stepped)
    F = doc["faiths"]["0"]
    assert F["holders"] and F["gods"][0]["names"]
    assert "liturgy" in F and F["liturgy"]["words"]
    assert doc["faiths"] == doc2["faiths"]
    learned = [st for l in res["lects"] if l.alive for w in l.lexicon.words.values() for st in w.etym
               if st.process == f"borrow:{lit.id}"]
    assert learned, "the holders took learned loans from the liturgy"


def test_one_faith_one_pantheon():
    """Every holder of a faith names the same gods, the seat culture's (polish lane): the orc culture of the sky faith
    lists only its sky god in gods.json, but it holds the human founders' river god too, taken with the faith."""
    P = FT.Plan(FaithRun())
    assert P.faiths[0]["pantheon"] == [0, 1]
    assert all(P.deme_gods[d] == [0, 1] for d, f in P.deme_faith.items() if f == 0)
    kinds = {(d, k): kind for v in P.events.values() for d, k, kind in v}
    assert kinds[(2, 1)] == "convert"


def test_pantheon_in_document(faith_result):
    res, doc, _ = faith_result
    F = doc["faiths"]["0"]
    assert [g["key"] for g in F["gods"]] == [0, 1]
    named = {n[0] for n in F["gods"][1]["names"]}
    assert set(F["holders"]) <= named, "every holder names every god of the pantheon"
    assert "taboos" in F
