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
        ("crop:rice", "padi", "N"), ("crop:chili", "cabai", "N"), ("TAKE", "ambil", "V"), ("GRIND", "giling", "V"),
        ("PUT", "taruh", "V"), ("POT", "periuk", "N"), ("BOIL", "rebus", "V"), ("SALT", "garam", "N"),
        ("STONE", "batu", "N"), ("BAKE", "bakar", "V"), ("POUND", "tumbuk", "V"), ("MORTAR", "lesung", "N"),
        ("ASH", "abu", "N"), ("HONEY", "madu", "N"), ("MILK", "susu", "N"))})
    title, sents = TX.recipe(lj)
    assert title == "How to cook rice" and len(sents) >= 4   # (chili is a spice, never the meal)
    assert sents[0]["en"] == "Take some rice." and "rice" in " ".join(w[1] for w in sents[0]["w"])
    assert all(s["roman"] for s in sents)
    assert sents[1]["en"] in ("Grind it with a stone.", "Pound it in a mortar.")   # (a grain's ways, WAYS["grain"])
    # (PW-1537 R3: lects of one people tell different recipes, not one template with the noun swapped)
    told = set()
    for i in range(12):
        lj2 = dict(lj, id=f"d{i}")
        told.add(tuple(s["en"] for s in TX.recipe(lj2)[1]))
    assert len(told) >= 3, told
    meat = copy.deepcopy(lj)
    meat["lexicon"] = {c: w for c, w in meat["lexicon"].items() if not c.startswith("crop:")}
    meat["lexicon"].update({c: {"ipa": f, "roman": f, "pos": p} for c, f, p in (
        ("animal:caprine", "kambin", "N"), ("CUT", "potong", "V"), ("KNIFE", "pisau", "N"), ("ROAST OR FRY", "panggan", "V"),
        ("FIRE", "api", "N"))})
    title, sents = TX.recipe(meat)
    assert title == "How to cook goat meat" and not any("Grind" in s["en"] for s in sents)


def test_myth_tells_only_the_faith_data():
    lj = _fable_lect()
    lj["lexicon"].update({c: {"ipa": f, "roman": f, "pos": p} for c, f, p in (
        ("name:god:7", "laut", "NAME"), ("SEA", "samudra", "N"), ("HOLD", "pegan", "V"), ("PIG", "babi", "N"),
        ("HEAR", "dengar", "V"), ("WE", "kami", "PRON"))})
    faith = {"name": "the faith of the sea", "gods": [
        {"key": 7, "domain": "sea", "label": "god of sea and rain", "high": True,
         "names": [["d1", "laut", "Laut", "lord of the sea", None]]},
        {"key": 9, "domain": "fire", "label": "spirit of fire", "high": False, "names": []}],
        "taboos": [[7, "swine", "wild swine"], [99, "swine", "x"], [7, "eels", "eels"]]}   # (the faith's own taboos)
    title, sents = TX.myth(lj, faith)
    en = [s["en"] for s in sents]
    assert title.startswith("What the gods hold") and en[0] == "Laut holds the sea."
    assert "Laut gives us fish." in en and "We do not eat pigs." in en and en[-1].startswith("Laut, ") and en[-1].endswith(" us!")
    assert not any("eels" in e or "fire" in e for e in en)   # (no word for eels; the fire god has no name here)
    assert "Laut" in " ".join(w[1] for w in sents[0]["w"]) and all(s["roman"] for s in sents)
    assert TX.myth(lj, None) == ("", [])


def test_gods_are_persons():
    """A god, its name and spirits take the person class (not things or abstractions)."""
    from planet.language import grammar as GR
    for c in ("name:god:7", "GOD", "SPIRIT", "god:sky"):
        assert GR.semantic_group(c) == "person", c


