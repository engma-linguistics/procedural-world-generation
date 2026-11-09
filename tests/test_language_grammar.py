"""grammar.py: typology draw and drift, grams on the ladder, paradigms, names through grammar (not slow)."""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pytest

from planet.language import grammar as G
from planet.language.percepts import from_ipa, word_ipa


@dataclass
class W:
    concept: str
    form: tuple
    pos: str = "N"
    freq_class: int = 2


def lex(**kw) -> dict:
    """A tiny lexicon: concept -> W (duck-typed like lexicon.Word)."""
    base = {"WATER": ("wata", "N"), "PERSON": ("muntu", "N"), "DOG": ("kawa", "N"), "TREE": ("tima", "N"),
            "GO": ("kele", "V"), "EAT": ("lija", "V"), "SEE": ("bona", "V"), "GIVE": ("pana", "V"),
            "NOT": ("sila", "FUNC"), "MANY": ("puli", "A"), "THAT": ("nako", "FUNC"), "AT": ("mosi", "FUNC"),
            "IN": ("tuka", "FUNC"), "I": ("ani", "FUNC"), "THOU": ("wena", "FUNC"), "HE OR SHE OR IT": ("jesu", "FUNC"),
            "WE": ("tiso", "FUNC"), "THEY": ("bano", "FUNC"), "ONE": ("moja", "A"), "TWO": ("pili", "A"),
            "HOLD": ("kamata", "V"), "COME": ("tola", "V"), "SAY": ("lowa", "V"), "CHILD (YOUNG HUMAN)": ("mwana", "N"),
            "HOUSE": ("numba", "N"), "EARTH (SOIL)": ("siko", "N"), "TONGUE": ("limi", "N"), "PEOPLE": ("pantu", "N"),
            "BELLY": ("tumbo", "N"), "WITH": ("nala", "FUNC"), "YESTERDAY": ("jana", "A"), "ANIMAL": ("nama", "N"),
            "NAME": ("sina", "N"), "TAKE": ("tava", "V")}
    base.update(kw)
    return {k: W(k, tuple(from_ipa(f)), pos) for k, (f, pos) in base.items()}


class Inv:
    def __init__(self):
        self.consonants = from_ipa("ptkmnslw")
        self.vowels = from_ipa("aiu")
        self.tones = []


def _grammar(seed=0, **typ_over):
    rng = np.random.default_rng(seed)
    typ = G.draw_typology(rng)
    typ.update(typ_over)
    G._derive(typ)
    return rng, G.proto_grammar(rng, Inv(), lex(), typ)


# --- typology ---------------------------------------------------------------------------------------------------------

def test_typology_correlations_hold():
    rng = np.random.default_rng(1)
    draws = [G.draw_typology(rng) for _ in range(500)]
    ov = [t for t in draws if t.ov() == "OV"]
    vo = [t for t in draws if t.ov() == "VO"]
    assert len(ov) > 100 and len(vo) > 100
    assert np.mean([t["adposition"] == "post" for t in ov]) > 0.75     # OV -> postpositions
    assert np.mean([t["adposition"] == "pre" for t in vo]) > 0.65       # VO -> prepositions
    assert np.mean([t["genitive"] == "GN" for t in ov]) > np.mean([t["genitive"] == "GN" for t in vo]) + 0.3
    assert np.mean([t["relative"] == "RelN" for t in ov]) > np.mean([t["relative"] == "RelN" for t in vo]) + 0.2
    counts = {w: sum(t["word_order"] == w for t in draws) for w in ("SOV", "SVO", "VSO")}
    assert counts["SOV"] > counts["SVO"] > counts["VSO"] > 0
    assert 0.33 < counts["SOV"] / 500 < 0.50
    assert all(t["head_direction"] == "final" for t in ov) and all(t["head_direction"] == "initial" for t in vo)
    assert len(draws[0]) >= 40


def test_typology_works_without_tables():
    T = G.load_tables(use_files=False)
    assert T.sources["paths"] == "builtin" and T.paths
    t = G.draw_typology(np.random.default_rng(3), table=T)
    assert t["word_order"] in G._FB_ORDER and len(t) >= 40


def test_drift_word_order_stable_articles_fickle():
    rng = np.random.default_rng(2)
    wo = art = 0
    n = 300
    for _ in range(n):
        t = G.draw_typology(rng)
        t0 = dict(t)
        G.drift(rng, t, 100)
        wo += t["word_order"] != t0["word_order"]
        art += (t["definite_article"] != t0["definite_article"]) or (t["indefinite_article"] != t0["indefinite_article"])
    assert wo / n < 0.08          # word order kept over 100 generations most of the time
    assert art > 2 * max(wo, 1)   # articles flip far more often


def test_drift_accepts_a_grammar():
    rng, g = _grammar(4)
    ch = G.drift(rng, g, 5000, kyr=3.0)
    assert ch and any("typology" in e[1] for e in g.events)


# --- grams on the ladder ----------------------------------------------------------------------------------------------

def test_proto_starts_low():
    """A proto starts with 1-3 free or clitic grams; one aiming at a big case system (PW-1586) also starts with its case
    endings already bound, 6+ cases (WALS 49A's bins), and nothing else bound."""
    many = 0
    for s in range(20):
        _, g = _grammar(s)
        born = [x for x in g.grams if x.history[-1:] and "case system it was born with" in x.history[-1][1]]
        plain = [x for x in g.grams if not x.function.startswith("CLASS") and x not in born]
        assert 1 <= len(plain) <= 3
        assert all(x.level <= G.CLITIC for x in g.grams if x not in born)
        if G.aims(g)["case"] == "many":
            many += 1
            assert all(x.level == G.AFFIX and x.function in G.CASE_FNS for x in born)
            assert G.case_count(g) >= G.CASE_MANY and G.realised_value("case", g) == "many"
        else:
            assert not born and G.complexity(g)["obligatory"] == 0
        assert len([e for e in g.exemplars if e.pos == "N"]) == 4 and len([e for e in g.exemplars if e.pos == "V"]) == 4
    assert many >= 3


def test_go_future_binds_and_enters_verb_cells(monkeypatch):
    monkeypatch.setattr(G, "ABANDON", 0.0)   # (binding is the point here, not whether this periphrasis survives)
    rng, g = _grammar(5, word_order="SOV", future="marked")
    g.grams = [x for x in g.grams if x.function != "FUT"]
    gr = G.recruit(rng, g, lex(), kyr=20.0, function="FUT", source="GO")
    assert gr is not None and gr.source[0] == "GO" and gr.level == 0
    assert tuple(gr.form) == tuple(from_ipa("kele"))
    lx = lex()
    for k in range(400):
        G.step(rng, g, 10, Inv(), lx, l2_share=0.0, population=2000, isolation=0.8, kyr=20 - k * 0.05)
        if gr.level >= G.AFFIX or not gr.live:
            break
    assert gr.live and gr.level >= G.AFFIX
    assert "GO" in lx and word_ipa(lx["GO"].form) == "kele"     # the source word stays a word
    verbs = [e for e in g.exemplars if e.pos == "V"]
    for e in verbs:
        assert e.cells[("FUT",)] == (e.stem + gr.form if gr.side == "post" else gr.form + e.stem)
        assert e.morph(("FUT",), "FUT") == tuple(gr.form)


def _pl_grammar():
    rng, g = _grammar(6, word_order="SOV", numeral="NNum", number="sg-pl")
    g.grams = []
    g.grams.append(G.Gram("PL", tuple(from_ipa("ti")), "N", "post", G.AFFIX, ("MANY", "X02"), 10.0, id="PL#x"))
    G._sync_cells(g)
    return rng, g


