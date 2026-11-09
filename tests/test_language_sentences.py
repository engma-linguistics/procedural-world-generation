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
    assert 5 <= len(lj["sentences"]) <= len(SN.SENTENCES)   # (17 since grammar phase A, each only where it applies)
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


# --- grammar phase A (2026-11-08) ---------------------------------------------------------------------------------------

def _more(**words):
    lj = lect()
    lj["lexicon"].update({c: {"ipa": f, "roman": f, "pos": "V" if c in ("GIVE", "TAKE", "COME", "GO", "RUN") else "N"}
                          for c, f in words.items()})
    return lj


def test_give_dative_serial_or_double_object():
    base = dict(GIVE="beri", TAKE="ambil", COME="datan")
    dat = _more(**base)
    dat["grams"] = [gram("DAT", "ke", 0, "pre", "NP")]
    s = by_id(dat)["give"]
    assert line(s)[1] == "woman give fish DAT child" and "DAT" in s["note"]
    ser = _more(**base)
    ser["typology"]["serial_verbs"] = "yes"
    assert line(by_id(ser)["give"])[1] == "woman take fish give child"
    dbl = _more(**base)
    s = by_id(dbl)["give"]
    assert line(s)[1] == "woman give fish child" and "double object" in s["note"]
    assert s["en"] == "The woman gives the child a fish."


def test_imperative_and_passive():
    lj = lect()
    s = by_id(lj)["imperative"]
    assert line(s)[1] in ("eat fish", "drink water") and s["en"].endswith("!")
    assert "passive" not in by_id(lj)
    lj["grams"] = [gram("PASS", "tər", 2, "pre", "V", ("BECOME", "G033", "concept"))]
    s = by_id(lj)["passive"]
    assert line(s)[1] == "fish PASS-see" and s["en"] == "The fish is seen."
    assert any(n["topic"] == "Voice" and "become" in n["text"] for n in SN.grammar_notes(lj))


def test_serial_verbs_only_when_drawn():
    lj = _more(TAKE="ambil", COME="datan", GO="pergi", RUN="lari")
    assert "serial" not in by_id(lj)
    lj["typology"]["serial_verbs"] = "yes"
    s = by_id(lj)["serial"]
    assert line(s)[1] == "man take fish come"
    lj["typology"].update(word_order="SOV", head_direction="final")
    assert line(by_id(lj)["serial"])[1] == "man fish take come"
    n = next(n for n in SN.grammar_notes(lj) if n["topic"] == "Serial verbs")
    assert "direction" in n["text"]


def test_reduplication_sentence_and_note():
    lj = lect()
    assert "redup" not in by_id(lj)
    lj["processes"] = {"redup": {"fn": "ITER", "shape": "CV", "side": "pre"}}
    lj["lexicon"]["HIT"] = {"ipa": "pukul", "roman": "pukul", "pos": "V"}
    s = by_id(lj)["redup"]
    assert "pu-pukul" in line(s)[0] and "ITER-hit" in line(s)[1] and "again and again" in s["en"]
    n = next(n for n in SN.grammar_notes(lj) if n["topic"] == "Reduplication")
    assert "again and again" in n["text"]


def test_split_ergativity_by_person_and_by_aspect():
    lj = lect(alignment="split")
    lj["grams"] = [gram("ACC", "o", 2, "post", "NP"), gram("ERG", "ne", 2, "post", "NP"),
                   gram("PAST", "ta", 2, "post", "V")]
    lj["processes"] = {"split": "person"}
    sp = by_id(lj)
    assert line(sp["split"])[1] == "man-ERG see 1SG-ACC"
    assert line(sp["transitive"])[1] == "woman-ERG see dog"
    lj["processes"] = {"split": "aspect"}
    sp = by_id(lj)
    assert "split" not in sp
    assert line(sp["transitive"])[1] == "woman see dog-ACC"
    assert line(sp["tense"])[1] == "man-ERG eat-PST fish"
    case = next(n for n in SN.grammar_notes(lj) if n["topic"] == "Case")
    assert "split by aspect" in case["text"]


def test_inclusive_we_sentence_and_pronoun_note():
    lj = lect()
    lj["lexicon"]["WE"] = {"ipa": "kami", "roman": "kami", "pos": "FUNC"}
    assert "clusive" not in by_id(lj)
    lj["lexicon"]["WE (INCLUSIVE)"] = {"ipa": "kita", "roman": "kita", "pos": "FUNC"}
    s = by_id(lj)["clusive"]
    assert line(s)[1].startswith("1PL.INCL") and "kami" in s["note"]
    n = next(n for n in SN.grammar_notes(lj) if n["topic"] == "Pronouns")
    assert "kita" in n["text"] and "kami" in n["text"]


