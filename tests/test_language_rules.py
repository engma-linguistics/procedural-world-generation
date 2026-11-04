"""Sound change rules (planet/language/rules.py): notation, application, environments, functional load, catalogue."""

import random
import time

import numpy as np
import pytest

from planet.language import rules as R
from planet.language.percepts import from_ipa, word_ipa
from planet.language.profiles import HUMAN, HUMAN_ARTICULATORS, VoiceProfile


def w(s):
    return tuple(from_ipa(s))


def ipa(word):
    return word_ipa(word)


def demo(rid):
    return next(r for r in R.DEMO_RULES if r.id == rid)


def rule(text, **meta):
    r, why = R.parse_rule(text, **meta)
    assert r is not None, why
    return r


# (demo id, input, expected, a word the rule must leave alone, stress pattern)
DEMO_CASES = [
    ("lenition.p_f", "apa", "afa", "ata", None),
    ("lenition.f_h", "afa", "aha", "taf", None),
    ("lenition.h_loss", "aha", "aa", "ata", None),
    ("lenition.intervocalic_voicing", "ata", "ada", "anta", None),
    ("lenition.spirantization", "aba", "aβa", "ba", None),
    ("devoicing.final", "tad", "tat", "tada", None),
    ("deletion.final_vowel", "tama", "tam", "ta", "penult"),
    ("reduction.unstressed_schwa", "tamaka", "təmakə", "ta", "penult"),
    ("reduction.syncope", "takatapa", "taktapa", "tata", "initial"),
    ("assimilation.nasal_place", "anpa", "ampa", "ana", None),
    ("palatalization.k_front", "kika", "tʃika", "kaku", None),
    ("nasal.vowel_nasalization", "pan", "pãn", "pa", None),
    ("nasal.nasal_loss", "pãn", "pã", "pãna", None),
    ("debuccalization.s_h", "past", "paht", "sa", None),
    ("dental.theta_f", "θa", "fa", "ta", None),
    ("cluster.simplification", "astra", "asra", "asta", None),
    ("harmony.back", "kuteli", "kutolu", "ku", None),
    ("umlaut.i", "musi", "mysi", "musa", None),
    ("rhotic.rhotacism", "asa", "ara", "sa", None),
    ("tone.onset_voicing_split", "dapa", "ta˨pa˦", "ama", None),
    ("tone.glottal_coda_rising", "taʔ", "ta˨˦", "ʔa", None),
    ("tone.h_coda_falling", "tah", "ta˦˨", "ha", None),
    ("chain_shift.raise_mid", "seta", "sita", "tase", "penult"),
    ("metathesis.cc", "aska", "aksa", "asa", None),
    ("epenthesis.cluster", "takt", "takət", "tak", None),
    ("labial.w_v", "wa", "va", "ja", None),
    ("rhotic.l_vocalization", "kalt", "kawt", "kala", None),
    ("debuccalization.uvular", "qa", "ʔa", "ka", None),
    ("debuccalization.uvular_pharyngeal", "χa", "ħa", "xa", None),
]


def test_demo_set_is_complete_and_documented():
    assert len(R.DEMO_RULES) >= 25
    assert {c[0] for c in DEMO_CASES} == {r.id for r in R.DEMO_RULES}
    for r in R.DEMO_RULES:
        assert r.cause in R.CAUSES and r.scope in R.SCOPES and 1 <= r.weight <= 5 and r.example, r.id
        assert R.describe(r).endswith(")"), r.id


@pytest.mark.parametrize("rid,src,want,other,stress", DEMO_CASES, ids=[c[0] for c in DEMO_CASES])
def test_demo_rule_applies_and_leaves_others(rid, src, want, other, stress):
    r = demo(rid)
    assert R.apply(r, w(src), stress) == w(want), (rid, ipa(R.apply(r, w(src), stress)))
    assert R.apply(r, w(other), stress) == w(other)


def test_parse_notation_kinds():
    assert rule("p > f / V_V").change.kind == "set"
    assert rule("h > ∅").change.kind == "delete"
    assert rule("∅ > ʔ / #_V").change.kind == "insert"
    assert rule("e > ea / _r").change.kind == "split"
    assert rule("sk > ks").change.kind == "metathesis"
    assert rule("b, d, g > p, t, k").change.kind == "map"
    assert rule("N > [αplace] / _C[αplace]").change.kind == "assimilate"
    r = rule("k > ts > s / _[+front V]")
    assert "chain" in r.notation and R.apply(r, w("ke")) == w("tse")


