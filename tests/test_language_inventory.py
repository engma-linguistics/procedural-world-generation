"""Proto-inventories look PHOIBLE-ish, respect make costs and dispersion; drawn words are legal and repair works."""

import collections
import math
from dataclasses import replace

import numpy as np
import pytest

from planet.language import inventory as I
from planet.language import profiles as P
from planet.language.percepts import from_ipa, to_ipa

N_DRAWS = 200


@pytest.fixture(scope="module")
def draws():
    rng = np.random.default_rng(20261103)
    return [I.draw_inventory(rng) for _ in range(N_DRAWS)]


def _stat(measure, key):
    return I.phoible_sizes()[measure]["stat"][key]


def test_sizes_within_phoible_quartiles(draws):
    """Self-check against the table: drawn size quartiles near PHOIBLE's, the median inside its interquartile range."""
    for measure, get, tol in (("consonants", lambda v: len(v.consonants), 3), ("vowels", lambda v: len(v.vowels), 3)):
        n = np.array([get(v) for v in draws])
        q1, med, q3 = np.percentile(n, [25, 50, 75])
        p1, p3 = _stat(measure, "q1"), _stat(measure, "q3")
        assert p1 <= med <= p3, (measure, med, p1, p3)
        assert abs(q1 - p1) <= tol and abs(q3 - p3) <= tol, (measure, q1, q3, p1, p3)
        inside = np.mean((n >= p1) & (n <= p3))
        assert inside >= 0.4, (measure, inside)


def test_top_segments_overlap_phoible(draws):
    cnt = collections.Counter(s for v in draws for s in v.consonants + v.vowels)
    ours = [s for s, _ in cnt.most_common(20)]
    cons, vows = I.phoible_pool()
    table = [s for s, _ in sorted(cons + vows, key=lambda t: -t[1])[:20]]
    overlap = len(set(ours) & set(table))
    assert overlap >= 16, (overlap, [to_ipa(s) for s in ours], [to_ipa(s) for s in table])
    # the commonest segments are near-universal in the draws, as in PHOIBLE (m 0.97, i 0.94, k 0.90)
    for ipa in ("m", "i", "k"):
        assert cnt[from_ipa(ipa)[0]] / N_DRAWS > 0.8, ipa


def test_vowel_dispersion_floor(draws):
    for v in draws:
        plain = [x for x in v.vowels if x == I._quality(x)]
        for i, a in enumerate(plain):
            for b in plain[i + 1:]:
                assert I.vowel_distance(a, b) >= I.MIN_V_DIST, (to_ipa(a), to_ipa(b))
        quals = set(plain)
        for x in v.vowels:   # long / nasal vowels only on qualities the system has
            assert I._quality(x) in quals, to_ipa(x)


def test_tone_share_and_tone_deaf_profile(draws):
    share = np.mean([bool(v.tones) for v in draws])
    assert 0.12 <= share <= 0.36, share   # PHOIBLE 0.23
    deaf = replace(P.HUMAN, id="tone_deaf", hear={**P.HUMAN.hear, "tone": 0.0})
    rng = np.random.default_rng(7)
    assert not any(I.draw_inventory(rng, deaf).tones for _ in range(60))


def test_lipless_profile_draws_no_labial():
    lipless = replace(P.HUMAN, id="lipless", make_cost={**P.HUMAN.make_cost, "labial": math.inf})
    rng = np.random.default_rng(11)
    for _ in range(40):
        inv = I.draw_inventory(rng, lipless)
        assert inv.consonants
        assert not [to_ipa(c) for c in inv.consonants if c.place == 0 or c.double]


def test_drawn_words_are_legal(draws):
    rng = np.random.default_rng(3)
    for inv in draws[:40]:
        for _ in range(40):
            w = I.draw_word(rng, inv)
            assert I.legal(w, inv), (to_ipa_word(w), inv.max_onset, inv.max_coda, inv.coda_class)


def to_ipa_word(w):
    return "".join(to_ipa(s) for s in w)


def test_repair_makes_illegal_words_legal(draws):
    rng = np.random.default_rng(5)
    for k, inv in enumerate(draws[:40]):
        other = draws[(k + 7) % len(draws)]
        for _ in range(25):
            # a foreign word: another lect's segments, clusters shuffled in
            w = list(I.draw_word(rng, other, n_syll=int(rng.integers(1, 4))))
            if rng.random() < 0.5:
                w.insert(int(rng.integers(len(w) + 1)), other.consonants[int(rng.integers(len(other.consonants)))])
            if rng.random() < 0.3:
                w = [s for s in w if s.kind == "C"] or w   # no vowel at all
            r = I.repair(tuple(w), inv)
            assert r and I.legal(r, inv), (to_ipa_word(w), to_ipa_word(r), inv.max_onset, inv.max_coda, inv.coda_class,
                                           inv.onset_required, inv.repair_style)
    # a legal word is left alone
    inv = draws[0]
    w = I.draw_word(rng, inv)
    assert I.repair(w, inv) == w


def test_simple_syllables_repair_clusters():
    rng = np.random.default_rng(9)
    for _ in range(50):
        inv = I.draw_inventory(rng)
        if inv.max_coda == 0:
            break
    else:
        pytest.skip("no simple-syllable inventory drawn")
    w = tuple(from_ipa("strakt"))
    r = I.repair(w, inv)
    assert I.legal(r, inv) and r[-1].kind == "V" and not any(a.kind == b.kind == "C" for a, b in zip(r, r[1:]))


def test_json_round_trip(draws):
    for inv in draws[:20]:
        back = I.from_json(I.to_json(inv))
        assert back.consonants == inv.consonants and back.vowels == inv.vowels and back.tones == inv.tones
        assert back.shapes == inv.shapes and back.stress == inv.stress and back.coda_class == inv.coda_class


def test_deterministic_per_seed():
    a = I.draw_inventory(np.random.default_rng(42))
    b = I.draw_inventory(np.random.default_rng(42))
    assert I.to_json(a) == I.to_json(b)


def test_observed_inventory_after_change(draws):
    inv = draws[3]
    rng = np.random.default_rng(1)
    forms = [I.draw_word(rng, inv) for _ in range(200)]
    forms.append(tuple(from_ipa("qʼa")))
    obs = I.observed(inv, forms)
    assert from_ipa("qʼ")[0] in obs.consonants and set(obs.consonants) <= set(inv.consonants) | {from_ipa("qʼ")[0]}
    assert obs.max_onset == inv.max_onset and math.isfinite(obs.cost[from_ipa("qʼ")[0]])