def test_numerals_note_uses_the_lects_own_words():
    """The numerals note quotes the lect's own composite words and its counting system's recipes (polish lane: it built
    'ten one' from the typology label, which disagreed with the word lists)."""
    lj = lect(numeral_base="vigesimal", numeral="NumN")
    lj["lexicon"].update({c: {"ipa": f, "roman": f, "pos": "A"} for c, f in
                          (("ONE", "sa"), ("TWO", "dua"), ("FIVE", "lima"), ("TEN", "pulu"), ("TWENTY", "kawan"),
                           ("ELEVEN", "pulsa"), ("FIFTEEN", "pulima"), ("THIRTY", "kawpu"), ("FORTY", "dukaw"))})
    lj["systems"] = {"numeral": {"label": "vigesimal", "system": "hybrid", "quinary": False}}
    n = SN.numerals_note(SN.View(lj))
    assert n["topic"] == "Numerals" and "twenties" in n["text"]
    shown = {x[0]: x[2] for x in n["ex"]}
    assert shown["pulsa"].startswith("11 = 10 + 1") and shown["kawpu"].startswith("30 = 20 + 10")
    assert shown["dukaw"].startswith("40 = 20 × 2")
    lj["systems"] = {}
    assert SN.numerals_note(SN.View(lj)) is None


# ---- demo-page bugs (grammar B, 2026-11-08) -------------------------------------------------------------------------------

def test_person_nouns_take_the_person_class():
    from planet.language import grammar as GR
    for c in ("MERCHANT", "SOLDIER", "TEACHER", "THIEF", "KING", "HUNTER"):
        assert GR.semantic_group(c) == "person", c
    lj = lect(gender="animacy")
    lj["lexicon"]["MERCHANT"] = {"ipa": "dagaŋ", "roman": "dagaŋ", "pos": "N"}
    lj["grams"] = [gram("CLASS:1", "o", 2, "pre", "N", ("PERSON", "G066", "concept")),
                   gram("CLASS:2", "e", 2, "pre", "N", ("STONE", "G066", "concept"))]
    lj["classes"] = {"kind": "animacy", "classes": [[1, "animate", "CLASS:1"], [2, "inanimate", "CLASS:2"]]}
    assert SN.class_of(SN.View(lj), "MERCHANT") == ("CLASS:1", "ANIM")


def test_class_numbers_have_no_gap_and_no_twin():
    import numpy as np
    from planet.language import grammar as GR
    g = GR.Grammar(typology=GR.Typology({"gender": "classes"}), aims=GR.Typology({"gender": "classes"}), shown={})
    g.class_system = GR.ClassSystem("classes")
    rng = np.random.default_rng(1)
    for grp in ("person", "plant", "animal"):
        GR.add_class(g, rng, None, None, 1.0, group=grp)
    g.class_system.classes = [c for c in g.class_system.classes if c.k != 1]   # (class 1 lost)
    GR.add_class(g, rng, None, None, 1.0, group="liquid")
    ks = [c.k for c in g.class_system.classes]
    assert len(set(ks)) == len(ks) == 3 and ks[-1] == 4
    # the page numbers them 1..n
    lj = lect(gender="classes")
    lj["grams"] = [gram(f"CLASS:{k}", f, 2, "pre", "N") for k, f in ((2, "mu"), (3, "ki"), (4, "ma"))]
    lj["classes"] = {"kind": "classes", "classes": [[2, "plant", "CLASS:2"], [3, "animal", "CLASS:3"],
                                                    [4, "liquid", "CLASS:4"]]}
    txt = next(n["text"] for n in SN.grammar_notes(lj) if n["topic"] == "Gender and noun classes")
    assert "class 1 for" in txt and "class 3 for" in txt and "class 4" not in txt
    assert by_id(lj)["transitive"]["w"][-1][1] == "CL2-dog"


def test_dual_note_shows_the_dual():
    lj = lect()
    lj["grams"] = [gram("PL", "s", 2, "post", "N"), gram("DU", "ki", 2, "post", "N")]
    n = next(n for n in SN.grammar_notes(lj) if n["topic"] == "Number")
    assert "dual" in n["text"].lower()
    assert [e[2] for e in n["ex"]] == ["dog", "dogs", "two dogs"] and n["ex"][2][1] == "dog-DU"