def test_parse_failures_reported_not_raised():
    for bad in ["r...r > l...r", "tone > stress", "p > ", "V[−ATR] > [+ATR] / [+ATR] word", "q > ᴺ", "[+wibble] > p"]:
        r, why = R.parse_rule(bad)
        assert r is None and why, bad


def test_tsv_parses_mostly():
    rules, failures = R.load_tsv()
    assert len(rules) >= 140
    assert len(failures) <= 40
    assert all(r.cause in R.CAUSES for r in rules)


def test_word_edges():
    r = rule("s > h / #_")
    assert R.apply(r, w("sasas")) == w("hasas")
    r = rule("s > h / _#")
    assert R.apply(r, w("sasas")) == w("sasah")
    r = rule("∅ > e / #_sC")
    assert R.apply(r, w("sta")) == w("esta") and R.apply(r, w("asta")) == w("asta")


def test_optional_and_star_contexts():
    r = rule("u > y / _C(C)i")
    assert R.apply(r, w("musi")) == w("mysi")
    assert R.apply(r, w("mupsi")) == w("mypsi")
    assert R.apply(r, w("mupsti")) == w("mupsti")
    r = rule("u > y / _C*i")
    assert R.apply(r, w("mupsti")) == w("mypsti") and R.apply(r, w("ui")) == w("yi")


def test_alternatives_and_braces():
    r = rule("N > ∅ / Ṽ_{C, #}")
    assert R.apply(r, w("pãnta")) == w("pãta") and R.apply(r, w("pãn")) == w("pã") and R.apply(r, w("pãna")) == w("pãna")


def test_left_context_reads_the_output_so_far():
    # syncope alternates rather than deleting every unstressed vowel; harmony spreads through the word
    assert R.apply(demo("reduction.syncope"), w("takatapaka"), "initial") == w("taktapka")
    assert R.apply(demo("harmony.back"), w("kitolu")) == w("kiteli")


def test_gemination_and_compensatory_lengthening():
    assert R.apply(rule("C > CC / V_j"), w("atja")) == w("atːja")
    assert R.apply(rule("CC > C"), w("atːa")) == w("ata")
    assert R.apply(rule("pt > tt"), w("apta")) == w("atːa")
    assert R.apply(rule("x > ∅ / _C (with compensatory lengthening)"), w("nixt")) == w("niːt")


def test_stress_conditions_need_stress():
    r = demo("reduction.unstressed_schwa")
    assert R.apply(r, w("tamaka"), "none") == w("tamaka")
    assert R.apply(r, w("tamaka"), lambda word: 1) == w("taməkə")


def test_functional_load_counts_merged_forms():
    r = rule("p > b")
    lex = [w("pa"), w("ba"), w("pi"), w("ti")]
    assert R.functional_load(r, lex) == pytest.approx(0.5)  # pa ~ ba merge; pi > bi has no partner
    assert R.functional_load(rule("q > k"), lex) == 0.0


def test_pick_rule_vetoes_heavy_mergers_and_offers_a_push_chain():
    merge = rule("e > i", id="raise_e")
    lex = [w(x) for x in ("pe", "pi", "te", "ti", "ke", "ki")]
    inv = list(w("eiptk"))
    assert R.functional_load(merge, lex) == 1.0
    picks = [R.pick_rule(np.random.default_rng(s), [merge], lex, inv) for s in range(40)]
    assert all(p is None or p.cause == "dispersion" for p in picks)
    # i is at the top of the space: it has nowhere to go, so no push (centralizing it to ɨ in every lect made ɨ the commonest
    # vowel of the run); a central vowel in the way lowers
    assert R.dispersion_rule(merge, inv) is None
    merge2 = rule("ə > ɨ", id="raise_schwa")
    push = R.dispersion_rule(merge2, list(w("əɨptk")))
    assert push is not None and push.cause == "dispersion"


def test_pick_rule_deterministic():
    lex = [w(x) for x in ("pata", "kasi", "tumo", "sela", "bana", "kipu", "mafa", "nosi")]
    inv = {s for word in lex for s in word}
    rules = R.catalogue(HUMAN)

    def run(rng):
        return [getattr(R.pick_rule(rng, rules, lex, inv), "id", None) for _ in range(30)]

    assert run(np.random.default_rng(7)) == run(np.random.default_rng(7))
    assert run(random.Random(7)) == run(random.Random(7))
    assert any(x is not None for x in run(np.random.default_rng(7)))


