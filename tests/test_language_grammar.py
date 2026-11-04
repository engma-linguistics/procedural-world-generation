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
    for s in range(20):
        _, g = _grammar(s)
        plain = [x for x in g.grams if not x.function.startswith("CLASS")]
        assert 1 <= len(plain) <= 3
        assert all(x.level <= G.CLITIC for x in g.grams)
        assert G.complexity(g)["obligatory"] == 0
        assert len([e for e in g.exemplars if e.pos == "N"]) == 4 and len([e for e in g.exemplars if e.pos == "V"]) == 4


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
    line = next(x for x in G.describe(g) if "plural" in x)
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

    def run(gen_yr, n=200, seed=1):
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
    H.RATE_SCALE, H.WORKERS = 8.0, 1
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
    old = (G.FUSE, G.ABANDON)
    G.FUSE, G.ABANDON = 5.0, 0.0
    try:
        G.step(rng, g, 10, inv=Inv(), lexicon=lex())
    finally:
        G.FUSE, G.ABANDON = old
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