def test_correlative_note_quotes_its_own_verb():
    lj = lect(relative="other")
    del lj["lexicon"]["SING"]
    lj["lexicon"]["DANCE"] = {"ipa": "tari", "roman": "tari", "pos": "V"}
    n = next(n for n in SN.grammar_notes(lj) if n["topic"] == "Relative clauses")
    assert "who dances, that woman" in n["text"] and "sings" not in n["text"]


def test_free_classifier_example_shows_the_classifier():
    lj = lect(numeral_classifiers="yes")
    lj["grams"] = [gram("CLASS:1", "ekor", 0, "pre", "N", ("ANIMAL", "G066", "concept")),
                   gram("CLASS:2", "buah", 0, "pre", "N", ("STONE", "G066", "concept"))]
    lj["classes"] = {"kind": "classifiers", "classes": [[1, "animal", "CLASS:1"], [2, "abstract", "CLASS:2"]]}
    n = next(n for n in SN.grammar_notes(lj) if n["topic"] == "Gender and noun classes")
    assert n["ex"] and all("CLF" in e[1] for e in n["ex"])
    assert n["ex"][0][2] == "two dogs"


def test_possession_note_names_the_sentences_thing():
    lj = lect()
    lj["lexicon"]["BOAT"] = {"ipa": "perahu", "roman": "perahu", "pos": "N"}
    s = SN.utterances(lj)
    assert next(x for x in s if x["id"] == "possession")["en"] == "My mother has a boat."
    n = next(n for n in SN.grammar_notes(lj, s) if n["topic"] == "Possession")
    assert "my mother has a boat" in n["text"] and "dog" not in n["text"]


def test_note_prose_names_the_joined_form():
    lj = lect(word_order="SOV", head_direction="final")
    lj["grams"] = [gram("PAST", "an", 1, "pre", "V"), gram("3PL", "e", 1, "post", "V")]
    n = next(n for n in SN.grammar_notes(lj) if n["topic"] == "Tense and aspect")
    forms = " ".join(e[0] for e in n["ex"])
    assert "am=" in forms or "aŋ=" in forms or "an=" in forms
    if "an=" not in forms:
        assert "before a stop" in n["text"]


def test_no_tool_jargon_in_notes_or_sentences():
    for kw in ({}, {"predicative_possession": "other"}, {"predicative_possession": "locational"}, {"relative": "other"}):
        lj = lect(**kw)
        SN.enrich(lj)
        blob = json.dumps(lj["sentences"]) + json.dumps(lj["grammar_notes"])
        for bad in ("G05", "G06", "the lane", "sketch.py", "Grambank marks"):
            assert bad not in blob, (kw, bad)


# --- grammar phase C (2026-11-08) -------------------------------------------------------------------------------------

def test_question_copula_relativizer_grams_replace_the_stand_ins():
    lj = lect(polar_question="final_particle")
    lj["grams"] = [gram("Q", "ma", 0, "post", "VP", ("NOT", "X47", "concept")),
                   gram("COP", "da", 2, "post", "VP", ("STAND", "X49", "concept")),
                   gram("REL", "ju", 0, "pre", "VP", ("WHO", "G058", "concept"))]
    s = by_id(lj)
    assert line(s["polar"])[1].endswith(" Q") and line(s["polar"])[0].endswith(" ma")
    assert line(s["copula"])[1] == "man that hunter-COP"
    assert line(s["relative"]) == ("mi tau kana ju lan", "1SG know woman REL sing")


def test_concord_on_adjective_demonstrative_and_verb():
    lj = lect(gender="sex")
    lj["grams"] = [gram("CLASS:1", "o", 2, "pre", "N", ("MAN", "G066", "concept")),
                   gram("CLASS:2", "e", 2, "pre", "N", ("WOMAN", "G066", "concept")),
                   gram("3SG", "a", 2, "pre", "V")]
    lj["processes"] = {"concord": ["adj", "dem", "verb"]}
    s = by_id(lj)
    assert line(s["transitive"])[1] == "F-woman F-see M-dog"
    assert line(s["copula"])[1].startswith("M-man M-that")
    assert "concord" in s["transitive"]["note"]


