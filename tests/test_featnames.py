"""Feature names (PW-1656) and the map's labels (PW-1655): planet/lineages/featnames.py on small hand-made lects and runs."""
import json

import pytest

from planet.lineages import featnames as FN


def lect(id, deme, fam, words, order="AN", born=20.0, died=None, end=None, people="human"):
    lex = {c: {"ipa": w, "roman": w} for c, w in words.items()}
    return {"id": id, "deme": deme, "family_true": fam, "lexicon": lex, "typology": {"adjective": order}, "born_kyr": born,
            "died_kyr": died, "end": end, "people": people}


WORDS_A = {"MOUNTAIN": "tor", "HILL": "bun", "WHITE": "kal", "BIG": "mak", "SEA": "mar", "ISLAND": "ey", "NOSE": "nas", "HEAD": "kop",
           "MOUTH": "mun", "LONG": "lan", "LAND": "lan", "LAKE": "lak"}
WORDS_B = {"MOUNTAIN": "zigu", "HILL": "dobo", "WHITE": "imi", "BIG": "ogo", "SEA": "uma", "ISLAND": "shima", "NOSE": "hana",
           "MOUTH": "kuchi", "LONG": "naga", "LAND": "kuni", "LAKE": "mizu"}


def tongues(*ls, habits=None):
    return FN.Tongues({"lects": list(ls), "names": {"habits": habits or {}}})


def test_book_and_clip():
    assert FN.book("zhèngizha'i") == "zhengizhai"
    assert FN.clip("dzilawidztai") == "dzila"  # (two syllables)
    assert FN.clip("dzilawi") == "dzila"
    assert FN.clip("dzilan") == "dzilan"
    assert FN.clip("tor") == "tor"


def test_coin_follows_the_lects_adjective_order_and_gives_the_common_english():
    import numpy as np
    a = lect("a", 1, "f1", WORDS_A, "AN")
    b = lect("b", 2, "f2", WORDS_B, "NA")
    T = tongues(a, b)
    ca = FN.coin(T, a, "peak", ("WHITE",), np.random.default_rng(0), 1)
    cb = FN.coin(T, b, "peak", ("WHITE",), np.random.default_rng(0), 1)
    assert ca["local"] == "Kaltor" and ca["parts"] == ["WHITE", "MOUNTAIN"]
    assert cb["local"] == "Zigu" + "imi" and cb["parts"] == ["MOUNTAIN", "WHITE"]
    assert ca["english"] == cb["english"] and ca["english"].startswith("White")  # (the Common renders the meaning, not the words)
    r = FN.coin(T, a, "range", ("LONG",), np.random.default_rng(0), 2)
    assert r["english"] == "The Long Mountains"
    s = FN.coin(T, a, "sea", ("BIG",), np.random.default_rng(0), 3)
    assert s["english"].startswith("The ") and s["english"].endswith("Sea")


def test_a_cape_takes_the_lects_coast_habit():
    import numpy as np
    a = lect("a", 1, "f1", WORDS_A)
    T = tongues(a, habits={"a": {"coast": ["head", "mouth"]}})
    assert FN.coin(T, a, "cape", (), np.random.default_rng(0), 1)["parts"][-1] == "HEAD"
    T2 = tongues(a)
    assert FN.coin(T2, a, "cape", (), np.random.default_rng(0), 1)["parts"][-1] == "NOSE"


class FakeLand:
    """holders() as given: [(kyr ago, deme)], oldest first."""
    seed = 7

    def __init__(self, seq):
        self.seq = seq

    def holders(self, cells):
        return self.seq

    def ll(self, c):
        return 10.0, 20.0


def feat(kind):
    return {"kind": kind, "cell": 0, "size": 1.0, "catch": [0], "mods": ("WHITE",)}


def test_a_newcomer_of_another_family_keeps_or_renames(monkeypatch):
    a = lect("a", 1, "f1", WORDS_A, people="dwarf")
    b = lect("b", 2, "f2", WORDS_B, people="elf")
    T = tongues(a, b)
    seq = [(20.0, 1), (15.0, 1), (10.0, 2), (5.0, 2), (0.0, 2)]
    monkeypatch.setitem(FN.RENAME_PER_KYR, "peak", 0.0)
    monkeypatch.setitem(FN.KEEP, "peak", 1.0)
    kept = FN.walk(FakeLand(seq), T, feat("peak"), 1)
    assert kept["layer"] == "substrate" and kept["kyr"] == 20.0 and kept["named_by_people"] == "dwarf"
    assert kept["said_by_people"] == "elf" and kept["local"] == "Kaltor" and len(kept["names"]) == 1
    monkeypatch.setitem(FN.KEEP, "peak", 0.0)
    renamed = FN.walk(FakeLand(seq), T, feat("peak"), 1)
    assert renamed["layer"] == "own" and renamed["kyr"] == 10.0 and renamed["named_by_people"] == "elf"
    assert [n[0] for n in renamed["names"]] == [20.0, 10.0] and renamed["names"][0][4] == "dwarf"


