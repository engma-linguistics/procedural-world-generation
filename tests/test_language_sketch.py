"""tools/language/sketch.py: Wikipedia-style language pages from a small synthetic languages.json (no engine run)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "language"))

import sketch  # noqa: E402

CORE = ["I", "THOU", "WE", "YOU", "HE OR SHE OR IT", "THEY", "WATER", "FIRE", "DOG", "BIG", "PERSON", "EAT", "ONE", "TWO",
        "THREE", "STONE", "SEE"]


def _fixture() -> dict:
    nodes = []

    def node(parent, kyr, lect, proc, form, gloss, note=None):
        nodes.append([parent, kyr, lect, proc, form, gloss] + ([note] if note else []))
        return len(nodes) - 1

    protos = {c: node(-1, 20.0, "p0", "proto", f"pa{i}", c.lower()) for i, c in enumerate(CORE)}

    def lexicon(lect, forms, extra=None):
        lex = {}
        for c in CORE:
            i = node(protos[c], 1.0, lect, "sound_change:S001", forms.get(c, f"ta{CORE.index(c)}"), 0)
            lex[c] = {"ipa": forms.get(c, f"ta{CORE.index(c)}"), "roman": forms.get(c, f"ta{CORE.index(c)}"),
                      "pos": "N", "freq": 1, "etym": i}
        for c, (base, form) in (extra or {}).items():
            j = node(lex[base]["etym"], 0.5, lect, f"compound:{base}+BIG", form, c.lower())
            lex[c] = {"ipa": form, "roman": form, "pos": "N", "freq": 3, "etym": j}
        return lex

    english_like = {
        "id": "d1", "deme": 1, "people": "human", "parent": "p0", "how": "bud", "substrate": None, "born_kyr": 5.0,
        "died_kyr": None, "end": None, "minority": False, "rate": 1.0, "gen_yr": 27.0, "language": "lang0",
        "family_true": "p0", "family_scholars": "fam0", "deme_name": "human 1 (the north of Testland)",
        "inventory": {"consonants": ["p", "b", "t", "d", "k", "ɡ", "f", "v", "s", "z", "ʃ", "h", "m", "n", "ŋ", "l", "ɹ",
                                     "j", "w", "tʃ", "dʒ", "θ"],
                      "vowels": ["i", "ɪ", "e", "ɛ", "æ", "ɑ", "o", "u", "ʊ", "ə"], "tones": [],
                      "shapes": {"CV": 0.3, "CVC": 0.4, "CCVC": 0.2, "CVCC": 0.1}, "stress": "initial",
                      "max_onset": 2, "max_coda": 2,
                      "allophones": {"t": ["ɾ between vowels"]}},
        "typology": {"word_order": "SVO", "adposition": "pre", "definite_article": "pre", "indefinite_article": "present",
                     "case": "none", "adjective": "AN", "genitive": "GN", "negation": "preverbal", "alignment": "nom-acc",
                     "number": "sg-pl", "gender": "none", "pro_drop": "no", "clusivity": "yes"},
        "grams": [{"function": "NEG", "form_ipa": "nɑ", "form_roman": "na", "level": 0, "level_name": "free word",
                   "side": "pre", "host": "V", "source": ["?", "X01", "coin"], "born_kyr": 3.0},
                  {"function": "PL", "form_ipa": "s", "form_roman": "s", "level": 2, "level_name": "affix",
                   "side": "post", "host": "N", "source": ["MANY", "G064", "concept"], "born_kyr": 4.0},
                  {"function": "3SG", "form_ipa": "z", "form_roman": "z", "level": 2, "level_name": "affix",
                   "side": "post", "host": "V", "source": ["HE OR SHE OR IT", "X08", "concept"], "born_kyr": 2.0}],
        "paradigms": {"nouns": {"columns": ["lemma", "PL"], "rows": [
            {"concept": "DOG", "cells": {"lemma": {"ipa": "dɔɡ", "roman": "dog"}, "PL": {"ipa": "dɔɡs", "roman": "dogs"}},
             "segmented": {"PL": "dɔɡ-s"}, "irregular": []}]}, "verbs": {"columns": ["lemma"], "rows": []},
            "periphrastic": []},
        "complexity": {"live_grams": 3, "mean_level": 1.3, "cells": 1, "allomorphy": 0},
        "lexicon": lexicon("d1", {"I": "aj", "THOU": "ju", "YOU": "ju", "DOG": "dɔɡ", "BIG": "bɪɡ", "PERSON": "pɛɹsən",
                                  "EAT": "it", "ONE": "wan"}, {"HOUSE": ("DOG", "dɔɡbɪɡ"), "BARN": ("DOG", "dɔɡhaw")}),
        "affixes": {}, "changes": [[4.5, "S001", "effort", None], [4.5, "S002", "effort", "d2"],
                                   [4.0, "simplification", "dispersion", None, {"merged": "x > k"}]],
        "rules_applied": 3, "l2": 0.1, "population": 5000.0, "shares_history": [], "stats": {
            "core_mean_syllables": 1.3, "core_mean_segments": 3.0, "homophone_share": 0.05, "inherited_core_share": 0.5}}
    clicky = json.loads(json.dumps(english_like))
    clicky.update({"id": "d2", "deme": 2, "people": "drow", "family_true": "p9", "parent": None, "how": "proto",
                   "born_kyr": 20.0, "deme_name": "drow 1 (the south of Testland)", "gen_yr": 145.0,
                   "inventory": {"consonants": ["ǃ", "ǀ", "ǁ", "ʘ", "kʼ", "tʼ", "m", "n", "l‼"],
                                 "vowels": ["a", "i", "u", "a‼"], "tones": [1, 3], "shapes": {"CV": 1.0},
                                 "stress": "none", "max_onset": 1, "max_coda": 0},
                   "typology": {"word_order": "SOV", "adposition": "post", "definite_article": "none",
                                "indefinite_article": "none", "case": "many", "adjective": "NA"},
                   "grams": [], "lexicon": lexicon("d2", {"I": "ǃa˦", "THOU": "ǃa˦"}), "changes": [],
                   "stats": {"core_mean_syllables": 3.4, "inherited_core_share": 0.9}})
    proto = {"id": "p0", "deme": None, "people": "human", "parent": None, "how": "proto", "born_kyr": 20.0,
             "died_kyr": 20.0, "end": "split", "family_true": "p0", "inventory": {"consonants": ["p", "t"],
                                                                                 "vowels": ["a"], "tones": []},
             "lexicon": {}, "changes": [[19.0, "S003", "effort", None]], "typology": {}, "grams": []}
    return {
        "format": "procgen-languages/1", "run": "test", "snapshot_concepts": CORE, "etym_nodes": nodes,
        "rules": {"S001": "p became ɸ between vowels (effort: lenition)", "S002": "t became θ between vowels (effort: x)",
                  "S003": "k became h between vowels (effort: lenition)", "simplification": "rare sounds merged"},
        "lects": [proto, english_like, clicky],
        "names": {"peoples": {"human": {"glossonym": {"ipa": "tɛst", "roman": "Test", "gloss": "the speech", "lect": "d1"}}},
                  "demes": {"1": {"name": {"ipa": "ɪŋɡlɪʃ", "roman": "Inglish", "gloss": "the people", "lect": "d1"}},
                            "2": {"name": {"ipa": "ǃa", "roman": "!A", "gloss": "the people", "lect": "d2"}}},
                  "common": {"lect": "d1", "exonyms": {}}, "scholars": {}},
        "shifts": [], "families": {"languages": [{"id": "lang0", "name": "speech of human 1", "lects": ["d1"]}]},
        "intelligibility": {"now": [["d1", "d2", 0.02]]},
    }


def test_render_page_sections_and_charts():
    doc = sketch.Doc(_fixture())
    page = sketch.render(doc, doc.lects["d1"])
    assert page.startswith(sketch.MARKER)
    assert "# Inglish language" in page
    for h in ("## History", "## Phonology", "### Consonants", "### Vowels", "## Orthography", "## Grammar",
              "### Pronouns", "## Vocabulary", "### Numerals", "## Sample phrases", "## Relatives and intelligibility"):
        assert h in page, h
    assert "| **Plosive** | p · b |" in page  # voiceless left, voiced right, bilabial first
    assert "| **Close** | i |" in page and "ɪ" in page
    assert "| t | ɾ between vowels |" in page  # allophones rendered when present
    assert "| 1st | aj ‹ay› |" in page  # pronoun chart from the lexicon
    assert "'thou' and 'you' are the same word" in page
    assert "only one 'we' form" in page  # clusivity flagged as a gap
    assert "k became h between vowels" in page  # the proto stage's change
    assert "(from" in page  # an adopted change names its source
    assert "dɔɡ-s" in page  # segmented paradigm cell
    assert "a big dog | bɪɡ dɔɡ" in page  # AN order
    assert "nɑ it" in page  # free preverbal negator
    assert "a coined particle" in page
    assert "Words built on **dog**" in page  # word family from compounds


def test_nonhuman_footnote_and_missing_allophones():
    doc = sketch.Doc(_fixture())
    page = sketch.render(doc, doc.lects["d2"])
    assert "| **Click** |" in page and "| **Ejective** |" in page
    assert "**‼**" in page  # house/VoQS mark explained
    assert "records no allophones" in page
    assert "| low | a˨ |" in page
    assert "'I' and 'thou' are the same word" in page


def test_english_score_and_auto(tmp_path):
    fx = _fixture()
    doc = sketch.Doc(fx)
    rank = sketch.english_ranking(doc)
    assert rank[0][1]["id"] == "d1" and rank[0][0] > rank[1][0]
    assert abs(sum(sketch.ENGLISH_WEIGHTS.values()) - 1) < 1e-9
    src = tmp_path / "languages.json"
    src.write_text(json.dumps(fx, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "sketches"
    out.mkdir()
    (out / "stale.md").write_text(sketch.MARKER + "\nold\n", encoding="utf-8")
    (out / "notes.md").write_text("hand-written\n", encoding="utf-8")
    assert sketch.main([str(src), "--out", str(out), "--auto"]) == 0
    names = {p.name for p in out.glob("*.md")}
    assert "stale.md" not in names and "notes.md" in names  # only generated pages are replaced
    assert "index.md" in names and "d1-human.md" in names and "d2-drow.md" in names
    idx = (out / "index.md").read_text(encoding="utf-8")
    assert "The English-likeness score" in idx and "Top 5" in idx and "Ladefoged" in idx
    assert "## Next to English" in (out / "d1-human.md").read_text(encoding="utf-8")


def test_root_families_allophone_table_and_case_clash():
    fx = _fixture()
    l = fx["lects"][0] if fx["lects"][0]["id"] == "d1" else next(x for x in fx["lects"] if x["id"] == "d1")
    l["inventory"]["allophones"] = [{"ipa": "b", "of": "p", "test": "intervocalic", "where": "between vowels only (lenition)"}]
    fx["roots"] = {"p0:DOG": {"node": 1, "lect": "p0", "kyr": 20.0, "concept": "DOG", "gloss": "dog", "ipa": "pa1", "pos": "N"}}
    for c in ("DOG", "BIG", "PERSON"):
        l["lexicon"][c]["roots"] = ["p0:DOG"]
    page = sketch.render(sketch.Doc(fx), l)
    assert "| allophone | phoneme | where |" in page and "| [b] | /p/ | between vowels only |" in page
    assert "Words built on one root: **dog**" in page and "| roots (main first) |" in page
    # a free locative is an adposition, not case; a clitic one is case
    t = {"case": "none"}
    free = [{"function": "LOC", "form_ipa": "ka", "level": 0}]
    assert sketch._typology_clashes(t, free) == []
    assert sketch._typology_clashes(t, [dict(free[0], level=1)])