def test_complement_topic_focus_sentences():
    lj = lect(word_order="free", head_direction="initial")
    lj["lexicon"]["SAY"] = {"ipa": "sema", "roman": "sema", "pos": "V"}
    lj["grams"] = [gram("COMP", "ko", 0, "pre", "VP", ("SAY", "G023", "concept")),
                   gram("FOC", "nu", 1, "post", "NP", ("COP", "G057", "gram"))]
    s = by_id(lj)
    assert line(s["complement"])[1] == "man say COMP dog sleep"
    assert line(s["topic"])[1] == "fish man eat"
    assert line(s["focus"])[1] == "man=FOC see dog"


def test_valence_chain_incorporation_and_voice_sentences():
    lj = lect(word_order="VSO")
    lj["lexicon"].update({"COME": {"ipa": "datan", "roman": "datan", "pos": "V"},
                          "BUILD": {"ipa": "bina", "roman": "bina", "pos": "V"}})
    lj["grams"] = [gram("APPL", "i", 2, "post", "V"), gram("RECP", "an", 2, "post", "V"), gram("SS", "ta", 2, "post", "V"),
                   gram("PV", "in", 2, "post", "V"), gram("DEF", "aŋ", 0, "pre", "NP")]
    lj["processes"] = {"incorp": True}
    s = by_id(lj)
    assert line(s["applicative"])[1] == "build-APPL DEF man DEF child house"
    assert line(s["reciprocal"])[1].startswith("see-RECP")
    assert "SS" in line(s["chain"])[1] and s["chain"]["en"].startswith("The man comes and")
    assert line(s["incorp"])[1] == "eat-fish DEF man"
    assert line(s["voice_pv"])[1] == "eat-PV man PIV fish"


def test_infix_stem_change_inflection_class_portmanteau_second_position():
    lj = lect(word_order="SOV", head_direction="final")
    lj["grams"] = [gram("PAST", "um", 2, "pre", "V"), gram("PL", "s", 2, "post", "N"),
                   gram("LOC", "ta", 2, "post", "NP"), gram("PL+LOC", "sat", 3, "post", "NP"),
                   gram("NEG", "ne", 1, "pre", "VP")]
    lj["grams"][1]["alt_ipa"] = "n"
    lj["processes"] = {"infix": {"fn": "PAST"}, "iclass": {"PL": {"salt": 7, "share": 0.5}},
                       "stem_change": {"FUT": [["a", "e"]]}, "second": True}
    v = SN.View(lj)
    w = [SN.Word("lis", "see", "SEE")]
    SN.attach(v, w, 0, "PAST")
    assert SN.render_word(v, w[0])[:2] == ("l<um>is", "<PST>see")
    w = [SN.Word("kum", "eat", "EAT")]
    assert not SN.attach(v, w, 0, "FUT")
    w = [SN.Word("nam", "x", "X")]
    assert SN.attach(v, w, 0, "FUT") and w[0].form == "nem" and w[0].gloss == "x\\FUT"
    forms = {c: SN.render_word(v, SN.noun_phrase(v, c, plural=True).words[0])[0] for c in ("DOG", "FISH", "HOUSE", "BIRD")}
    assert {f.split("-")[1] for f in forms.values()} <= {"s", "n"}
    np_ = SN.noun_phrase(v, "HOUSE", plural=True)
    SN._np_gram(v, np_, "LOC")
    assert SN.render_word(v, np_.words[0])[1] == "house-PL.LOC"
    neg = by_id(lj)["negation"]
    assert line(neg)[1].split()[0].endswith("=NEG") and "second position" in neg["note"]


