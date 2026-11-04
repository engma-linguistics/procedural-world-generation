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
    ("tone.voiced_coda_low", "tab", "tà", "taba", None),
    ("tone.glottal_coda_high", "taʔ", "tá", "ʔa", None),
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
    push = R.dispersion_rule(merge, inv)
    assert push is not None and push.cause == "dispersion"
    assert R.apply(push, w("pi")) == w("pɨ")  # i is at the top of the space: it centralizes out of e's way


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
    assert "tone.voiced_coda_low" not in {r.id for r in R.catalogue(atonal)}
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
