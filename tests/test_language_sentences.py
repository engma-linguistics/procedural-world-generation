"""planet/language/sentences.py: grammar notes and interlinear-glossed sample sentences, built from a lect's json record."""
from __future__ import annotations

import copy
import json

from planet.language import sentences as SN

WORDS = {
    "WOMAN": "kana", "MAN": "tor", "DOG": "pemo", "SEE": "lis", "HOUSE": "ruma", "SLEEP": "nem", "BIG": "olo", "IN": "ta",
    "EAT": "kum", "FISH": "sal", "THOU": "su", "I": "mi", "FIRE": "ika", "WATER": "aqa", "DRINK": "pin", "NOT": "na",
    "WHAT": "ke", "CHILD (YOUNG HUMAN)": "lalu", "MOTHER": "ama", "HOLD": "kap", "BROTHER": "keku", "TWO": "dua",
    "BIRD": "piru", "THAT": "ne", "HUNTER": "buru", "KNOW": "tau", "SING": "lan", "IF": "kaŋ", "WITH": "sama",
    "HE OR SHE OR IT": "ia", "COLD": "sejo", "AT": "di", "WHO": "sapa",
}
POS = {"SEE": "V", "SLEEP": "V", "EAT": "V", "DRINK": "V", "HOLD": "V", "KNOW": "V", "SING": "V", "BIG": "A", "COLD": "A",
       "TWO": "N"}


def lect(**typ) -> dict:
    t = {"word_order": "SVO", "adposition": "pre", "genitive": "NG", "adjective": "NA", "demonstrative": "NDem",
         "numeral": "NNum", "relative": "NRel", "alignment": "neutral", "negation": "preverbal",
         "polar_question": "intonation", "pro_drop": "no", "alienability": "no", "copula": "yes",
         "predicative_possession": "have", "wh_in_situ": "no", "head_direction": "initial", "numeral_classifiers": "no",
         "gender": "none", "adjective_verb_like": "no"}
    t.update(typ)
    return {"id": "d1", "people": "human", "typology": t, "grams": [],
            "inventory": {"consonants": ["p", "t", "k", "b", "d", "ɡ", "m", "n", "ŋ", "s", "l", "r", "j", "w", "ʔ", "q"],
                          "vowels": ["a", "e", "i", "o", "u"]},
            "lexicon": {c: {"ipa": f, "roman": f, "pos": POS.get(c, "N")} for c, f in WORDS.items()},
            "paradigms": {}}


def gram(fn, form, level, side, host, source=("?", "X", "coin"), born=1.0):
    return {"function": fn, "form_ipa": form, "level": level, "side": side, "host": host, "source": list(source),
            "born_kyr": born}


def by_id(lj) -> dict:
    return {s["id"]: s for s in SN.utterances(lj)}


def line(s) -> tuple[str, str]:
    return " ".join(w[0] for w in s["w"]), " ".join(w[1] for w in s["w"])


def test_word_order_follows_typology():
    svo = by_id(lect())["transitive"]
    sov = by_id(lect(word_order="SOV", head_direction="final"))["transitive"]
    vso = by_id(lect(word_order="VSO"))["transitive"]
    assert line(svo)[1] == "woman see dog"
    assert line(sov)[1] == "woman dog see"
    assert line(vso)[1] == "see woman dog"
    assert svo["en"] == "The woman sees the dog."


def test_free_order_falls_back_on_head_direction_and_says_so():
    s = by_id(lect(word_order="free", head_direction="final"))["transitive"]
    assert line(s)[1] == "woman dog see"
    assert "free" in s["note"]