def test_second_read_sentence_fixes():
    """Grammar C, from the read of phase B's demo: object agreement shown on a transitive verb; reduplication a copy of
    today's stem; a stored cell whose stem alternates shown unsegmented; 'DAT' kept in capitals; the genitive named;
    numerals say which is times and which plus; an imperative with an object marker says so."""
    lj = lect(word_order="SOV", head_direction="final", numeral="NNum", numeral_base="decimal")
    lj["lexicon"].update({c: {"ipa": f, "roman": f, "pos": "N"} for c, f in
                          (("TEN", "pu"), ("ONE", "sa"), ("THREE", "tiga"), ("AND", "dan"), ("GIVE", "beri"))})
    lj["lexicon"]["GIVE"]["pos"] = "V"
    lj["grams"] = [gram("3SG.O", "nja", 2, "post", "V"), gram("DAT", "ke", 0, "post", "NP"),
                   gram("GEN", "nu", 1, "post", "NP")]
    lj["processes"] = {"redup": {"fn": "ITER", "shape": "CV", "side": "pre"}}
    lj["paradigms"] = {"verbs": {"rows": [{"concept": "SEE", "cells": {"lemma": {"ipa": "lis"}},
                                            "segmented": {"ITER": "la-lus"}}]}}
    notes = {n["topic"]: n for n in SN.grammar_notes(lj)}
    assert "see" in notes["Object agreement"]["ex"][0][1]
    assert notes["Giving (two objects)"]["text"].startswith("DAT ")
    assert "genitive marker, a clitic" in notes["Possession"]["text"]
    v = SN.View(lj)
    w = SN.verb(v, "SEE", redup=True)[0]
    assert SN.render_word(v, w[0])[0] == "li-lis"
    imp = by_id(lj)["imperative"]
    assert "marks its object" in imp["note"]


def test_third_read_fixes():
    """Grammar D, from demo read 3: the imperative object keeps its case; a vowel-initial stem reduplicates with no
    glide; a stored cell for the inner markers carries the outer ones; a bound copula in the possession sentence; a
    fronted question word takes its free case word along; serial-verb doers take the ergative; no jargon; glide
    allomorphs name their vowels; same-sounding markers and stem-vowel persons are named; head-marked possession is
    not 'no marker'; the antipassive names no ergative where there is none."""
    lj = lect(alignment="nom-acc", predicative_possession="other")
    lj["grams"] = [gram("ACC", "o", 0, "post", "NP"), gram("COP", "da", 2, "post", "N"), gram("COM", "sa", 2, "post", "NP"),
                   gram("ANTIP", "si", 2, "post", "V"), gram("1SG.O", "n", 2, "post", "V"),
                   gram("1PL.O", "n", 2, "post", "V"), gram("3SG.POSS", "ri", 2, "post", "N")]
    lj["lexicon"]["GO"] = {"ipa": "ulo", "roman": "ulo", "pos": "V"}
    s = by_id(lj)
    assert line(s["imperative"])[1] == "eat fish ACC"
    assert line(s["content"])[1].startswith("what ACC ") and "with its case marker" in s["content"]["note"]
    assert line(s["possession"])[1].endswith("-COM-COP") and "COP" not in line(s["possession"])[1].split()[-2:-1]
    assert "ergative" not in s["antipassive"]["note"]
    notes = {n["topic"]: n for n in SN.grammar_notes(lj)}
    assert "1PL.OBJ and 1SG.OBJ are both n" in notes["Word shapes"]["text"]
    assert "with no marker" not in notes["Possession"]["text"] and "person marker" in notes["Possession"]["text"]
    txt = " ".join(n["text"] for n in notes.values()) + " ".join(x.get("note", "") for x in s.values())
    assert "gram)" not in txt and "gram is tracked" not in txt
    # reduplication of a vowel-initial stem: a bare copy, no glide
    lj["processes"] = {"redup": {"fn": "ITER", "shape": "CV", "side": "pre"}}
    v = SN.View(lj)
    w = SN.verb(v, "GO", redup=True)[0]
    assert SN.render_word(v, w[0])[0] == "u-ulo"
    # a stored class cell under a plural: the cell's own stem shape, the plural added outside it
    lj = lect()
    lj["lexicon"]["DOG"] = {"ipa": "aru", "roman": "aru", "pos": "N"}
    lj["grams"] = [gram("CLASS:1", "ne", 2, "pre", "N"), gram("PL", "ŋi", 2, "pre", "N")]
    lj["paradigms"] = {"nouns": {"rows": [{"concept": "DOG", "cells": {"lemma": {"ipa": "aru"}},
                                           "segmented": {"CLASS:1": "n-aru"}}]}}
    v = SN.View(lj)
    w = SN.Word("aru", "dog", "DOG")
    SN.attach(v, [w], 0, "CLASS:1", "CL1")
    SN.attach(v, [w], 0, "PL")
    assert SN.render_word(v, w)[0] == "ŋi-n-aru"
    # serial verbs in an ergative lect: the doer takes the ergative
    lj = _more(TAKE="ambil", COME="datan")
    lj["typology"].update(alignment="erg-abs", serial_verbs="yes")
    lj["grams"] = [gram("ERG", "ku", 2, "post", "NP")]
    assert "man-ERG" in line(by_id(lj)["serial"])[1]
    # glide allomorphs say which vowels they follow
    assert SN._where("a", "ja", {"j", "w"}) == "ja after a front or central vowel"
    assert SN._where("a", "wa", {"j", "w"}) == "wa after a back or rounded vowel"
    # a person shown only by a stem change: in the sentence and in the notes, not 'no marker yet'
    lj = lect()
    lj["grams"] = [gram("1SG", "mo", 2, "pre", "V")]
    lj["processes"] = {"stem_change": {"2SG": [["i", "e"]]}}
    lj["lexicon"]["HEAR"] = {"ipa": "dinik", "roman": "dinik", "pos": "V"}
    lj["lexicon"]["THUNDER"] = {"ipa": "kulot", "roman": "kulot", "pos": "N"}
    s = by_id(lj)["polar"]
    assert "hear\\2SG" in line(s)[1] and "stem's vowel" in s["note"]
    notes = {n["topic"]: n for n in SN.grammar_notes(lj)}
    assert "2SG" not in notes["Person agreement"]["text"].split("No marker yet for")[-1].split(".")[0]
    assert "2SG subject (you)" in notes["Word shapes"]["text"] and notes["Word shapes"]["ex"]