def _drop_final_vowel(form):
    return tuple(form[:-1]) if len(form) > 1 and form[-1].kind == "V" else tuple(form)


def test_final_vowel_loss_makes_allomorphy_and_analogy_levels_it():
    rng, g = _pl_grammar()
    assert G.complexity(g)["allomorphy"] == 0
    nouns = [e for e in g.exemplars if e.pos == "N"]
    assert all(word_ipa(e.cells[("PL",)]) == word_ipa(e.stem) + "ti" for e in nouns)
    n = G.apply_rule_to_grammar(g, _drop_final_vowel, "final_vowel_loss", 9.0)
    assert n > 0
    pl = g.gram("PL")
    assert word_ipa(pl.form) == "t"
    c = G.complexity(g)
    assert c["allomorphy"] >= 4 and c["stem_alternations"] >= 4     # wata ~ watat-: the stem keeps its vowel inside
    w = next(e for e in nouns if e.concept == "WATER")
    assert word_ipa(w.stem) == "wat" and word_ipa(w.cells[("PL",)]) == "watat"
    for e in nouns:
        G.analogy(g, e, ("PL",), 8.0)
    assert G.complexity(g)["allomorphy"] == 0
    assert word_ipa(w.cells[("PL",)]) == "watt"
    assert any("analogy" in ev[1] for ev in g.events)


def test_analogy_hazard_fires_in_step():
    rng, g = _pl_grammar()
    G.apply_rule_to_grammar(g, _drop_final_vowel, "final_vowel_loss", 9.0)
    before = G.complexity(g)["allomorphy"]
    for k in range(100):
        G.step(rng, g, 10, Inv(), None, l2_share=0.3, population=50000, isolation=0.2, kyr=9 - k * 0.05)
    assert any("analogy" in ev[1] for ev in g.events)
    assert G.complexity(g)["allomorphy"] < before


def test_erosion_to_nothing_loses_the_gram_and_removes_cells():
    rng, g = _pl_grammar()
    G.apply_rule_to_grammar(g, lambda f: tuple(f) if tuple(f) != tuple(from_ipa("ti")) else (), "kill", 5.0)
    # cells kept the affix (it sits inside words), so the gram's form follows the cells and survives
    assert g.gram("PL") is not None
    gone = lambda f: tuple(s for s in f if not (s.kind == "C" and s.place == 2 and s.manner == 0))  # noqa: E731
    G.apply_rule_to_grammar(g, lambda f: _drop_final_vowel(gone(f)) if f else f, "t_loss", 4.0)
    G.apply_rule_to_grammar(g, lambda f: _drop_final_vowel(gone(f)) if f else f, "t_loss", 4.0)
    pl = next(x for x in g.grams if x.function == "PL")
    if pl.live:   # survives only as stem marking
        assert pl.level == G.FUSED and not pl.form
    else:
        assert all(("PL",) not in e.cells for e in g.exemplars)


def test_l2_share_lowers_fusion_measured():
    def run(l2):
        out = []
        for s in range(16):
            rng, g = _grammar(100 + s)
            lx = lex()
            for k in range(60):
                G.step(rng, g, 10, Inv(), lx, l2_share=l2, population=5000, isolation=0.5, kyr=20 - k * 0.25)
            c = G.complexity(g)
            out.append(c["obligatory"] + c["mean_level"])
        return float(np.mean(out))
    low, high = run(0.0), run(0.6)
    assert high < 0.6 * low


def test_reanalysis_perfect_to_past():
    rng, g = _grammar(8)
    g.grams = [G.Gram("PERF", tuple(from_ipa("ka")), "V", "post", G.AFFIX, ("HOLD", "G006"), 10.0, id="PERF#1")]
    T = G.load_tables()
    import dataclasses
    T2 = dataclasses.replace(T, paths=[p for p in T.paths if p.from_gram and p.sources == ("PERF",)])
    G._recruit(rng, g, lex(), 5.0, T2, {}, Inv())
    assert g.grams[0].function == "PAST" and "reanalysed" in g.grams[0].history[-1][1]


# --- names through grammar --------------------------------------------------------------------------------------------

def test_people_set_with_five_classes():
    rng, g = _grammar(9, gender="classes", demonstrative="DemN")
    g.class_system = G.ClassSystem("classes")
    g.grams = [x for x in g.grams if not x.function.startswith("CLASS")]
    forms = {"person": "mu", "people": "ba", "manner": "lu", "abstract": "bu", "plant": "mi"}
    for grp, f in forms.items():
        nc = G.add_class(g, rng, Inv(), lex(), 10.0, group=grp, level=G.AFFIX)
        g.by_id(nc.gram_id).form = tuple(from_ipa(f))
    assert len(g.class_system.classes) == 5
    root = tuple(from_ipa("ganda"))
    s = G.people_set(root, g, Inv())
    got = {k: v["ipa"] for k, v in s.items()}
    want = {"person": "muganda", "people": "baganda", "land": "buganda", "language": "luganda"}
    assert got == {k: word_ipa(from_ipa(v)) for k, v in want.items()}
    assert len(set(got.values())) == 4 and all(word_ipa(root) in v for v in got.values())


def test_people_set_without_classes_is_distinct():
    rng, g = _grammar(10, gender="none", numeral_classifiers="no")
    g.class_system = None
    g.grams = [G.Gram("PL", tuple(from_ipa("ri")), "N", "post", G.AFFIX, ("MANY", "X02"), 5.0, id="PL#1")]
    s = G.people_set(tuple(from_ipa("tolo")), g, Inv(), lex())
    ipas = [v["ipa"] for v in s.values()]
    assert len(set(ipas)) == 4 and all("tolo" in x for x in ipas)
    assert s["people"]["ipa"] == "tolori"


def test_compound_order_follows_head_direction():
    head, mod = tuple(from_ipa("numba")), tuple(from_ipa("kawa"))
    _, gi = _grammar(11, word_order="SVO", adposition="pre")
    _, gf = _grammar(11, word_order="SOV", adposition="post")
    assert word_ipa(G.compound(head, mod, gi)) == "numbakawa"     # head-initial: head first
    assert word_ipa(G.compound(head, mod, gf)) == "kawanumba"     # head-final: head last


def test_place_name_locative_by_level():
    _, g = _grammar(12)
    g.grams = [G.Gram("LOC", tuple(from_ipa("ni")), "NP", "post", G.FREE, ("IN", "X04"), 5.0, id="LOC#1")]
    base = tuple(from_ipa("mosa"))
    free = G.place_name(base, g)
    assert free["ipa"] == "mosa ni" and len(free["words"]) == 2
    g.grams[0].level = G.AFFIX
    bound = G.place_name(base, g)
    assert bound["ipa"] == "mosani" and len(bound["words"]) == 1
    assert G.place_name(base, g, loc=False)["ipa"] == "mosa"


# --- output -----------------------------------------------------------------------------------------------------------

def test_json_roundtrip_table_and_describe():
    rng, g = _grammar(13)
    lx = lex()
    for k in range(60):
        G.step(rng, g, 10, Inv(), lx, kyr=20 - k * 0.25)
    G.apply_rule_to_grammar(g, _drop_final_vowel, "fvl", 5.0)
    d = json.loads(json.dumps(G.to_json(g)))
    g2 = G.from_json(d)
    assert G.complexity(g2) == G.complexity(g)
    assert G.paradigm_table(g2) == G.paradigm_table(g)
    t = G.paradigm_table(g)
    assert t["nouns"]["columns"][0] == "lemma" and len(t["verbs"]["rows"]) == 4
    lines = G.describe(g)
    assert lines and lines[0].startswith("Basic order") and lines[-1].startswith("Measured")
    c2 = G.copy(g)
    G.apply_rule_to_grammar(c2, lambda f: tuple(f[1:]) if len(f) > 2 else tuple(f), "x", 1.0)
    assert G.paradigm_table(g) == t       # the copy evolves apart