def test_catalogue_filters_by_articulators_and_scales_by_cost():
    human = {r.id: r for r in R.catalogue(HUMAN)}
    assert "lenition.p_f" in human and "S001" in human
    lipless = VoiceProfile(id="lipless", source="spec", articulators=HUMAN_ARTICULATORS - {"lips"})
    cat = {r.id: r for r in R.catalogue(lipless)}
    assert "lenition.p_f" not in cat and "S001" not in cat and "rhotic.rhotacism" in cat
    atonal = VoiceProfile(id="atonal", source="spec", hear={"tone": 0.0})
    assert "tone.onset_voicing_split" not in {r.id for r in R.catalogue(atonal)}
    costly_labials = VoiceProfile(id="beaked", source="spec", make_cost={"labial": 10.0})
    beaked = {r.id: r for r in R.catalogue(costly_labials)}
    assert beaked["dental.theta_f"].weight < human["dental.theta_f"].weight  # produces a labial
    assert beaked["debuccalization.uvular"].weight == human["debuccalization.uvular"].weight
    assert beaked["S100"].weight > human["S100"].weight  # m > ∅ / _# removes one


def test_describe_plain_words():
    assert R.describe(rule("p > f / V_V", cause="effort", family="lenition")) == "p became f between vowels (effort: lenition)"
    assert "lost" in R.describe(demo("lenition.h_loss"))