def test_sentence_spelling_is_the_book_spelling():
    lj = lect()
    s = by_id(lj)["transitive"]
    assert s["roman"] == SN.book_spelling(lj, s["ipa"].split(" "))


def test_phase_d_sentences_and_notes():
    """Grammar D: three-way demonstratives, graded pasts, the newer aspects, the mirative, polite address with an
    honorific, comparison by type, obviation and differential object marking."""
    lj = _more(THIS="ki", OLD="tua", CLIMB="naik", FINISH="habis")
    lj["lexicon"]["YOU"] = {"ipa": "kamu", "roman": "kamu", "pos": "N"}
    lj["typology"].update(alignment="nom-acc")
    lj["grams"] = [gram("DIST", "neja", 0, "post", "NP"), gram("PAST", "su", 0, "post", "V"),
                   gram("RECPST", "baru", 0, "post", "V"), gram("REMPST", "lama", 0, "post", "V"),
                   gram("COMPL", "bis", 1, "post", "V"), gram("MIR", "pa", 1, "post", "VP"),
                   gram("HON", "an", 2, "post", "V"), gram("OBV", "ri", 2, "post", "N"), gram("ABL", "da", 0, "post", "NP"),
                   gram("ACC", "o", 0, "post", "NP")]
    lj["processes"] = {"polite": {"kind": "plural", "concept": "YOU"}, "compare": "locational", "dom": "animate"}
    s = by_id(lj)
    assert line(s["deixis"])[1].startswith("man DIST") and "three distances" in s["deixis"]["note"]
    assert "PST.REM" in line(s["remote"])[1] and "from nearer to further back: PST.RCT, PST, PST.REM" in s["remote"]["note"]
    assert "COMPL" in line(s["aspect"])[1] and "eaten the fish up" in s["aspect"]["en"]
    assert "MIR" in line(s["mirative"])[1]
    assert line(s["polite"])[1].startswith("2PL.POL") and "HON" in line(s["polite"])[1]
    assert "dog ABL" in line(s["comparative"])[1] and "bigger" in s["comparative"]["en"]
    assert "OBV" in line(s["obviative"])[1]
    assert "ACC" in line(s["transitive"])[1]                       # (a dog is animate: marked)
    lj2 = copy.deepcopy(lj)
    lj2["lexicon"]["DOG"]["ipa"] = "x"
    del lj2["lexicon"]["DOG"], lj2["lexicon"]["BIRD"], lj2["lexicon"]["FISH"]
    lj2["lexicon"]["STONE"] = {"ipa": "batu", "roman": "batu", "pos": "N"}
    assert "ACC" not in line(by_id(lj2)["transitive"])[1]          # (a stone is not: bare)
    notes = {n["topic"]: n for n in SN.grammar_notes(lj)}
    assert "three distances" in notes["Demonstratives"]["text"] and len(notes["Demonstratives"]["ex"]) >= 3
    assert "Polite address" in notes and "Comparison" in notes and "Obviation" in notes
    assert "only animate objects" in notes["Case"]["text"]
    for kind, want in (("exceed", "exceed"), ("particle", "than"), ("conjoined", "small")):
        lj["processes"]["compare"] = kind
        lj["lexicon"]["SMALL"] = {"ipa": "kecil", "roman": "kecil", "pos": "A"}
        assert want in line(by_id(lj)["comparative"])[1], kind