def test_a_daughter_language_inherits_the_name_in_its_own_words(monkeypatch):
    a = lect("a", 1, "f1", WORDS_A, people="dwarf")
    a2 = lect("a2", 3, "f1", {**WORDS_A, "MOUNTAIN": "tur"}, people="dwarf")
    T = tongues(a, a2)
    monkeypatch.setitem(FN.RENAME_PER_KYR, "peak", 0.0)
    r = FN.walk(FakeLand([(20.0, 1), (10.0, 3), (0.0, 3)]), T, feat("peak"), 1)
    assert r["layer"] == "inherited" and r["kyr"] == 20.0 and r["local"] == "Kaltur"


def test_unpeopled_features_go_unnamed():
    assert FN.walk(FakeLand([(20.0, None), (0.0, None)]), tongues(lect("a", 1, "f1", WORDS_A)), feat("peak"), 1) is None


def test_rivers_outlast_peaks_outlast_towns_in_the_ages():
    feats = [{"kind": "river", "kyr": 20.0}, {"kind": "river", "kyr": 18.0}, {"kind": "peak", "kyr": 12.0}, {"kind": "peak", "kyr": 16.0}]
    lang = {"names": {"demes": {"0": {"settlements": [{"tier": "town", "kyr": 3.0}, {"tier": "village", "kyr": 19.0}]}}}}
    a = FN.ages(feats, lang)
    assert a["river"]["median_kyr"] > a["peak"]["median_kyr"] > a["town"]["median_kyr"]
    assert a["town"]["n"] == 1


def test_durability_order_of_the_rules():
    # (rivers keep their names longest, towns are renamed most: the ticket's order holds in the rules themselves)
    assert FN.KEEP["river"] >= FN.KEEP["lake"] >= FN.KEEP["range"] >= FN.KEEP["peak"] >= FN.KEEP["region"]
    assert FN.RENAME_PER_KYR["river"] <= FN.RENAME_PER_KYR["range"] <= FN.RENAME_PER_KYR["peak"]


def test_labels_carry_both_tongues(tmp_path):
    run = {"id": "r1", "meta": {"id": "r1", "present": {"landmasses": [
        {"rank": 0, "kind": "continent", "lat": 1.0, "lon": 2.0, "area_mkm2": 10.0, "called": "Simath"}]}}}
    (tmp_path / "run.json").write_text(json.dumps(run))
    (tmp_path / "settlements.json").write_text(json.dumps({"sites": [
        {"id": 5, "kind": "town", "lat": 3.0, "lon": 4.0, "tier_peak": "town", "peak_pop": 3000, "founded_kyr": 6.0, "abandoned_kyr": None},
        {"id": 6, "kind": "chief", "lat": 3.0, "lon": 4.0, "tier_peak": "village", "peak_pop": 300, "founded_kyr": 6.0}]}))
    lang = {"names": {"landmasses": {"Simath": {"roman": "Zheyrhiwa", "today": {"roman": "Jiyiwa"}, "people": "tortle", "kyr": 20.0}},
                      "demes": {"0": {"settlements": [{"site": 5, "roman": "Iligya", "english": "Blackford"}]}}}}
    feats = {"features": [{"kind": "peak", "id": "peak:0", "lat": 5.0, "lon": 6.0, "size": 3000.0, "english": "Whitefell", "local": "Kaltor",
                           "names": [[20.0, "Whitefell", "Kaltor", "a", "dwarf", "named"]], "kyr": 20.0}]}
    pol = {"polities": [{"id": 1, "tier_peak": "state", "capital": {"site": 5, "lat": 3.0, "lon": 4.0}, "founded_kyr": 5.0, "fell_kyr": None,
                         "names": [[5.0, "Iligya (humans)"]], "name": "Iligya (humans)", "peak_cells": 30},
                        {"id": 2, "tier_peak": "chiefdom", "capital": {"site": 5, "lat": 3.0, "lon": 4.0}, "names": [[5.0, "x"]], "name": "x"}]}
    L = {l["kind"]: l for l in FN.labels(tmp_path, pol, lang, feats)["labels"]}
    assert set(L) == {"continent", "peak", "town", "state"}  # (no villages, no chiefdoms)
    assert (L["continent"]["english"], L["continent"]["local"]) == ("Simath", "Jiyiwa")
    assert (L["town"]["english"], L["town"]["local"], L["town"]["from_kyr"]) == ("Blackford", "Iligya", 6.0)
    assert L["state"]["names"] == [[5.0, "Blackford (humans)", "Iligya (humans)"]]
    assert L["peak"]["names"][0][1:3] == ["Whitefell", "Kaltor"]


@pytest.mark.parametrize("kind", sorted(FN.HEAD))
def test_every_kind_has_heads_keep_and_caps(kind):
    assert kind in FN.KEEP and kind in FN.CAPS and kind in FN.RENAME_PER_KYR