def test_speed():
    rng = np.random.default_rng(1)
    segs = w("ptkbdgmnslraeiou")
    lex = [tuple(segs[i] for i in rng.integers(0, len(segs), 5)) for _ in range(400)]
    times = []
    for r in R.DEMO_RULES:
        t0 = time.perf_counter()
        for f in lex:
            R.apply(r, f)
        times.append(time.perf_counter() - t0)
    times.sort()
    assert times[len(times) // 2] < 0.005 and times[-1] < 0.030, times  # ~0.5 ms median on a quiet machine


def test_rules_pickle_for_spawned_workers():
    import pickle

    rules = list(R.DEMO_RULES) + R.load_tsv()[0]
    back = pickle.loads(pickle.dumps(rules))
    word = w("kastipenu")
    for a, b in zip(rules, back):
        assert R.apply(a, word) == R.apply(b, word), a.id


# ---------------------------------------------------------------------------------------------- review fixes (2026-11-03)

def tsv(rid):
    return next(r for r in R.load_tsv()[0] if r.id == rid)


def test_hear_axes_do_not_stand_in_for_articulators():
    from planet.language.profiles import load_profiles, resolve_profile

    from dataclasses import replace

    # a made-up voiceless-source profile: a bird keeps its larynx (a valve) and voices with the syrinx, so the real avian
    # profile qualifies for voicing rules; this one has neither
    avian = resolve_profile("avian", lambda lid: [], data=load_profiles())
    avian = replace(avian, articulators=frozenset(a for a in avian.articulators if a not in ("larynx", "syrinx")))
    assert "larynx" not in avian.articulators
    caps = R.profile_capabilities(avian)
    assert "larynx" not in caps and "hear:larynx" in caps and "hear:tone" in caps
    cat = R.catalogue(avian)
    assert cat and not any("larynx" in r.needs for r in cat)
    assert not any(r.cause == "tonogenesis" for r in cat)
    words = [w(x) for x in ("ata", "tad", "aza", "akda", "taʔ", "dapa", "tah")]
    for r in cat:
        for f in words:
            out = R.apply(r, f)
            if len(out) == len(f):  # voicing changes only with a manner change (a flap, an approximant)
                assert all(a.voice == b.voice or a.manner != b.manner for a, b in zip(out, f)), r.id
            assert all(s.tone == 0 for s in out), r.id
    # the legacy tokens land in the hear namespace
    assert tsv("S166").needs == {"larynx", "hear:tone"} and "hear:length" in tsv("S113").needs
    assert "tongue_tip" in tsv("S049").needs


def test_catalogue_has_no_twins():
    from collections import Counter

    cat = R.catalogue(HUMAN)
    counts = Counter(R.rule_key(r) for r in cat)
    assert max(counts.values()) == 1
    ids = {r.id for r in cat}
    for twin in ("S015", "S018", "S095", "S115", "S075", "S049", "S088", "S140", "S020", "S113", "S135", "S130",
                 "S069", "S151", "S166", "S167", "S168"):
        assert twin not in ids, twin
    assert ("S061" in ids) != ("S062" in ids)
    assert "lenition.p_f" in ids and "devoicing.final" in ids


def test_stressed_context_vowels():
    r = tsv("S047")  # C > CC / V́[-long]_V: raddoppiamento after the stressed vowel only
    assert r.env.ctx_stress
    assert R.apply(r, w("patama"), "penult") == w("patamːa")
    assert R.apply(r, w("patama"), "initial") == w("patːama")
    assert R.apply(r, w("patama"), "none") == w("patama")
    flap = tsv("S013")  # t, d > ɾ / V́_V: flapping after the stressed vowel, not everywhere
    assert R.apply(flap, w("atata"), "penult") == w("ataɾa")
    assert R.apply(flap, w("atata"), "final") == w("atata")
    verner = tsv("S173")  # [-voice fricative] > [+voice] / [-stress]V_
    assert R.apply(verner, w("afafa"), "penult") == w("avafa")
    assert "stressed" in R.describe(r) and "unstressed" in R.describe(verner)


def test_tonogenesis_pathways():
    onset = demo("tone.onset_voicing_split")  # voiced onset -> low, voiceless -> high, then devoicing
    out = R.apply(onset, w("bada"))
    assert out == w("pa˨ta˨")
    assert [s.tone for s in R.apply(onset, w("taka")) if s.kind == "V"] == [3, 3]
    assert R.apply(demo("tone.glottal_coda_rising"), w("taʔ"))[-1].tone == 4  # sắc/nặng
    assert R.apply(demo("tone.h_coda_falling"), w("tah"))[-1].tone == 5  # hỏi/ngã
    assert R.apply(demo("tone.glottal_coda_rising"), w("ʔata")) == w("ʔata")
    # the staged tsv rows parse and do the same
    assert R.apply(tsv("S166"), w("dapa")) == R.apply(onset, w("dapa"))
    assert R.apply(tsv("S167"), w("ʔataʔ")) == w("ʔata˨˦")  # the onset glottal stays
    assert R.apply(tsv("S168"), w("tah")) == w("ta˦˨")
    tones = [s.tone for s in R.apply(tsv("S169"), w("taʔpahkat")) if s.kind == "V"]
    assert tones == [4, 5, 1]
    assert len(tsv("S166").then) == 2 and "then" in R.describe(tsv("S166"))


def test_glottals_and_glottalic_stops_are_left_alone():
    voicing = demo("lenition.intervocalic_voicing")
    assert R.apply(voicing, w("aʔa")) == w("aʔa") and R.apply(voicing, w("aha")) == w("aha")
    assert R.apply(voicing, w("ata")) == w("ada")
    assert R.apply(tsv("S077"), w("aʔda")) == w("aʔda") and R.apply(tsv("S077"), w("akda")) == w("aɡda")
    for r in (demo("assimilation.nasal_place"), tsv("S075")):
        assert R.apply(r, w("anʔa")) == w("anʔa") and R.apply(r, w("anħa")) == w("anħa")
        assert R.apply(r, w("anka")) == w("aŋka")
    for r in (demo("devoicing.final"), tsv("S095")):
        assert R.apply(r, w("taɓ")) == w("taɓ") and R.apply(r, w("tad")) == w("tat")
    assert R.apply(tsv("S165"), w("ɓa")) == w("ɓa") and R.apply(tsv("S165"), w("ba")) != w("ba")
    lab = tsv("S068")
    assert lab.weight <= 2
    for x in ("wu", "ju", "pu", "mu", "ʔu", "hu"):
        assert R.apply(lab, w(x)) == w(x), x
    assert R.apply(lab, w("ku")) == w("kʷu")


def test_harmony_is_root_controlled():
    h = demo("harmony.back")
    assert R.apply(h, w("mikutolu")) == w("mikiteli")  # no boundary given: the first vowel leads
    assert R.apply(h, w("mikutolu"), stem_index=2) == w("mukutolu")  # the root ku- leads, the prefix agrees
    assert R.apply(h, w("mikutolu"), stem_index=lambda f: 2) == w("mukutolu")
    assert R.apply_all(h, [w("mikutolu")], None, 2) == [w("mukutolu")]


def test_pick_rule_skips_rules_that_change_nothing():
    dead = rule("p > f / _i", id="dead")  # p occurs, never before i
    live = rule("t > d / a_a", id="live")
    lex = [w(x) for x in ("apa", "pata", "tapa", "kapu", "pamo", "lata")]
    inv = {s for f in lex for s in f}
    before = R.PICK_STATS["noop_draws"]
    picks = [R.pick_rule(np.random.default_rng(s), [dead, live], lex, inv) for s in range(60)]
    assert all(p is None or p.id == "live" for p in picks) and any(p is not None for p in picks)
    assert R.PICK_STATS["noop_draws"] > before
    assert R.pick_rule(np.random.default_rng(0), [dead], lex, inv) is None


def test_functional_load_counts_minimal_pairs():
    voicing = demo("lenition.intervocalic_voicing")
    base = [w(x) for x in ("tasi", "kelo", "monu", "ruka", "sefa", "lito", "naku", "fosa", "mika", "selu", "tura",
                           "kano", "kiso", "tome", "ripa", "sula", "meta", "nopi")]  # the rule fires, no pairs
    paired = base + [w("pala"), w("bala")]  # one p ~ b minimal pair, p initial: not in the rule's environment
    plain = base + [w("pala"), w("sumi")]
    assert R.functional_load(voicing, paired) == pytest.approx(0.1)  # the contrast's load, not just this context
    assert R.functional_load(voicing, plain) == 0.0
    many = base + [w(x) for x in ("pala", "bala", "pina", "bina", "apa", "aba", "pumo", "bumo")]
    assert R.functional_load(voicing, many) > R.functional_load(voicing, paired)
    vetoed = sum(R.pick_rule(np.random.default_rng(s), [voicing], paired, w("ptkbsfmnlraeiou")) is None
                 for s in range(200))
    vetoed_plain = sum(R.pick_rule(np.random.default_rng(s), [voicing], plain, w("ptkbsfmnlraeiou")) is None
                       for s in range(200))
    assert vetoed_plain == 0 and 120 < vetoed < 190  # load 0.1: veto 1 - exp(-1.5) = 78 %
    assert R.veto_probability(0.05) == pytest.approx(0.53, abs=0.02)


def test_describe_names_real_outputs():
    d = R.describe(tsv("S163"))
    assert "b > ɓ" in d and "became ɗ" not in d
    d = R.describe(rule("D > ɓ"))  # a class to a literal keeps place: b > ɓ, d > ɗ
    assert "b > ɓ" in d and "d > ɗ" in d and "became ɓ" not in d
    assert "p > b" in R.describe(demo("lenition.intervocalic_voicing"))
    assert "eschool" not in demo("epenthesis.cluster").example
    assert R.apply(demo("epenthesis.cluster"), w("pokl")) == w("pokəl")  # anaptyxis, as the example says


# --- review of run a24559: rule hygiene ------------------------------------------------------------------------------

def test_nasal_place_assimilation_takes_retroflex_and_labiodental():
    r = demo("assimilation.nasal_place")
    assert ipa(R.apply(r, w("amʈa"))) == "aɳʈa"
    assert ipa(R.apply(r, w("aŋɖa"))) == "aɳɖa"
    assert ipa(R.apply(r, w("aɳpa"))) == "ampa"     # was m{retroflex=1}
    assert ipa(R.apply(r, w("anfa"))) == "aɱfa"
    assert ipa(R.apply(r, w("aɱta"))) == "anta"
    rules, _ = R.load_tsv()
    s075 = next(q for q in rules if q.id == "S075")
    for x in ("aɳpa", "amʈa", "aɱka", "aɲʈa"):
        out = R.apply(s075, w(x))
        assert all(R.writable(s) for s in out), ipa(out)


def test_outputs_snapped_to_table_segments():
    from dataclasses import replace
    m_rf = replace(w("m")[0], retroflex=1)
    assert not R.writable(m_rf) and R.writable(R.snap(m_rf)) and R.snap(m_rf).manner == 3
    assert R.snap(w("a")[0]) == w("a")[0]
    toned = replace(w("ʊ")[0], height=1, tone=3)   # an axis combination with no symbol, tone kept
    sn = R.snap(toned)
    assert R.writable(sn) and sn.tone == 3
    # a rule that sets an unwritable combination: apply hands back table segments only
    rf = R.Rule("test.rf", R.lit(w("m")[0]), R.Change.set(retroflex=1))
    out = R.apply(rf, w("ama"))
    assert all(R.writable(s) for s in out) and ipa(out) != "a" + "m{retroflex=1}" + "a"


def test_s042_rare_and_diffusing():
    rules, _ = R.load_tsv()
    s042 = next(q for q in rules if q.id == "S042")
    assert s042.weight == 1.0 and s042.scope == "diffusing"


def test_epenthesis_uses_the_inventory_vowel():
    from planet.language import inventory as I
    rules, _ = R.load_tsv()
    s124 = next(q for q in rules if q.id == "S124")
    assert ipa(R.apply(s124, w("tak"))) == "takə"     # no inventory: the catalogue's ə
    inv = I.Inventory(consonants=list(w("ptkmn")), vowels=list(w("aiu")), freq={x: 1.0 for x in w("ptkmnaiu")})
    assert ipa(R.apply(s124, w("tak"), inventory=inv)) == "taki"
    cl = demo("epenthesis.cluster")
    assert ipa(R.apply(cl, w("takt"), inventory=inv)) == "takit"
    s042 = next(q for q in rules if q.id == "S042")
    assert R.epenthesis_for(s042, inv) is s042   # only vowel epenthesis is re-pointed