def test_deterministic_per_seed():
    def run():
        rng, g = _grammar(14)
        for k in range(30):
            G.step(rng, g, 10, Inv(), lex(), l2_share=0.1, kyr=20 - k * 0.5)
        return json.dumps(G.to_json(g), sort_keys=True)
    assert run() == run()


def test_lect_style_kwargs():
    rng, g = _grammar(15)
    G.step(rng, g, 20, l2=0.2, population=1000, isolation=0.3, kyr=3.0, lexicon=lex(), inventory=Inv(), lect="x")
    assert isinstance(G.apply_rule_to_grammar(g, lambda f: tuple(f), "id", 1.0), int)


@pytest.mark.parametrize("seed", range(5))
def test_class_system_grows_from_classifiers(seed):
    rng, g = _grammar(200 + seed, gender="classes")
    assert g.class_system is not None and len(g.class_system.classes) == 3
    assert all(g.by_id(c.gram_id).level == G.FREE for c in g.class_system.classes)


# --- review fixes: source kinds, recruitment paths, clipping, deletion, root-controlled harmony ------------------------

def test_allative_concept_is_not_the_allative_marker():
    """The concept ALL ('all') and the function ALL (allative) no longer collide in the description."""
    rng, g = _grammar(3, number="sg-pl")
    g.grams = [x for x in g.grams if x.function != "PL"]
    gr = G.recruit(rng, g, lex(ALL=("wote", "FUNC"), MANY=("", "A")), kyr=20.0, function="PL", source="ALL")
    assert gr is not None and gr.source[0] == "ALL" and gr.source[2] == "concept"
    assert G._origin(gr) == "once the word for 'all'"
    line = next(x for x in G.describe(g) if "plural" in x and "class marker" not in x)
    assert "allative" not in line and "'all'" in line
    # a reanalysed gram names its old function
    gr.source = ("PERF", "G0xx", "gram")
    assert G._origin(gr) == "once the perfect marker"
    back = G.from_json(json.loads(json.dumps(G.to_json(g))))
    assert any(tuple(x.source) == ("PERF", "G0xx", "gram") for x in back.grams)


def test_recruitment_paths_are_real():
    T = G.load_tables()
    for p in T.paths:
        if p.target == "PASS" and not p.from_gram:
            assert "TAKE" not in p.sources, p     # 'get' is not 'take'
        if p.target == "NEG":
            assert "NOT" not in p.sources, p      # no negator from the negator
        if p.id == "G003":
            assert p.target == "RECPST"
    rng, g = _grammar(4, past="marked")
    g.grams = []
    lx = lex(COME=("tola", "V"))
    assert G.recruit(rng, g, lx, kyr=20.0, function="RECPST") is None   # no past tense yet: no recent past
    g.grams.append(G.Gram("PAST", tuple(from_ipa("ka")), "V", "post", G.CLITIC, ("?", "proto", "unknown"), 20.0, id="P#1"))
    gr = G.recruit(rng, g, lx, kyr=20.0, function="RECPST")
    assert gr is not None and gr.source[0] == "COME"
    neg = G.recruit(rng, g, lx, kyr=20.0, function="NEG")             # no 'nothing/lack/refuse' word: coined
    assert neg is not None and neg.source[2] == "coin" and G._origin(neg) == "a newly coined word"
    neg2 = G.recruit(rng, g, lex(NOTHING=("hapana", "N")), kyr=20.0, function="NEG")
    assert neg2 is None or neg2.source[0] == "NOTHING"


def test_recruited_gram_clipped_to_two_syllables():
    rng, g = _grammar(5, word_order="SOV", future="marked")
    g.grams = [x for x in g.grams if x.function != "FUT"]
    gr = G.recruit(rng, g, lex(GO=("kelemanito", "V")), kyr=20.0, function="FUT", source="GO")
    assert gr is not None and tuple(gr.form) == tuple(from_ipa("kele"))
    assert any("clipped" in h for _, h in gr.history)


def test_rule_deleting_everything_keeps_minimal_stems_and_loses_grams():
    rng, g = _pl_grammar()
    G.apply_rule_to_grammar(g, lambda f: (), "wipe", 5.0)
    for e in g.exemplars:
        assert len(e.stem) == 1 and all(len(c) >= 1 for c in e.cells.values())
    assert all(len(f) >= 1 for _, f in g.helpers.values())
    pl = next(x for x in g.grams if x.function == "PL")
    assert not pl.live and any("eroded to nothing" in t for _, t in g.events)
    assert any("kept minimal" in t for _, t in g.events)


def test_stem_index_passed_when_rule_accepts_it():
    rng, g = _pl_grammar()
    seen = []

    def rule(form, stem_index=0):
        seen.append((len(form), stem_index))
        return form

    G.apply_rule_to_grammar(g, rule, "harmony", 5.0)
    nouns = [e for e in g.exemplars if e.pos == "N" and ("PL",) in e.cells]
    assert nouns and seen
    pre = g.gram("PL").side == "pre"
    for e in nouns:
        want = len(g.gram("PL").form) if pre else 0
        assert (len(e.cells[("PL",)]), want) in seen
    G.apply_rule_to_grammar(g, lambda f: f, "plain", 5.0)   # one-argument callables still work


# --- review of run a24559: thin grammar, a zero plural that came back -------------------------------------------------

def _append_a(form):
    """Epenthesis after a final consonant (what S123-style rules do)."""
    f = tuple(form)
    return f + tuple(from_ipa("a")) if f and f[-1].kind == "C" else f


def test_zero_affix_stays_zero_and_renewal_is_a_new_gram():
    rng, g = _pl_grammar()
    nouns = [e for e in g.exemplars if e.pos == "N"]
    # PL -ti worn to nothing, but kept as stem marking (cells differ from the stem)
    G.apply_rule_to_grammar(g, lambda f: tuple(f) if tuple(f) != tuple(from_ipa("ti")) else (), "kill", 5.0)
    pl = next(x for x in g.grams if x.function == "PL")
    pl.form = ()
    for e in nouns:
        e.set(("PL",), (("stem", tuple(e.stem) + tuple(from_ipa("k"))), ("PL", ())))   # an umlaut-like stem mark
    G._check_lost(g, 4.5)
    assert pl.live and pl.level == G.FUSED and pl.form == ()
    # an epenthetic vowel after the marked stem goes to the stem, not to the zero affix, and the gram stays empty
    G.apply_rule_to_grammar(g, _append_a, "epenthesis", 4.0)
    assert pl.form == () and all(e.morph(("PL",), "PL") == () for e in nouns)
    # renewal: a new periphrasis is a new Gram with its own id and birth date; binding retires the zero
    monkey = G.ABANDON
    try:
        G.ABANDON = 0.0
        new = G.recruit(rng, g, lex(), kyr=3.0, function="PL")
    finally:
        G.ABANDON = monkey
    assert new is not None and new is not pl and new.id != pl.id and new.born_kyr == 3.0 and new.level == G.FREE
    assert pl.born_kyr == 10.0


