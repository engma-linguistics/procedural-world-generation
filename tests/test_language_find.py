"""tools/language/find.py: feature filters and reference-profile likeness over a tiny synthetic languages.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "language"))

import find  # noqa: E402
import pytest  # noqa: E402

HAWAIIAN_LIKE = {"SUN": "laːmaka", "WATER": "wai", "MOTHER": "makuahine", "FIRE": "ahi", "BIRD": "manu", "I": "au",
                 "TWO": "lua", "EAT": "ʔai", "STONE": "pohaku", "NIGHT": "poː", "WIND": "makani", "TREE": "laːʔau",
                 "FISH": "iʔa", "MAN": "kane", "WOMAN": "wahine", "HAND": "lima", "EYE": "maka", "HEAD": "poʔo"}
ENGLISH_LIKE = {"SUN": "sʌn", "WATER": "wɔtɹ", "MOTHER": "mʌðɹ", "FIRE": "faɪɹ", "BIRD": "bɝd", "I": "aɪ", "TWO": "tu",
                "EAT": "it", "STONE": "ston", "NIGHT": "naɪt", "WIND": "wɪnd", "TREE": "tɹi", "FISH": "fɪʃ",
                "MAN": "mæn", "WOMAN": "wʊmn", "HAND": "hænd", "EYE": "aɪ", "HEAD": "hɛd"}
CLICKY = {"SUN": "ǃaǀa", "WATER": "ǁo", "MOTHER": "ǃʰana", "FIRE": "ǀuǀu", "BIRD": "ǂiǂi", "I": "ǀa", "TWO": "ǃo",
          "EAT": "ǁaǁa", "STONE": "ǃoǃo", "NIGHT": "ǀeǀe"}


def _lect(lid, deme, people, cons, vows, words, onset, coda, typology, tones=()):
    return {"id": lid, "deme": deme, "end": None, "people": people, "parent": None, "language": f"lang{deme}",
            "family_scholars": f"fam{deme}", "family_true": f"p{deme}", "population": 1000.0 * (deme + 1),
            "deme_name": f"{people} {deme} (the north of Testland)",
            "inventory": {"consonants": cons, "vowels": vows, "tones": list(tones), "max_onset": onset, "max_coda": coda,
                          "stress": "penult"},
            "typology": typology, "complexity": {"mean_level": 1.0, "fused": 0},
            "lexicon": {c: {"ipa": w, "roman": w, "pos": "N", "freq": 1} for c, w in words.items()}}


def _doc() -> dict:
    lects = [
        _lect("d0", 0, "human", ["p", "k", "ʔ", "h", "m", "n", "l", "w"], ["a", "e", "i", "o", "u", "aː", "oː"],
              HAWAIIAN_LIKE, 1, 0, {"word_order": "VSO", "adposition": "pre", "case": "none"}),
        _lect("d1", 1, "dwarf", ["p", "b", "t", "d", "k", "ɡ", "f", "v", "θ", "ð", "s", "z", "ʃ", "h", "m", "n", "ŋ", "l",
                                 "ɹ", "j", "w", "tʃ"],
              ["i", "ɪ", "e", "ɛ", "æ", "ɑ", "ɔ", "o", "ʊ", "u", "ʌ", "ə"], ENGLISH_LIKE, 2, 2,
              {"word_order": "SVO", "adposition": "pre", "case": "none"}),
        _lect("d2", 2, "drow", ["ǃ", "ǀ", "ǁ", "ǂ", "ǃʰ", "n", "h"], ["a", "e", "i", "o", "u"], CLICKY, 1, 0,
              {"word_order": "SOV", "adposition": "post", "case": "many"}, tones=(1, 3)),
        {"id": "p0", "deme": None, "end": None, "people": "human", "lexicon": {}},   # a proto: never listed
    ]
    names = {"demes": {"0": {"name": {"roman": "Hawaiki", "lect": "d0"}}, "1": {"name": {"roman": "Angle", "lect": "d1"}}}}
    return {"format": "procgen-languages/1", "lects": lects, "names": names}


def _write(tmp_path) -> Path:
    p = tmp_path / "languages.json"
    p.write_text(json.dumps(_doc(), ensure_ascii=False), encoding="utf-8")
    return p


def test_features(tmp_path):
    doc, feats = find.load(_write(tmp_path))
    f = {x["id"]: x for x in feats}
    assert set(f) == {"d0", "d1", "d2"}
    assert f["d0"]["syllables"] == "CV" and f["d0"]["final_vowel_share"] == 1.0 and f["d0"]["long_vowels"] == 1
    assert f["d0"]["name"] == "Hawaiki" and f["d0"]["place"] == "the north of Testland"
    assert f["d1"]["syllables"] == "CCVCC" and f["d1"]["interdental"] == 1 and f["d1"]["final_vowel_share"] < 0.5
    assert f["d2"]["clicks"] == 1 and f["d2"]["tones"] == 2 and f["d1"]["clicks"] == 0


def test_profiles_well_formed():
    profiles = find.load_profiles()
    for need in ("hawaiian", "sindarin", "quenya", "japanese", "english", "finnish", "arabic", "mandarin", "georgian",
                 "welsh"):
        assert need in profiles
    for k, p in profiles.items():
        assert p["words"] >= 20, k
        assert p["texture"] and p["sources"], k
    assert profiles["english"]["consonants"] == 24   # from sketch.py, not the table


def test_likeness_ranks_the_obvious_lect_first(tmp_path):
    doc, feats = find.load(_write(tmp_path))
    hits, n = find.run(doc, feats, like="hawaiian")
    assert n == 3 and [h["f"]["id"] for h in hits][0] == "d0"
    hits, _ = find.run(doc, feats, like="english")
    assert hits[0]["f"]["id"] == "d1"
    assert hits[0]["samples"] and hits[0]["contributions"]["texture"] >= 0
    hits, _ = find.run(doc, feats, like="zulu")
    assert hits[-1]["f"]["id"] != "d2"   # the click lect is not the least Zulu-like


def test_filters(tmp_path):
    doc, feats = find.load(_write(tmp_path))
    ids = lambda **kw: [h["f"]["id"] for h in find.run(doc, feats, **kw)[0]]  # noqa: E731
    assert ids(wheres=["consonants<=10", "syllables=CV"]) == ["d2", "d0"]   # by speakers
    assert ids(wheres=["clicks"]) == ["d2"]
    assert ids(wheres=["!clicks", "tones=0"], sort="consonants:asc") == ["d0", "d1"]
    assert ids(order="VSO") == ["d0"]
    assert ids(wheres=["word_order=VSO|SVO"], sort="final_vowel_share") == ["d0", "d1"]
    assert ids(people="elves") == ["d2"]      # drow count as elves
    assert ids(people="dwarves,humans", wheres=["place~north"]) == ["d1", "d0"]


def test_cli_json(tmp_path, capsys):
    assert find.main([str(_write(tmp_path)), "--like", "hawaiian", "--top", "2", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["matched"] == 3 and len(out["hits"]) == 2 and out["hits"][0]["id"] == "d0"
    assert "texture" not in out["hits"][0] and out["hits"][0]["samples"][0]["concept"] == "sun"
    assert find.main([str(_write(tmp_path)), "--where", "nosuchkey>1"]) == 2


def test_vowel_qualities_and_sparse_profiles():
    """PW-1624: long and nasal vowels are series, not more qualities; a profile with blank cells is not nearer to
    everything (its filled terms are scaled to a full profile's weight)."""
    assert find.vowel_qualities(["a", "aː", "i", "iː", "u", "ã"]) == 3
    f = {"consonants": 10, "vowels": 5, "tones": 0, "max_onset": 1, "max_coda": 0, "final_vowel_share": 0.5,
         "cluster_share": 0.2, "mean_syllables": 2.0, "stress": "initial", "word_order": "SOV", "adposition": "post",
         "case": "none", "synthesis": 1.0, "texture": {}, "nonhuman": 0, **{k: 0 for k in find.SERIES}}
    full = {"consonants": 20, "vowels": 5, "tones": 0, "max_onset": 1, "max_coda": 0, "final_vowel_share": 0.5,
            "cluster_share": 0.2, "mean_syllables": 2.0, "stress": "penult", "word_order": "SOV", "adposition": "post",
            "case": "none", "synthesis": 1.0, "series": []}
    sparse = dict(full, stress=None, word_order=None, adposition=None, case=None, synthesis=None)
    d_full, _ = find.distance(f, full)
    d_sparse, comp = find.distance(f, sparse)
    assert d_sparse > sum(comp.values())   # (the filled terms scaled up to a full profile's weight)
    assert d_sparse == pytest.approx(sum(comp.values()) * find.OPTIONAL_WEIGHT /
                                     sum(find.WEIGHTS[k] for k in comp if k in find.OPTIONAL))