def test_fable_prefers_a_shallow_ancestor():
    """A 20 kyr root keeps few shared words; the fable takes an ancestor last spoken 3-6 kyr ago (polish lane)."""
    root = _fable_lect()
    root.update(id="p1", parent=None, died_kyr=20.0, deme=0, people="human")
    mid = copy.deepcopy(root)
    mid.update(id="m1", parent="p1", died_kyr=4.5, deme=1)
    other = copy.deepcopy(root)
    other.update(id="m2", parent="p1", died_kyr=12.0, deme=2)
    kids = []
    for i, par in enumerate(("m1", "m1", "m1", "m2", "m2")):
        k = copy.deepcopy(root)
        k.update(id=f"d{i}", parent=par, died_kyr=None, deme=10 + i, population=100 * (i + 1))
        kids.append(k)
    lects = {x["id"]: x for x in [root, mid, other] + kids}
    anc, ds = TX.pick_family(lects)
    assert anc["id"] == "m1" and {d["id"] for d in ds} == {"d0", "d1", "d2"}
    assert TX.FABLE_DAUGHTERS[0] <= len(ds) <= TX.FABLE_DAUGHTERS[1]


def test_invocation_marks_the_object_once():
    """'X, hear us!' in a lect with a bound 1PL object marker: one =1PL.OBJ, not two (frost giant, demo read 4)."""
    lj = _fable_lect()
    lj["lexicon"].update({c: {"ipa": f, "roman": f, "pos": p} for c, f, p in (
        ("name:god:7", "laut", "NAME"), ("SEA", "samudra", "N"), ("HOLD", "pegan", "V"), ("HEAR", "dengar", "V"),
        ("WE", "kami", "PRON"))})
    lj["grams"] = [gram("1PL.O", "mi", 1, "post", "V")]
    faith = {"name": "f", "gods": [{"key": 7, "domain": "sea", "label": "g", "high": True,
                                    "names": [["d1", "laut", "Laut", "x", None]]}], "taboos": []}
    _t, sents = TX.myth(lj, faith)
    inv = next(s for s in sents if s["en"].endswith(" us!"))
    gl = " ".join(w[1] for w in inv["w"])
    assert gl.count("1PL.OBJ") == 1, gl


def test_fable_ancestor_is_the_state_at_the_split():
    """PW-1592: the ancestor is a lect as it stood at its first bud (a split state), and the daughters come from both
    sides of that split; a root the line coined after the split and both branches share is caught by fable_descent."""
    m = _fable_lect()
    m.update(id="m1", parent=None, died_kyr=None, born_kyr=10.0, deme=1, people="human", population=500)
    for w in m["lexicon"].values():
        w["roots"] = ["m1:OLD@10"]
    bud = copy.deepcopy(m)
    bud.update(id="d2", parent="m1", born_kyr=5.0, deme=2, population=300)
    late = copy.deepcopy(m)
    late.update(id="d3", parent="m1", born_kyr=3.0, deme=3, population=200)
    early = copy.deepcopy(m)
    early.update(id="d4", parent="m1", born_kyr=8.0, deme=4, population=900)
    split = copy.deepcopy(m)
    split.update(id="m1@5", split_of="m1", split_kyr=5.0, died_kyr=5.0, branches={"m1": "line", "d2": "d2", "d3": "line"})
    lects = {x["id"]: x for x in (m, bud, late, early)}
    anc, ds = TX.pick_family(lects, splits=[split])
    assert anc["id"] == "m1@5" and "d4" not in {d["id"] for d in ds}
    assert {split["branches"][d["id"]] for d in ds} == {"line", "d2"}
    roots = {"m1:OLD@10": {"lect": "m1", "kyr": 10.0}, "m1:SAY@4": {"lect": "m1", "kyr": 4.0}}
    assert TX.fable_descent(anc, ds, roots, lects) == []
    for d in ds:   # (a change of the line after the split, shared across it: the cold review's R2)
        d["lexicon"]["SAY"]["roots"] = ["m1:SAY@4"]
    assert any("shared by branches" in x for x in TX.fable_descent(anc, ds, roots, lects))