def test_grammar_holds_several_live_grams():
    """RECRUIT / ABANDON: with no sound change and moderate L2 (0.3), lects hold a median 5+ live grams after 700
    generations, and most new periphrases bind before they fall out of use."""
    live, bound, abandoned = [], 0, 0
    for s in range(10):
        rng, g = _grammar(300 + s)
        lx = lex()
        for k in range(70):
            G.step(rng, g, 10, Inv(), lx, l2_share=0.3, population=50000, isolation=0.3, kyr=20 - k * 0.28)
        live.append(len(g.live()))
        for gr in g.grams:
            first = next((t for _, t in gr.history if t.startswith(("now ", "lost"))), "")
            bound += first.startswith("now ")
            abandoned += first.startswith("lost: the periphrasis")
    assert np.median(live) >= 5, live
    assert abandoned < 0.3 * (bound + abandoned), (bound, abandoned)


# --- typology drift in the run (the 2026-11-04 round) -------------------------------------------------------------------

def test_step_drifts_typology_at_the_lect_rate():
    """grammar.step drifts the typology's aims when asked (lect.grammar_step asks), per generation times the lect's rate:
    over ~720 generations (20 kyr of human history) a good share of features change, at rate 0 none drift (an aim can
    still move when an unwanted gram binds: that is adoption, not drift)."""
    changed, frozen = [], []
    drift_ev = lambda g: [e for e in g.events if e[1].startswith("typology ") and "marker bound" not in e[1]]  # noqa: E731
    for s in range(6):
        rng, g = _grammar(s)
        t0 = dict(G.aims(g))
        G.step(rng, g, 720, drift_typology=True, rate=1.0)
        changed.append(sum(G.aims(g)[f] != t0[f] for f, _ in G.FEATURES))
        rng, g = _grammar(s)
        G.step(rng, g, 720, drift_typology=True, rate=0.0)
        frozen.append(len(drift_ev(g)))
    assert np.mean(changed) >= 6 and not any(frozen), (changed, frozen)


def test_lect_grammar_step_turns_drift_on():
    from planet.language import lect as LC
    seen = {}

    class Fake:
        def step(self, rng, g, n, **kw):
            seen.update(kw)
    lect = type("L", (), {"grammar": None, "inventory": None, "lexicon": None, "rate": 1.3})()
    LC.grammar_step(Fake(), None, lect, 10.0, {"l2": 0.1, "population": 100.0, "isolation": 0.5, "kyr": 3.0})
    assert seen["drift_typology"] is True and seen["rate"] == 1.3


def test_drift_retention_by_class_and_harmony():
    """20 kyr at human generations (722) and the median L2 share 0.54: very stable features kept by ~85%+, stable ~70-90%,
    fickle ~40-70%; 145-yr generations keep more; OV keeps postpositions and VO prepositions after flips."""
    T = G.load_tables()

    def run(gen_yr, n=400, seed=1):   # (n 200 -> 400, PW-1600: at 200 the OV share sat at the 0.85 bar by draw order)
        rng = np.random.default_rng(seed)
        ret = {c: [] for c in G.STABILITY}
        harm = []
        for _ in range(n):
            t = G.draw_typology(rng, T)
            t0 = dict(t)
            for _ in range(40):
                G.drift(rng, t, 500.0 / gen_yr, 0.54, T)
            for f, c in G.FEATURES:
                ret[c].append(t[f] == t0[f])
            harm.append((t.ov(), t["adposition"]))
        return {c: float(np.mean(v)) for c, v in ret.items()}, harm

    human, harm = run(27.7)
    assert 0.75 <= human["very_stable"] <= 0.95, human
    assert 0.65 <= human["stable"] <= 0.90, human
    assert 0.40 <= human["fickle"] <= 0.70, human
    assert human["very_stable"] > human["medium"] > human["fickle"], human
    long, _ = run(145.0)
    assert all(long[c] > human[c] for c in G.STABILITY), (long, human)
    ov = [a for o, a in harm if o == "OV"]
    vo = [a for o, a in harm if o == "VO"]
    assert np.mean([a == "post" for a in ov]) > 0.85 and np.mean([a == "pre" for a in vo]) > 0.8


def test_disharmonic_value_flips_faster():
    T = G.load_tables()
    t = G.draw_typology(np.random.default_rng(0), T)
    t["word_order"], t["adposition"] = "SOV", "post"
    G._derive(t)
    assert G._disharmony("adposition", t, T) < 1.5
    t["adposition"] = "pre"
    assert G._disharmony("adposition", t, T) > 5.0
    assert G._disharmony("case", t, T) == 1.0


# --- typology and grams, one system (the 2026-11-04 round) --------------------------------------------------------------

def test_steps_never_leave_a_typology_clash():
    """Twelve lects drifting fast over 2000 generations in 40 steps: after every step the shown typology agrees with the
    live grams (no 'number: none' beside a plural, no 'case: none' beside a locative, the negator on its side)."""
    seen = 0
    for s in range(12):
        rng, g = _grammar(100 + s)
        for _ in range(40):
            G.step(rng, g, 50, inv=Inv(), lexicon=lex(), l2_share=0.3, drift_typology=True, rate=2.0)
            assert G.clashes(g, lex()) == [], (s, G.clashes(g, lex()))
        seen += len(g.live())
    assert seen > 30


def test_short_history_has_no_typology_clashes():
    """The whole driver (shifts with calques, budding, sound change over the grams) on the tiny run: every living lect's
    typology agrees with its grams, and the language pass's check says so."""
    from test_language_history import TinyRun
    from planet.language import checks as CK, history as H
    old = (H.RATE_SCALE, H.WORKERS)
    H.RATE_SCALE, H.WORKERS = 240.0, 1
    try:
        res = H.generate(None, run=TinyRun(), analyse=False)
    finally:
        H.RATE_SCALE, H.WORKERS = old
    living = [l for l in res["lects"] if l.alive and l.grammar is not None]
    assert len(living) >= 4
    for l in living:
        assert G.clashes(l.grammar, l.lexicon) == [], (l.id, G.clashes(l.grammar, l.lexicon))
    row = CK.typology_consistency(res)
    assert row["pass"] and row["value"]["lects_with_clashes"] == 0, row


def test_typology_reads_the_grams():
    rng, g = _pl_grammar()
    G.realise(g)
    assert g.typology["number"] == "sg-pl"
    g.grams[0].level = G.LOST
    G.realise(g)
    assert g.typology["number"] == "none" and G.aims(g)["number"] == "sg-pl"   # the aim stays: the ladder will renew it
    g.grams.append(G.Gram("LOC", tuple(from_ipa("ka")), "NP", "post", G.FREE, ("AT", "X"), 5.0, id="LOC#y"))
    G.aims(g)["adposition"] = "pre"
    G.realise(g)
    assert g.typology["case"] == "none" and g.typology["adposition"] == "post"   # a free postposition is an adposition, not case
    g.grams[-1].level = G.CLITIC
    G.realise(g)
    assert g.typology["case"] == "few"   # case from clitic level on (WALS 49)
    g.grams[-1].level = G.FREE
    G.realise(g)
    G._follow_syntax(g, 5.0)
    G.realise(g)
    assert g.grams[-1].side == "pre" and g.typology["adposition"] == "pre"   # the free word moved with the syntax
    assert G.clashes(g) == []


def test_flip_toward_marking_recruits_and_flip_to_none_erodes():
    """'number: none > sg-pl' pulls a plural onto the ladder within a few hundred generations; 'past: marked > none' lets
    a bound past erode."""
    got = lost = 0
    for s in range(10):
        rng, g = _grammar(200 + s, number="none", past="marked")
        g.grams = [G.Gram("PAST", tuple(from_ipa("na")), "V", "post", G.AFFIX, ("X", "X"), 10.0, id="PAST#x")]
        G._sync_cells(g)
        G.aims(g)["number"], G.aims(g)["past"] = "sg-pl", "none"
        G.step(rng, g, 400, inv=Inv(), lexicon=lex(), l2_share=0.3)
        got += g.typology["number"] != "none"
        lost += g.typology["past"] == "none"
        assert G.clashes(g, lex()) == []
    assert got >= 6 and lost >= 6, (got, lost)


