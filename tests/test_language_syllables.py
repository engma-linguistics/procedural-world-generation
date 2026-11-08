"""Sound lane pass 3: weight stress, deletion load, phonotactics re-read from the words, the phonotactic veto, stray contours."""
import numpy as np

from planet.language import inventory as I
from planet.language import rules as R
from planet.language.percepts import from_ipa, word_ipa


def w(s):
    return tuple(from_ipa(s))


def rule(text):
    r, why = R.parse_rule(["X", "deletion", text, "prosody", "stress", "3", "e"])
    assert r is not None, why
    return r


def test_weight_stress_is_the_latin_rule():
    assert R.stressed_vowel(w("pata"), "weight") == 1                    # two syllables: the first
    assert R.stressed_vowel(w("patakan"), "weight") == 1                 # light penult: the antepenult
    assert R.stressed_vowel(w("patantan"), "weight") == 3                # closed penult: heavy
    assert R.stressed_vowel(w("pataːka"), "weight") == 3                 # long penult: heavy
    assert I.stress_marked(w("patakan"), "weight") == "ˈpatakan"


def test_apocope_runs_under_weight_stress_and_not_without_stress():
    apo = rule("V[−stress] > ∅ / _#")
    assert word_ipa(R.apply(apo, w("kapata"), "weight")) == "kapat"
    assert R.apply(apo, w("kapata"), "none") == w("kapata")


def test_a_conditioned_deletion_merges_only_where_it_applies():
    apo = rule("V[−stress] > ∅ / _#")
    lex = [w(x) for x in ("kata", "kita", "pulo", "sema")]
    assert R.functional_load(apo, lex, "penult") == 0.0                  # kat, kit, pul, sem: nothing merges
    lex2 = lex + [w("kato")]
    assert R.functional_load(apo, lex2, "penult") > 0                     # kata and kato both become kat


def test_syllable_profile_and_retemplate():
    open_ = [w(x) for x in ("pata", "kalu", "mi", "sapo")] * 10
    assert I.syllable_profile(open_) == (1, 0, False)
    closed = open_ + [w(x) for x in ("patan", "kalsu", "trak")] * 10
    mo, mc, med = I.syllable_profile(closed)
    assert (mo, mc, med) == (2, 1, True)
    inv = I.draw_inventory(np.random.default_rng(3))
    inv2 = I.retemplate(inv, open_)
    assert inv2.max_coda == 0 and inv2.max_onset == 1 and set(inv2.shapes) == {"CV", "V"}
    inv3 = I.retemplate(inv2, closed)
    assert inv3.max_coda == 1 and inv3.max_onset == 2 and "CVC" in inv3.shapes


def test_new_violations_counts_only_new_shapes():
    prof = (1, 0, False)
    before = [w("pata"), w("kalu")]
    assert I.new_violations(before, [w("pat"), w("kalu")], prof) == 1.0  # a final coda in an open-syllable lect
    assert I.new_violations(before, [w("pada"), w("kalu")], prof) == 0.0