def test_rulings_class_labels_animate_fallback_and_own_sentence():
    """Owner rulings 11-08 (PW-1538): a class marked on the noun with nothing agreeing is 'noun class marking (no
    agreement)', not gender; an animate noun with no class of its own takes the person class before the inanimate
    default; one per-lect sentence from the people's own life (faith, home, food); no 'rank' claim for politeness."""
    from planet.language import grammar as GR
    assert GR.gender_label("sex", []) == GR.GENDER_NO_AGREEMENT and GR.gender_label("sex", ["adj"]) == "sex"
    assert GR.gender_label("none", ["adj"]) == "none"
    assert GR.fallback_groups("animal")[0] == "person" and GR.fallback_groups("liquid") == GR.CLASS_FALLBACK
    lj = lect(gender="classes")
    lj["grams"] = [gram("CLASS:1", "mu", 2, "pre", "N"), gram("CLASS:2", "ki", 2, "pre", "N")]
    lj["classes"] = {"kind": "classes", "classes": [[1, "person", "CLASS:1"], [2, "abstract", "CLASS:2"]]}
    txt = next(n["text"] for n in SN.grammar_notes(lj) if n["topic"] == "Gender and noun classes")
    assert GR.GENDER_NO_AGREEMENT in txt and "animals" in txt
    assert by_id(lj)["transitive"]["w"][-1][1] == "CL1-dog"   # (the dog takes the person class, not the default)
    lj["processes"] = {"concord": ["adj"]}
    txt = next(n["text"] for n in SN.grammar_notes(lj) if n["topic"] == "Gender and noun classes")
    assert GR.GENDER_NO_AGREEMENT not in txt
    lj = lect()
    lj["lexicon"]["WE"] = {"ipa": "kami", "roman": "kami", "pos": "FUNC"}
    lj["lexicon"]["crop:millet"] = {"ipa": "dawa", "roman": "dawa", "pos": "N"}
    own = by_id(lj).get("own")
    assert own is not None and own["en"] == "We eat millet."
    lj["home"] = "RIVER"
    lj["lexicon"]["RIVER"] = {"ipa": "sunai", "roman": "sunai", "pos": "N"}
    lj["lexicon"]["DWELL (LIVE, RESIDE)"] = {"ipa": "tingal", "roman": "tingal", "pos": "V"}
    lj["lexicon"]["PRAY"] = {"ipa": "doa", "roman": "doa", "pos": "V"}
    lj["lexicon"]["name:god:7"] = {"ipa": "lato", "roman": "lato", "pos": "NAME"}
    ens = set()
    for k in range(12):
        lj["id"] = f"d{k}"
        ens.add(by_id(lj)["own"]["en"])
    assert ens == {"We eat millet.", "We live by the river.", "We pray to Lato."}


def test_marker_beside_its_identical_source_is_said_once():
    """PW-1537 R1: a free marker still identical to the word it came from is not said twice beside it (haplology)."""
    v = SN.View(lect())
    out = SN.haplology(v, [SN.Word("ɡbinaf", "that", "THAT"), SN.Word("ɡbinaf", "COP"), SN.Word("ka", "dog", "DOG")])
    assert [w.gloss for w in out] == ["that.COP", "dog"] and v.extra


def test_numeral_note_only_where_the_parts_are_heard():
    """PW-1537 R8: '11 = 10 + 1' only when 'ten' and 'one' can be heard in the form."""
    lj = lect()
    lj["systems"] = {"numeral": {"system": "decimal"}}
    lj["lexicon"].update({"TEN": {"ipa": "pulu", "pos": "NUM"}, "ONE": {"ipa": "sa", "pos": "NUM"},
                          "ELEVEN": {"ipa": "pulusa", "pos": "NUM"}, "FIFTEEN": {"ipa": "kito", "pos": "NUM"},
                          "FIVE": {"ipa": "lima", "pos": "NUM"}})
    n = SN.numerals_note(SN.View(lj))
    texts = [e[2] for e in n["ex"]]
    assert any(t.startswith("11 = 10 + 1") for t in texts), texts
    assert any(t.startswith("15: built as 10 + 5") and "worn" in t for t in texts), texts