def test_affix_clitic_and_free_gram_breaks_match_leipzig():
    lj = lect()
    lj["grams"] = [gram("3SG", "a", 2, "pre", "V"), gram("DEF", "il", 1, "pre", "NP"), gram("PAST", "bo", 0, "pre", "V")]
    s = by_id(lj)["tense"]
    form, gl = line(s)
    assert gl == "DEF=man PST 3SG-eat DEF=fish"
    # every word has the same breaks in both lines
    for f, g in s["w"]:
        assert [c for c in f if c in "-="] == [c for c in g if c in "-="]
    assert s["en"] == "The man ate the fish."
    assert "-" not in s["ipa"] and "=" not in s["ipa"]


def test_accusative_and_ergative_marking():
    acc = lect(alignment="nom-acc")
    acc["grams"] = [gram("ACC", "o", 2, "post", "NP")]
    assert line(by_id(acc)["transitive"])[1] == "woman see dog-ACC"
    erg = lect(alignment="erg-abs")
    erg["grams"] = [gram("ERG", "ne", 1, "post", "NP")]
    assert line(by_id(erg)["transitive"])[1] == "woman=ERG see dog"
    no_marker = lect(alignment="nom-acc")
    assert line(by_id(no_marker)["transitive"])[1] == "woman see dog"


def test_locative_case_or_adposition():
    adp = by_id(lect())["locative"]
    assert line(adp)[1] == "dog big sleep in house"
    case = lect(word_order="SOV", head_direction="final", adjective="AN")
    case["grams"] = [gram("LOC", "de", 2, "post", "NP")]
    s = by_id(case)["locative"]
    assert line(s)[1] == "big dog house-LOC sleep"


def test_pro_drop_with_agreement_and_polar_particle():
    lj = lect(pro_drop="yes", polar_question="final_particle")
    lj["grams"] = [gram("2SG", "u", 2, "pre", "V")]
    s = by_id(lj)["polar"]
    assert line(s)[1] == "2SG-see fire Q"
    assert s["q"] == 1
    kept = by_id(lect(polar_question="intonation"))["polar"]
    assert line(kept)[1] == "2SG see fire" and kept["q"] == 1


def test_wh_fronting_and_in_situ():
    assert line(by_id(lect(wh_in_situ="no"))["content"])[1] == "what child eat"
    assert line(by_id(lect(wh_in_situ="yes"))["content"])[1] == "child eat what"


def test_negation_placement():
    pre = by_id(lect())["negation"]
    assert line(pre)[1] == "1SG NEG drink water"
    fin = by_id(lect(negation="clause_final"))["negation"]
    assert line(fin)[1] == "1SG drink water NEG"
    bound = lect()
    bound["grams"] = [gram("NEG", "ka", 2, "pre", "VP")]
    assert line(by_id(bound)["negation"])[1] == "1SG NEG-drink water"


def test_possession_kinds():
    have = by_id(lect())["possession"]
    assert line(have)[1] == "mother 1SG have dog"
    loc = by_id(lect(predicative_possession="locational"))["possession"]
    assert "at" in line(loc)[1] and "COP" in line(loc)[1]
    other = by_id(lect(predicative_possession="other", copula="no"))["possession"]
    assert line(other)[1] == "mother 1SG with dog"


def test_numeral_and_kin_with_plural_affix():
    lj = lect(numeral="NumN")
    lj["grams"] = [gram("PL", "s", 2, "post", "N")]
    s = by_id(lj)["number"]
    assert line(s)[1] == "brother 1SG see two bird-PL"
    assert s["en"] == "My brother sees two birds."
    free = lect()
    free["grams"] = [gram("PL", "pada", 0, "post", "N")]
    assert "PL" not in line(by_id(free)["number"])[1]   # a free plural word is dropped after a numeral


def test_copula_and_relative():
    cop = by_id(lect())["copula"]
    assert line(cop)[1] == "man that COP hunter"
    nocop = by_id(lect(copula="no"))["copula"]
    assert line(nocop)[1] == "man that hunter"
    rel = by_id(lect())["relative"]
    assert line(rel)[1] == "1SG know woman REL sing"
    reln = by_id(lect(relative="RelN", word_order="SOV", head_direction="final"))["relative"]
    assert line(reln)[1] == "1SG sing woman know"


