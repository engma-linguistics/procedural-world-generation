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


def test_new_violations_types_only_counts_a_new_syllable_type():
    """PW-1622: a coda in an open-syllable lect is a new type; a second coda consonant in a lect with single codas is not."""
    before = [w("pata"), w("kalu")]
    assert I.new_violations(before, [w("pat"), w("kalu")], (1, 0, False), types_only=True) == 1.0
    assert I.new_violations([w("pant"), w("kalu")], [w("pantk"), w("kalu")], (1, 1, True)) == 1.0
    assert I.new_violations([w("pant"), w("kalu")], [w("pantk"), w("kalu")], (1, 1, True), types_only=True) == 0.0


def test_phonotactic_refusal_is_the_lines_not_the_draws():
    """PW-1622: a change the phonotactics turn down is not drawn again until the re-fire wait has passed (it was re-rolled
    each draw, about 440 a step, so CV lects grew codas within an interval or two), and daughters inherit the refusal."""
    from planet.language import lect as LC, lexicon as LX, profiles as PR
    lex = LX.Lexicon("x", {}, {}, True)
    for k, f in enumerate(["pata", "kalu", "mina", "sefo", "tuke", "lamo", "nupi", "kesa"] * 4):
        lex.words[f"W{k}"] = LX.Word(f"W{k}", w(f), "N", 3, (), 0.0)
    segs = sorted({s for x in lex.words.values() for s in x.form}, key=repr)
    inv = I.Inventory(consonants=[s for s in segs if s.kind == "C"], vowels=[s for s in segs if s.kind == "V"],
                      shapes={"CV": 1.0}, stress="initial")
    lc = LC.Lect(id="x", deme=0, people="human", parent=None, how="proto", born_kyr=10.0, lexicon=lex, inventory=inv,
                 profile=PR.HUMAN, profile_key="human")
    apocope = rule("V > ∅ / _#")

    class Always:
        def random(self):
            return 0.0
    assert lc.phonotactic_veto(apocope, Always()) == "type"   # (every word would end in a consonant: a new syllable type)
    lc.refused[LC.base_id(apocope.id)] = 9.0
    assert not lc.may_fire(apocope, 8.0) and lc.may_fire(apocope, 9.0 - lc.refire_kyr())
    assert not lc.copy("y", 0, 8.0, "bud").may_fire(apocope, 8.0)


def test_retemplate_keeps_the_held_open_pattern():
    """PW-1647: while the line holds open syllables and single onsets (its word-shape anchor), a few loans with codas or
    clusters do not open the template, so coins and loan repairs stay CV; once the line's own pattern has codas, they do."""
    open_ = [w(x) for x in ("pata", "kalu", "mi", "sapo")] * 10
    leaky = open_ + [w(x) for x in ("patan", "trak")] * 2   # (about 9% of the words: loans from a coda neighbour)
    inv = I.retemplate(I.draw_inventory(np.random.default_rng(3)), open_)
    assert I.retemplate(inv, leaky).max_coda >= 1                       # no anchor: the template opens
    held = I.pattern_of(open_)
    kept = I.retemplate(inv, leaky, held)
    assert kept.max_coda == 0 and kept.max_onset == 1 and set(kept.shapes) == {"CV", "V"}
    assert I.retemplate(inv, leaky, I.pattern_of(leaky)).max_coda >= 1  # a line that holds codas takes them