def test_unwanted_gram_that_binds_becomes_the_aim():
    rng, g = _grammar(7, definite_article="none")
    gr = G.Gram("DEF", tuple(from_ipa("nako")), "NP", "post", G.CLITIC, ("THAT", "X"), 10.0, id="DEF#x")
    g.grams = [gr]
    G.aims(g)["definite_article"] = "none"
    old = (G.FUSE, G.ABANDON, G.DEGRAM)
    G.FUSE, G.ABANDON, G.DEGRAM = 5.0, 0.0, 0.0
    try:
        G.step(rng, g, 10, inv=Inv(), lexicon=lex())
    finally:
        G.FUSE, G.ABANDON, G.DEGRAM = old
    assert gr.level >= G.AFFIX and G.aims(g)["definite_article"] == "post" == g.typology["definite_article"]
    assert any("marker bound" in e[1] for e in g.events)


def test_outside_write_becomes_an_aim_and_clusivity_follows_the_lexicon():
    rng, g = _grammar(8)
    g.typology["number"] = "sg-du-pl"     # a calque on shift writes the shown typology
    g.typology["word_order"] = "VSO"
    G.realise(g, lex())
    assert G.aims(g)["number"] == "sg-du-pl" and G.aims(g)["word_order"] == "VSO" == g.typology["word_order"]
    assert G.clashes(g, lex()) == []
    assert g.typology["clusivity"] == "no"
    both = lex(**{"WE (INCLUSIVE)": ("tiso", "FUNC"), "WE (EXCLUSIVE)": ("kami", "FUNC")})
    G.realise(g, both)
    assert g.typology["clusivity"] == "yes"


def test_json_keeps_the_aims():
    rng, g = _grammar(9)
    G.step(rng, g, 300, inv=Inv(), lexicon=lex(), drift_typology=True, rate=3.0)
    h = G.from_json(json.loads(json.dumps(G.to_json(g))))
    assert dict(G.aims(h)) == dict(G.aims(g)) and dict(h.typology) == dict(g.typology)
    c = G.copy(g)
    assert dict(G.aims(c)) == dict(G.aims(g)) and G.aims(c) is not G.aims(g)


# --- grammar phase A (2026-11-07) --------------------------------------------------------------------------------------

def _gram(fn, form="ka", level=G.CLITIC, side="post", host=None, src=("X", "X")):
    return G.Gram(fn, tuple(from_ipa(form)), host or G.func_info(fn).host, side, level, src, 10.0, id=f"{fn}#t")


def test_pull_is_per_function_not_per_first_feature():
    """A live locative no longer blocks the pull toward an accusative or ergative; a plural no longer blocks the dual;
    a reportative no longer blocks the witnessed evidential; a few-case system with no oblique case pulls one."""
    rng, g = _grammar(11, case="many", alignment="split", number="sg-du-pl", evidentiality="direct+indirect")
    g.grams = [_gram("LOC"), _gram("PL"), _gram("EVID.REP", host="VP")]
    for k, v in (("case", "many"), ("alignment", "split"), ("number", "sg-du-pl"), ("evidentiality", "direct+indirect")):
        G.aims(g)[k] = v
    u = G._unrealised(g, G.aims(g))
    assert u["alignment:ACC"] == {"ACC"} and u["alignment:ERG"] == {"ERG"}
    assert u["number:DU"] == {"DU"} and u["evidentiality:DIR"] == {"EVID.DIR"}
    assert u["case:rich"] == {"INS", "COM"} and u["case:ALL"] == {"ALL"} and u["case:ABL"] == {"ABL"}   # (PW-1569)
    assert u["case:local"] == set(G.LOCAL_CASE) and u["case:periph"] == {"PERL", "PRIV", "TRANSL"}
    assert "case" not in u and "number" not in u   # (the locative and the plural answer those)
    g.grams += [_gram("ACC"), _gram("DU"), _gram("INS")]
    u = G._unrealised(g, G.aims(g))
    assert "alignment:ACC" not in u and "number:DU" not in u and "case:rich" not in u and "alignment:ERG" in u


def test_ergative_sources_ablative_locative_genitive_and_agentive_by():
    T = G.load_tables()
    erg = {p.id: p.sources for p in T.paths if p.target == "ERG"}
    assert erg["X17"] == ("INS",) and erg["X19"] == ("ABL",) and erg["X20"] == ("LOC",) and erg["X21"] == ("GEN",)
    assert "NEAR" in erg["X22"]
    for fn, src in (("ABL", "LEAVE"), ("ALL", "GO"), ("INS", "TAKE")):
        assert any(p.target == fn and src in p.sources and not p.from_gram for p in T.paths), fn
    # an ablative reanalysed as the ergative
    rng, g = _grammar(12, case="few", alignment="erg-abs")
    g.grams = [_gram("ABL", "tu")]
    gr = G.recruit(rng, g, lex(), 5.0, function="ERG", source="ABL")
    assert gr is not None and gr.function == "ERG" and gr.source[0] == "ABL" and g.typology["alignment"] == "erg-abs"
    # an agentive 'by' word recruited as the ergative
    rng, g = _grammar(13, case="few", alignment="erg-abs")
    g.grams = []
    gr = G.recruit(rng, g, lex(NEAR=("pepe", "FUNC")), 5.0, function="ERG", source="NEAR")
    assert gr is not None and gr.source[0] == "NEAR"


def test_split_ergativity_is_chosen_and_dropped():
    rng, g = _grammar(14, case="few", alignment="split")
    g.grams = [_gram("ACC"), _gram("ERG", "lu")]
    G._processes(g, rng, 5.0, 1.0, {})
    assert g.processes["split"] == "person"   # no perfective or past to hang an aspect split on
    seen = set()
    for s in range(40):
        r = np.random.default_rng(s)
        h = G.copy(g)
        h.processes = {}
        h.grams.append(_gram("PERF", "se", level=G.AFFIX))
        G._processes(h, r, 5.0, 1.0, {})
        seen.add(h.processes["split"])
    assert seen == {"person", "aspect"}
    g.grams[1].level = G.LOST
    G._processes(g, rng, 4.0, 1.0, {})
    assert "split" not in g.processes and any("split of the alignment ends" in e[1] for e in g.events)
    h = G.from_json(json.loads(json.dumps(G.to_json(h))))
    assert h.processes["split"] in ("person", "aspect")


def _real_proto(seed, **typ_over):
    """A proto grammar on a real lexicon (lexicon.proto_lexicon over a human inventory)."""
    from planet.language import lect as LC
    from planet.language import lexicon as LX
    from planet.language import speak as SP
    rng = np.random.default_rng(seed)
    inv = LC.draw_inventory(rng, SP.profile_for_people("human"))
    lx = LX.proto_lexicon(rng, inv, LX.concepts(None), 20.0, f"p{seed}")
    typ = G.draw_typology(rng)
    typ.update(typ_over)
    G._derive(typ)
    return rng, inv, lx, G.proto_grammar(rng, inv, lx, typ)