def test_joining_glide_and_nasal_assimilation():
    cons = {"j", "w", "m", "n", "ŋ"}
    assert SN.join("ka", "a", cons) == ("ka", "ja")
    assert SN.join("ku", "a", cons) == ("ku", "wa")
    assert SN.join("kan", "pa", cons) == ("kam", "pa")
    assert SN.join("kan", "ka", cons) == ("kaŋ", "ka")
    assert SN.join("kan", "ka", {"n"}) == ("kan", "ka")    # the lect has no ŋ
    lj = lect(word_order="SOV", head_direction="final")
    lj["grams"] = [gram("3SG", "an", 2, "pre", "V")]
    t = by_id(lj)["tense"]
    assert t["w"][-1][0] == "aŋ-kum" and t["ipa"].endswith("aŋkum")


def test_paradigm_cell_wins():
    lj = lect()
    lj["grams"] = [gram("3SG", "a", 2, "pre", "V")]
    lj["paradigms"] = {"verbs": {"columns": ["lemma", "3SG"], "rows": [
        {"concept": "SEE", "cells": {"lemma": {"ipa": "lis"}, "3SG": {"ipa": "elis"}}, "segmented": {"3SG": "e-lis"},
         "irregular": ["3SG"]}]}}
    assert by_id(lj)["transitive"]["w"][1] == ["e-lis", "3SG-see"]


def test_missing_concepts_degrade():
    lj = lect()
    for c in ("WOMAN", "MAN", "HOUSE", "MOTHER"):
        del lj["lexicon"][c]
    s = by_id(lj)
    assert "transitive" not in s and "possession" not in s    # no woman, man or person; no mother
    assert "polar" in s and "negation" in s
    lj2 = copy.deepcopy(lect())
    lj2["lexicon"] = {k: v for k, v in lj2["lexicon"].items() if k in ("I", "DOG", "SEE")}
    assert SN.utterances(lj2) == []
    assert isinstance(SN.grammar_notes(lj2), list)


def test_noun_classes_on_nouns():
    lj = lect(gender="sex")
    lj["grams"] = [gram("CLASS:1", "o", 2, "pre", "N", ("MAN", "G066", "concept")),
                   gram("CLASS:2", "e", 2, "pre", "N", ("WOMAN", "G066", "concept"))]
    s = by_id(lj)["transitive"]
    assert line(s)[1] == "F-woman see M-dog"


def test_enrich_is_compact_json():
    lj = lect(alignment="nom-acc")
    lj["grams"] = [gram("ACC", "o", 2, "post", "NP"), gram("PAST", "bo", 1, "pre", "V"), gram("PL", "s", 2, "post", "N")]
    SN.enrich(lj)
    assert 5 <= len(lj["sentences"]) <= 10
    topics = {n["topic"] for n in lj["grammar_notes"]}
    assert {"Number", "Case", "Gender and noun classes", "Tense and aspect", "Person agreement", "Negation", "Questions",
            "Possession", "Relative clauses", "Copula"} <= topics
    assert all(s["ipa"] and s["roman"] and s["en"] for s in lj["sentences"])
    assert len(json.dumps({"s": lj["sentences"], "n": lj["grammar_notes"]}, ensure_ascii=False)) < 9000


def test_note_examples_name_sentences_by_id():
    lj = SN.enrich(lect())
    neg = next(n for n in lj["grammar_notes"] if n["topic"] == "Negation")
    assert neg["ex"] == ["negation"]
    form, gloss, en, s = SN.example(lj, "negation")
    assert gloss == "1SG NEG drink water" and en == "I do not drink the water." and s["id"] == "negation"
    poss = next(n for n in lj["grammar_notes"] if n["topic"] == "Possession")
    assert SN.example(lj, poss["ex"][0])[3] is None and SN.example(lj, "nope") is None
