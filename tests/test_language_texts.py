"""planet/language/texts.py: the fable told in a proto-language and its daughters, and the per-language recipe."""
from __future__ import annotations

import copy

from planet.language import texts as TX
from test_language_sentences import gram, lect


def _fable_lect(**typ):
    lj = lect(**typ)
    lj["lexicon"].update({c: {"ipa": f, "roman": f, "pos": p} for c, f, p in (
        ("SIT", "duduk", "V"), ("TREE", "pohon", "N"), ("SAY", "kata", "V"), ("COME", "datan", "V"), ("GIVE", "beri", "V"),
        ("GOOD", "baik", "A"), ("SEED", "biji", "N"))})
    return lj


def test_fable_is_told_whole_with_four_lines():
    lj = _fable_lect()
    lj["grams"] = [gram("PAST", "su", 0, "post", "V"), gram("FUT", "akan", 0, "pre", "V")]
    sents = TX.fable(lj)
    assert TX.complete(sents, len(TX.FABLE_EN))
    for s in sents:
        assert s["roman"] and s["ipa"] and len(s["roman"].split(" ")) == len(s["w"]) and s["en"] in TX.FABLE_EN
    assert "PST" in " ".join(w[1] for w in sents[0]["w"])
    assert "FUT" in " ".join(w[1] for w in sents[2]["w"]) and "NEG" in " ".join(w[1] for w in sents[3]["w"])


def test_fable_family_pick_and_missing_words():
    p = _fable_lect()
    p.update(id="p1", parent=None, died_kyr=20.0, deme=0)
    kids = []
    for i in range(3):
        k = copy.deepcopy(p)
        k.update(id=f"d{i}", parent="p1", died_kyr=None, deme=i + 1, population=100 * (i + 1))
        kids.append(k)
    poor = copy.deepcopy(kids[0])
    poor.update(id="d9", deme=9)
    del poor["lexicon"]["SEED"]
    lects = {x["id"]: x for x in [p, poor] + kids}
    assert not TX.complete(TX.fable(poor), len(TX.FABLE_EN))
    proto, ds = TX.pick_family(lects)
    assert proto["id"] == "p1" and len(ds) == 3 and "d9" not in {d["id"] for d in ds}


def test_recipe_uses_the_peoples_own_food():
    lj = _fable_lect()
    lj["lexicon"].update({c: {"ipa": f, "roman": f, "pos": p} for c, f, p in (
        ("crop:millet", "jawa", "N"), ("TAKE", "ambil", "V"), ("GRIND", "giling", "V"), ("PUT", "taruh", "V"),
        ("POT", "periuk", "N"), ("COOK", "masak", "V"), ("SALT", "garam", "N"), ("STONE", "batu", "N"))})
    title, sents = TX.recipe(lj)
    assert title == "How to cook millet" and len(sents) == 6
    assert sents[0]["en"] == "Take some millet." and "millet" in " ".join(w[1] for w in sents[0]["w"])
    assert all(s["roman"] for s in sents)