def test_clusivity_makes_an_inclusive_we_and_loses_it():
    kinds = set()
    for s in range(12):   # (a window wide enough for both kinds under any inventory draw)
        rng, inv, lx, g = _real_proto(30 + s, clusivity="yes")
        inc = lx.get("WE (INCLUSIVE)")
        assert inc is not None and inc.form != lx["WE"].form
        assert g.typology["clusivity"] == "yes" and G.clashes(g, lx) == []
        kinds.add("compound" if any(st.process.startswith("compound") for st in inc.etym) else "root")
    assert kinds == {"compound", "root"}
    G.aims(g)["clusivity"] = "no"
    old = G.CLUSIVE_LOSS
    G.CLUSIVE_LOSS = 1.0
    try:
        G.step(rng, g, 20, inv=inv, lexicon=lx, kyr=3.0)
    finally:
        G.CLUSIVE_LOSS = old
    assert "WE (INCLUSIVE)" not in lx and g.typology["clusivity"] == "no" and "WE" in lx
    assert any("no more inclusive/exclusive" in e[1] for e in g.events)
    rng, inv, lx, g = _real_proto(40, clusivity="no")
    assert "WE (INCLUSIVE)" not in lx and g.typology["clusivity"] == "no"


def test_reduplicant_shapes():
    st = tuple(from_ipa("bona"))
    assert word_ipa(G.reduplicant(st, "full")) == "bona"
    assert word_ipa(G.reduplicant(st, "CV", "pre")) == "bo"
    assert word_ipa(G.reduplicant(st, "CV", "post")) == "na"
    assert word_ipa(G.reduplicant(tuple(from_ipa("kain")), "CV", "pre")) == "ka"


def test_verb_reduplication_is_a_built_process_in_the_verb_cells():
    rng, g = _grammar(15, verb_reduplication="yes")
    rd = g.processes["redup"]
    assert rd["fn"] in G.REDUP and g.typology["verb_reduplication"] == "yes"
    v = next(e for e in g.exemplars if e.pos == "V")
    cell = v.parts[(rd["fn"],)]
    red = G.reduplicant(v.stem, rd["shape"], rd["side"])
    assert dict(cell)[rd["fn"]] == red and dict(cell)["stem"] == v.stem
    assert rd["fn"] in G.paradigm_table(g)["verbs"]["columns"]
    G.aims(g)["verb_reduplication"] = "no"
    old = G.REDUP_LOSS
    G.REDUP_LOSS = 1.0
    try:
        G.step(rng, g, 20, inv=Inv(), lexicon=lex())
    finally:
        G.REDUP_LOSS = old
    assert "redup" not in g.processes and g.typology["verb_reduplication"] == "no"
    assert all((rd["fn"],) not in e.cells for e in g.exemplars) and G.clashes(g, lex()) == []
    rng, g = _grammar(16, verb_reduplication="no")
    assert "redup" not in g.processes and g.typology["verb_reduplication"] == "no"


def test_counting_base_builds_the_higher_numerals():
    """The grammar's counting base picks the lexicon's numeral system (lexsys), and the composites follow it: a
    multiplier where the grammar puts a numeral beside its noun ('two ten' NumN, 'ten two' NNum)."""
    from planet.language import lexsys as LS

    def made(lx, c):
        # (the step that makes the concept itself: a built TWENTY can sit inside HUNDRED's etymology)
        return next((st for st in reversed(lx[c].etym) if st.process.startswith("compound:")), None)
    rng, inv, lx, g = _real_proto(50, numeral_base="decimal", numeral="NumN")
    st = made(lx, "TWENTY")
    assert lx.systems["numeral"]["system"] == "decimal" and st is not None and st.note.startswith("two ten")
    assert made(lx, "HUNDRED") is None and any("counting base decimal" in e[1] for e in g.events)
    rng, inv, lx, g = _real_proto(51, numeral_base="vigesimal", numeral="NNum")
    assert lx.systems["numeral"]["system"] in ("vigesimal", "hybrid")
    assert made(lx, "FORTY").process == "compound:TWENTY+TWO" and made(lx, "FORTY").note.startswith("twenty two")
    if lx.systems["numeral"]["system"] == "vigesimal":
        assert made(lx, "HUNDRED").note.startswith("twenty five")
    rng, inv, lx, g = _real_proto(52, numeral_base="other")
    assert lx.systems["numeral"]["system"] in ("quinary", "restricted")
    assert all(made(lx, c) is not None for c in ("SIX", "SEVEN", "EIGHT", "NINE"))
    assert made(lx, "SIX").process == "compound:FIVE+ONE"


def test_decimal_lects_do_not_renew_digits_as_five_plus():
    """An ordinary compound recipe (data/compounds.tsv) builds SIX as 'five one' or TEN as 'two hands' only where the
    counting system builds on five (grammar A's leftover); subtractive NINE 'one from ten' fits any system."""
    from planet.language import lexicon as LX
    from planet.language import lexsys as LS
    rng, inv, lx, g = _real_proto(53, numeral_base="decimal")
    lx.systems["numeral"]["quinary"] = False
    parts = {LX._compound_parts(np.random.default_rng(s), lx, LX.concept_info(k), None, None)[0]
             for s in range(30) for k in ("SIX", "SEVEN", "EIGHT", "NINE", "TEN")}
    assert "FIVE" not in parts and "HAND" not in parts
    assert not LS.recipe_fits(lx, "SIX", "FIVE", "ONE") and LS.recipe_fits(lx, "NINE", "TEN", "ONE")
    lx.systems["numeral"]["quinary"] = True
    assert LS.recipe_fits(lx, "SIX", "FIVE", "ONE") and LS.recipe_fits(lx, "TEAR", "EYE", "WATER")


def test_person_markers_bind_as_a_set():
    """One subject pronoun binding pulls most of its series with it; later gaps fill by analogy."""
    sizes = []
    for s in range(12):
        rng, g = _grammar(60 + s, verb_agreement="suffix")
        g.grams = [_gram("3SG", "jesu", level=G.FREE, src=("HE OR SHE OR IT", "X08"))]
        g.grams[0].age_gens = 400
        old = G.FUSE
        G.FUSE = 0.2
        try:
            G.step(rng, g, 30, inv=Inv(), lexicon=lex(), l2_share=0.0)
        finally:
            G.FUSE = old
        sizes.append(len({x.function for x in g.grams if x.live and x.function in G.PERSON_FNS and x.level >= G.CLITIC}))
    assert sum(1 for k in sizes if k == 1) <= 2 and np.median(sizes) >= 4, sizes
    rng, g = _grammar(80, verb_agreement="suffix")
    g.grams = [_gram("1SG", "ani", level=G.AFFIX, src=("I", "X06"))]
    G._person_fill(g, rng, lex(), 3.0, G.load_tables(), 1.0)
    new = [x for x in g.grams if x.function != "1SG"]
    assert len(new) == 1 and new[0].level == G.AFFIX and new[0].side == "post"
    assert any("by analogy with the paradigm" in e[1] for e in g.events)


def test_degrammaticalization_is_rare_and_prefers_orphaned_edge_markers():
    rng, g = _grammar(81, case="few")
    gen = _gram("GEN", "sa", level=G.AFFIX, host="NP")
    gen.age_gens = 400
    g.grams = [gen, _gram("DAT", "ku", level=G.LOST, host="NP")]
    neg = _gram("NEG", "si", level=G.AFFIX, host="VP")
    assert G._degram_bias(g, gen) == G.DEGRAM_EDGE * G.DEGRAM_ORPHAN and G._degram_bias(g, neg) == 1.0
    old = (G.DEGRAM, G.FUSE_LEVEL, G.L2_STRIP)
    G.DEGRAM, G.FUSE_LEVEL, G.L2_STRIP = 50.0, (1.0, 0.7, 0.0), 0.0   # (at the fusion hazard itself; no further fusion)
    try:
        for _ in range(40):
            G.step(rng, g, 10, inv=Inv(), lexicon=lex())
            if gen.level < G.AFFIX:
                break
    finally:
        G.DEGRAM, G.FUSE_LEVEL, G.L2_STRIP = old
    assert gen.level == G.CLITIC and any("degrammaticalization" in e[1] for e in g.events)
    assert any("degrammaticalized: affix > clitic" in h[1] for h in gen.history)


