"""The synchronic rule layer (planet/language/phonology.py, sound lane 2026-11-08)."""
from types import SimpleNamespace

import numpy as np

from planet.language import inventory as I
from planet.language import phonology as PH
from planet.language import rules as RU
from planet.language.percepts import from_ipa, word_ipa


def _rule(note, fam="lenition", rid="x"):
    r, why = RU.parse_rule({"id": rid, "rule": note, "family": fam, "cause": "effort"})
    assert r is not None, why
    return r


def _lect(inv, live=()):
    return SimpleNamespace(id="L", hiatus_key="L", inventory=inv, live=list(live), dead_rules=[], sandhi_drawn=False,
                           lexicon=None, load_forms=lambda: [])


def test_conditioned_change_becomes_a_phrase_rule_and_narrows_with_age():
    inv = I.Inventory(consonants=list(from_ipa("pbtdk")), vowels=list(from_ipa("aiu")))
    L = _lect(inv)
    r = _rule("p > b / V_V")
    PH.on_change(L, r, 5.0)
    assert [x.level for x in L.live] == ["phrase"]
    PH.update(L, 4.5)
    assert L.live[0].level == "phrase"
    PH.update(L, 3.0)
    assert L.live[0].level == "word"
    PH.update(L, 1.0)
    assert (L.live and L.live[0].level == "stem") or L.dead_rules   # (old: stem level, or dead past its drawn life)
    PH.on_change(L, _rule("p > b", rid="y"), 1.0)   # (context-free: no rule)
    assert all(x.ref != "c:y" for x in L.live)


def test_old_rules_die():
    inv = I.Inventory(consonants=list(from_ipa("pbt")), vowels=list(from_ipa("a")))
    L = _lect(inv)
    PH.on_change(L, _rule("p > b / V_V"), 30.0)
    PH.update(L, 0.0)
    assert not L.live and L.dead_rules and "old" in L.dead_rules[-1][3]


def test_live_rules_apply_to_new_words_through_realize():
    inv = I.Inventory(consonants=list(from_ipa("pbtdkm")), vowels=list(from_ipa("aiu")), shapes={"CV": 1.0})
    L = _lect(inv)
    PH.on_change(L, _rule("p > b / V_V"), 1.0)
    PH.attach(L)
    w = tuple(from_ipa("kapa"))
    assert word_ipa(I.realize(w, inv)) == "kaba"


def test_phrase_rules_apply_across_word_joins():
    r = _rule("p > b / V_V")
    a, b = tuple(from_ipa("ka")), tuple(from_ipa("pata"))
    out = PH.apply_phrase([a, b], [(r, "phrase")])
    assert [word_ipa(x) for x in out] == ["ka", "bata"]


def test_meeussen_sandhi():
    r = PH.sandhi_rule("meeussen")
    w = tuple(from_ipa("ka˦ta˦ma˦"))
    assert word_ipa(RU.apply(r, w, "none")) == "ka˦ta˨ma˦"


def test_tonal_line_draws_sandhi_once():
    inv = I.Inventory(consonants=list(from_ipa("pt")), vowels=list(from_ipa("a")), tones=[1, 3, 4])
    got = 0
    for k in range(40):
        L = _lect(inv)
        L.id = L.hiatus_key = f"p{k}"
        PH.draw_sandhi(L, 1.0)
        got += any(x.ref.startswith("s:") for x in L.live)
        PH.draw_sandhi(L, 0.5)
        assert sum(x.ref.startswith("s:") for x in L.live) <= 1
    assert 15 <= got <= 38


def test_allophone_rules_and_json_round_trip():
    p, x = from_ipa("t")[0], from_ipa("d")[0]
    r = PH.allophone_rule(x, p, "intervocalic")
    assert word_ipa(RU.apply(r, tuple(from_ipa("ata")), "none")) == "ada"
    rows = PH.rules_from_json({"rules": [{"r": r.id, "lv": "phonetic"}, {"r": "s:meeussen", "lv": "phrase"},
                                         {"r": "c:" + RU.DEMO_RULES[0].id, "lv": "word"}]})
    assert [lv for _r, lv in rows] == ["phonetic", "phrase", "word"]


def test_notation_over_own_sounds():
    r = _rule("p, t, k > b, d, g / V_V")
    t = PH.notation(r, list(from_ipa("ptm")))
    assert t == "p → b, t → d / V_V"
    assert PH.notation(r, list(from_ipa("pt")), allophone=True).startswith("/p/ → [b]")


def test_new_paradigm_cells_join_under_the_live_rules():
    """A cell a grammar step builds (stem + new affix) runs the word-level live rules at the join; a cell that was there
    before is left alone (sound change already ran on it)."""
    from planet.language import grammar as GR
    inv = I.Inventory(consonants=list(from_ipa("pbtdkm")), vowels=list(from_ipa("aiu")), shapes={"CV": 1.0, "CVC": 1.0},
                      max_coda=1)
    L = _lect(inv)
    PH.on_change(L, _rule("p > b / V_V"), 1.0)   # (a phrase-level rule: it runs inside words too)
    PH.attach(L)
    g = GR.Grammar(typology=GR.Typology({}))
    ex = GR.Exemplar("DOG", "N", tuple(from_ipa("kap")))
    ex.set(("PL",), (("stem", tuple(from_ipa("kap"))), ("PL", tuple(from_ipa("i")))))
    old = GR.Exemplar("CAT", "N", tuple(from_ipa("mup")))
    old.set(("PL",), (("stem", tuple(from_ipa("mup"))), ("PL", tuple(from_ipa("a")))))
    g.exemplars = [ex, old]
    before = {("CAT", "N", ("PL",)): old.parts[("PL",)]}
    assert PH.apply_new_cells(g, inv, before) == 1
    assert word_ipa(ex.cells[("PL",)]) == "kabi" and [word_ipa(m) for _, m in ex.parts[("PL",)]] == ["kab", "i"]
    assert word_ipa(old.cells[("PL",)]) == "mupa"