# --- grammar phase B (2026-11-08) -------------------------------------------------------------------------------------

def test_phase_b_paths_mood_genitive_object_possessor():
    T = G.load_tables()
    by = {}
    for p in T.paths:
        by.setdefault(p.target, []).append(p)
    assert {"OBLG", "HORT", "APPR", "IMP"} <= set(by)
    assert any(p.id == "G007" for p in by["OBLG"]) and any(p.id == "G034" for p in by["HORT"])
    assert any(p.from_gram and p.sources == ("ABL",) for p in by["GEN"])
    assert any(not p.from_gram and "THAT" in p.sources for p in by["GEN"])
    lead = [p for f in G.OBJ_FNS + G.POSS_FNS for p in by.get(f, []) if p.weight > 0]
    assert sorted(p.target for p in lead) == ["1SG.POSS", "3SG.O"]   # (one lead path per series, the rest bind with it)
    assert all(p.weight == 0 for p in by["1PL.INCL"])


def test_object_and_possessor_series_bind_as_sets_and_show_in_the_typology():
    sizes = []
    for s in range(8):
        rng, g = _grammar(90 + s, object_agreement="suffix", verb_agreement="suffix")
        G.aims(g)["object_agreement"] = "suffix"
        g.grams = [_gram("3SG.O", "jesu", level=G.FREE, side="post", src=("HE OR SHE OR IT", "X33"))]
        g.grams[0].age_gens = 400
        old = G.FUSE
        G.FUSE = 0.3
        try:
            G.step(rng, g, 30, inv=Inv(), lexicon=lex(), l2_share=0.0)
        finally:
            G.FUSE = old
        obj = {x.function for x in g.grams if x.live and x.function in G.OBJ_FNS and x.level >= G.CLITIC}
        sizes.append(len(obj))
        assert all(x.host == "V" for x in g.grams if x.function in G.OBJ_FNS)
        if obj:
            assert g.typology["object_agreement"] == "suffix"
    assert np.median(sizes) >= 3, sizes   # (the lexicon has no 'you all': at most 5 of 6)
    rng, g = _grammar(92, genitive="NG")
    g.grams = [_gram("1SG.POSS", "ani", level=G.CLITIC, side="post", src=("I", "X39"))]
    G._person_set(g, g.grams[0], np.random.default_rng(0), lex(), 3.0, G.load_tables())
    poss = [x for x in g.grams if x.function in G.POSS_FNS]
    assert len(poss) >= 3 and all(x.host == "N" for x in poss)


def test_inclusive_subject_marker_joins_only_with_an_inclusive_we():
    rng, g = _grammar(93, verb_agreement="suffix")
    gr = _gram("1SG", "ani", level=G.CLITIC, src=("I", "X06"))
    g.grams = [gr]
    old = dict(G.PERSON_JOIN)
    G.PERSON_JOIN.update({k: 1.0 for k in G.PERSON_JOIN})
    try:
        G._person_set(g, gr, rng, lex(), 3.0, G.load_tables())
        assert G.INCL_FN not in {x.function for x in g.grams}
        g.grams = [gr]
        G._person_set(g, gr, rng, lex(**{"WE (INCLUSIVE)": ("tuso", "FUNC")}), 3.0, G.load_tables())
        incl = [x for x in g.grams if x.function == G.INCL_FN]
        assert len(incl) == 1 and incl[0].source[0] == "WE (INCLUSIVE)"
    finally:
        G.PERSON_JOIN.clear()
        G.PERSON_JOIN.update(old)
    assert G.feature_of(G.INCL_FN) == ("verb_agreement",)


# --- grammar phase C (2026-11-08) -------------------------------------------------------------------------------------

def test_question_and_copula_are_realised_from_grams():
    rng, g = _grammar(3, polar_question="final_particle", copula="yes")
    g.grams = [x for x in g.grams if x.function not in ("Q", "COP")]
    G.realise(g)
    assert g.typology["polar_question"] == "intonation" and g.typology["copula"] == "no"
    assert "Q" in G._unrealised(g, G.aims(g)).get("polar_question", set())
    g.grams.append(G.Gram("Q", tuple(from_ipa("li")), "VP", "post", G.FREE, ("IF", "X46", "concept"), 5.0, id="Q#1"))
    g.grams.append(G.Gram("COP", tuple(from_ipa("jesu")), "VP", "post", G.FREE, ("HE OR SHE OR IT", "X48", "concept"),
                          5.0, id="COP#1"))
    G.realise(g)
    assert g.typology["polar_question"] == "final_particle" and g.typology["copula"] == "yes"
    g.by_id("Q#1").level = G.AFFIX
    G.realise(g)
    assert g.typology["polar_question"] == "verb_morph"
    assert G.clashes(g) == []


def test_copy_path_keeps_the_source_gram():
    rng, g = _grammar(4)
    g.grams = [G.Gram("COP", tuple(from_ipa("jesu")), "VP", "post", G.CLITIC, ("HE OR SHE OR IT", "X48", "concept"), 5.0,
                      id="COP#1")]
    gr = G.recruit(rng, g, lex(), 4.0, function="FOC")
    assert gr is not None and gr.function == "FOC" and gr.source[1] == "G057"
    assert g.by_id("COP#1").function == "COP" and g.by_id("COP#1").live


def test_concord_grows_with_a_bound_class_marker_and_ends_without():
    rng, g = _grammar(5, gender="classes")
    for c in g.class_system.classes:
        g.by_id(c.gram_id).level = G.AFFIX
    for _ in range(200):
        G._concord(g, rng, 1.0, 0.5, 0.0)
    assert g.processes["concord"] == ["adj", "dem", "verb"]
    for c in g.class_system.classes:
        g.by_id(c.gram_id).level = G.FREE
    G._concord(g, rng, 1.0, 0.5, 0.0)
    assert "concord" not in g.processes


def test_inflection_class_split_is_lexical_and_survives_json():
    rng, g = _pl_grammar()
    assert G._iclass(g, rng, 1.0, 1.0, 0.0, lex(), Inv())
    pl = g.gram("PL")
    assert pl.alt and pl.alt != pl.form
    ic = g.processes["iclass"]["PL"]
    members = [c for c in ("WATER", "PERSON", "DOG", "TREE", "HOUSE", "NAME", "TONGUE", "ANIMAL") if G.iclass_member(ic, c)]
    assert members == [c for c in ("WATER", "PERSON", "DOG", "TREE", "HOUSE", "NAME", "TONGUE", "ANIMAL")
                       if G.iclass_member(dict(ic), c)]   # (deterministic, no str hash)
    G._sync_cells(g)
    for ex in g.exemplars:
        if ex.pos == "N" and ("PL",) in ex.parts:
            want = pl.alt if G.iclass_member(ic, ex.concept) else pl.form
            assert ex.morph(("PL",), "PL") == tuple(want)
    g2 = G.from_json(json.loads(json.dumps(G.to_json(g))))
    assert g2.gram("PL").alt == pl.alt and g2.processes["iclass"] == g.processes["iclass"]


def test_portmanteau_merges_two_endings_in_cells_and_dies_with_a_part():
    rng, g = _pl_grammar()
    g.grams.append(G.Gram("LOC", tuple(from_ipa("ka")), "NP", "post", G.AFFIX, ("IN", "X04"), 10.0, id="LOC#x"))
    G._sync_cells(g)
    assert G._cumulate(g, rng, 1.0, 1.0)
    G._sync_cells(g)
    pm = g.gram("PL+LOC")
    assert pm is not None and pm.level == G.FUSED
    ex = next(e for e in g.exemplars if e.pos == "N")
    assert [lab for lab, _ in ex.parts[("PL", "LOC")]] == ["stem", "PL+LOC"]
    G._lose(g, g.by_id("LOC#x"), 1.0, "test")
    G._check_lost(g, 1.0)
    assert not pm.live


def test_infix_goes_after_the_first_consonants():
    rng, g = _grammar(7)
    g.grams = [G.Gram("PAST", tuple(from_ipa("um")), "V", "pre", G.AFFIX, ("?", "proto", "unknown"), 5.0, id="PAST#1")]
    G._sync_cells(g)
    assert G._infix(g, rng, 1.0, 1.0)
    G._sync_cells(g)
    ex = next(e for e in g.exemplars if e.pos == "V" and e.concept == "GO")
    assert [lab for lab, _ in ex.parts[("PAST",)]] == ["stem", "PAST", "stem"]
    assert word_ipa(ex.cells[("PAST",)]) == "kumele"


def test_stem_change_recorded_when_the_ending_is_gone():
    rng, g = _pl_grammar()
    pl = g.gram("PL")
    pl.form, pl.level = (), G.FUSED
    for ex in g.exemplars:
        if ("PL",) in ex.cells:
            ex.set(("PL",), (("stem", tuple(from_ipa(word_ipa(ex.stem).replace("a", "e")))), ("PL", ())))
    G._check_lost(g, 1.0)
    assert pl.live and ["a", "e"] in g.processes["stem_change"]["PL"]


def test_rulings_species_leanings_deep_past_and_comparison_prior():
    """Owner rulings 11-08: the three species leanings read generation length and pitch range (PW-1538 C); long-lived
    protos start with a deep past of bound grams (PW-1544 b); the comparison aim follows WALS 121A (PW-1538 D)."""
    assert G.leanings(25.0, 1.0) == {}
    assert G.leanings(G.LONG_GEN_YR, 1.0) == G.LEAN_LONG_GEN
    assert G.leanings(144.9, 1.0) == G.LEAN_LONG_GEN and G.deep_past_gens(144.9) == G.DEEP_PAST_GENS  # elves (ruling 11-08)
    assert G.leanings(G.SHORT_GEN_YR - 1, 1.0) == G.LEAN_SHORT_GEN
    assert G.leanings(25.0, G.WIDE_PITCH) == G.LEAN_WIDE_PITCH
    assert G.deep_past_gens(G.LONG_GEN_YR) == G.DEEP_PAST_GENS and G.deep_past_gens(25.0) == 0.0
    bound0 = bound1 = 0
    for s in range(6):
        g0 = G.proto_grammar(np.random.default_rng(s), Inv(), lex())
        g1 = G.proto_grammar(np.random.default_rng(s), Inv(), lex(), deep_gens=G.DEEP_PAST_GENS)
        bound0 += sum(1 for x in g0.live() if x.level >= G.AFFIX and x.function not in G.CASE_FNS)   # (PW-1586: case at birth)
        bound1 += sum(1 for x in g1.live() if x.level >= G.AFFIX and x.function not in G.CASE_FNS)
        assert any("deep unrecorded past" in e[1] for e in g1.events)
    assert bound0 == 0 and bound1 >= 6
    rng = np.random.default_rng(3)
    T = G.load_tables()
    draws = [G._draw_feature(rng, "comparative", G.Typology(G.draw_typology(rng)), T) for _ in range(600)]
    share = {k: draws.count(k) / len(draws) for k in G.COMPARE_PRIOR}
    assert all(abs(share[k] - p) < 0.06 for k, p in G.COMPARE_PRIOR.items())


# --- lane 4 (PW-1569, PW-1571) ------------------------------------------------------------------------------------------

def test_local_case_series_and_wals_bins():
    """A bound inessive beside a bound allative and ablative on the same side makes the illative and elative (region
    marker inside, direction outside); the 'case' label reads 'many' from 6 cases (WALS 49A), with the bin beside it."""
    rng, g = _grammar(21, case="many")
    g.grams = [_gram("INE", "sa", G.AFFIX), _gram("ALL", "ne", G.AFFIX), _gram("ABL", "ta", G.AFFIX),
               _gram("GEN", "n", G.AFFIX)]
    assert G.case_count(g) == 5 and G.case_bin(g) == "5" and G.realised_value("case", g) == "few"
    assert G._local_series(g, rng, 10.0, 1.0)
    ill, ela = g.gram("ILL"), g.gram("ELA")
    assert word_ipa(ill.form) == "sane" and word_ipa(ela.form) == "sata" and ill.level == G.AFFIX and ill.side == "post"
    assert G.case_count(g) == 7 and G.case_bin(g) == "6-7" and G.realised_value("case", g) == "many"
    g.grams = [_gram("LOC", "ka", G.CLITIC)]
    assert G.case_bin(g) == "borderline" and G.realised_value("case", g) == "few"


def test_proclitics_bind_more_slowly(monkeypatch):
    """PRE_FUSE: a clitic before its host takes the clitic > affix step at a fraction of the rate of one after it."""
    hits = {"pre": 0, "post": 0}
    monkeypatch.setattr(G, "RECRUIT", 0.0)
    monkeypatch.setattr(G, "PRESSURE", 0.0)
    for seed in range(120):   # (40 -> 120 seeds, PW-1600: 4 vs 7 hits at 40 was within draw noise)
        for side in ("pre", "post"):
            rng, g = _grammar(seed, case="few")
            g.grams = [_gram("LOC", "ka", G.CLITIC, side=side)]
            G.step(rng, g, 20, lexicon=lex(), kyr=10.0)
            hits[side] += any(x.function == "LOC" and x.level >= G.AFFIX for x in g.grams)
    assert hits["pre"] < 0.5 * hits["post"], hits


def test_free_gram_wears_like_a_function_word():
    """PW-1537 R1: a free or clitic gram longer than GRAM_WEAR_FLOOR loses its last syllable (or a one-syllable gram its
    final consonant) by wear, never onto another gram's form and never to no vowel."""
    _rng, g = _grammar(10, gender="none", numeral_classifiers="no")
    a = G.Gram("DEF", tuple(from_ipa("untsu")), "N", "pre", G.FREE, ("THAT", "G001"), 5.0, id="DEF#1")
    b = G.Gram("COP", tuple(from_ipa("bin")), "V", "pre", G.CLITIC, ("THAT", "G002"), 5.0, id="COP#1")
    c = G.Gram("TOP", tuple(from_ipa("bi")), "N", "post", G.FREE, ("IF", "G003"), 5.0, id="TOP#1")
    g.grams = [a, b, c]
    assert G._wear_gram(g, a, None, 1.0) and word_ipa(a.form) == "un"
    assert not G._wear_gram(g, b, None, 1.0) and word_ipa(b.form) == "bin"   # (bi is TOP's form)
    assert not G._wear_gram(g, c, None, 1.0)   # (two segments: at the floor)


def test_cumulative_exponence_blurs_the_join():
    """PW-1537 R5: a portmanteau no longer splits into its two markers (kuː + h was called one when it was not)."""
    f = G._blur_join(tuple(from_ipa("kuː")), tuple(from_ipa("ha")))
    assert word_ipa(f) == "kha"   # (the first marker's last sound gone: the whole keeps a vowel)
    assert word_ipa(G._blur_join(tuple(from_ipa("kuː")), tuple(from_ipa("ham")))) == "kham"
    assert word_ipa(G._blur_join(tuple(from_ipa("u")), tuple(from_ipa("ni")))) == "ui"
    assert G._blur_join(tuple(from_ipa("u")), tuple(from_ipa("h"))) is None
