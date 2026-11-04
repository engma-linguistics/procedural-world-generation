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


def test_proto_words_pronounceable(draws):
    """Review of run a24559 (proto *çla˨wu˦vnje˦k*): onsets and codas of at most two consonants; a two-consonant onset
    is obstruent or nasal + liquid/glide rising into the vowel, or s + voiceless stop; a two-consonant coda opens with a
    sonorant or is stop + s; medial runs at most three; tone only in tonal inventories."""
    from planet.language.percepts import SONORITY
    rng = np.random.default_rng(7)
    for inv in draws[:80]:
        assert inv.max_onset <= 2 and inv.max_coda <= 2
        for _ in range(15):
            w = I.draw_word(rng, inv)
            assert not inv.tones or all(s.tone for s in w if s.kind == "V")
            assert inv.tones or all(s.tone == 0 for s in w)
            assert all(s.kind != "T" for s in w)
            runs = I._runs(w)
            assert len(runs[0]) <= 2 and len(runs[-1]) <= 2, to_ipa_word(w)
            assert all(len(r) <= 3 for r in runs[2:-1:2]), to_ipa_word(w)
            on = runs[0]
            if len(on) == 2:
                a, b = on
                assert I._s_cluster(a, b) or (SONORITY(b) >= 7 and SONORITY(a) <= 6), to_ipa_word(w)
    st, pn, vn = (tuple(from_ipa(x)) for x in ("st", "pn", "vn"))
    inv = next(v for v in draws if v.max_onset == 2)
    assert not inv.onset_ok(pn) and not inv.onset_ok(vn)
    assert inv.onset_ok(st) or not set(st) <= set(inv.consonants)


# ---------------------------------------------------------------------------------------------- phonemes and allophones
def _forms(*ws):
    return [tuple(from_ipa(w)) for w in ws]


def _seg(ipa):
    return from_ipa(ipa)[0]


def test_assimilated_nasal_is_an_allophone():
    """ŋ only before k and ɡ, n never there: ŋ is listed as an allophone of n (nasal place assimilation), not a phoneme."""
    forms = _forms("naŋka", "taŋɡa", "ini", "nuta", "kina", "aŋki", "mana", "tan")
    segs = list(dict.fromkeys(s for f in forms for s in f))
    al = I.phonemic(forms, segs)
    assert al.get(_seg("ŋ")) == (_seg("n"), "nasal_place")
    assert _seg("n") not in al and _seg("m") not in al
    # once ŋ also stands before a vowel (a contrast: ŋa vs na), it is a phoneme
    forms2 = forms + _forms("ŋa")
    assert _seg("ŋ") not in I.phonemic(forms2, segs)
    # the observed inventory lists the phonemes and keeps ŋ beside them
    inv = I.Inventory(consonants=[_seg(x) for x in "nmtk"] + [_seg("ɡ")], vowels=[_seg(x) for x in "aiu"],
                      shapes={"CV": 0.6, "CVC": 0.4}, max_coda=1)
    ob = I.observed(inv, forms)
    assert _seg("ŋ") not in ob.consonants and _seg("ŋ") in ob.allophones and _seg("n") in ob.consonants
    assert {"ipa": "ŋ", "of": "n", "test": "nasal_place", "where": I.ALLO_TESTS["nasal_place"]} in I.allophones_json(ob)
    # new words are drawn from the phonemes and realized: n before k comes out as ŋ, and ŋ-words are legal
    assert I.realize(tuple(from_ipa("anka")), ob) == tuple(from_ipa("aŋka"))
    assert I.legal(tuple(from_ipa("aŋka")), ob)
    rng = np.random.default_rng(1)
    for _ in range(200):
        w = I.draw_word(rng, ob, 2)
        for j, s in enumerate(w):
            if s == _seg("n") and j + 1 < len(w):
                assert w[j + 1].place != 5  # (no unassimilated n before a velar)


def test_inserted_glottal_stop():
    """ʔ only word-initially before vowels, no vowel-initial words: an inserted onset, not a phoneme; with a vowel-initial
    word beside it, a phoneme."""
    forms = _forms("ʔata", "ʔiku", "tama", "ʔumi", "kita")
    segs = list(dict.fromkeys(s for f in forms for s in f))
    assert I.phonemic(forms, segs).get(_seg("ʔ")) == (None, "glottal_onset")
    assert _seg("ʔ") not in I.phonemic(forms + _forms("aku"), segs)


def test_intervocalic_voicing_allophone():
    forms = _forms("tada", "pata", "tiku", "kadi", "tupa", "atu")
    segs = list(dict.fromkeys(s for f in forms for s in f))
    al = I.phonemic(forms, segs)
    assert al.get(_seg("d")) is None  # (t also stands between vowels: atu, pata: d contrasts)
    forms = _forms("tada", "padi", "tiku", "kadi", "tupi", "kat")
    segs = list(dict.fromkeys(s for f in forms for s in f))
    assert I.phonemic(forms, segs).get(_seg("d")) == (_seg("t"), "intervocalic")


def test_two_allophones_of_one_phoneme_must_not_share_an_environment():
    forms = _forms("kaɡa", "kiɣa", "kuta", "tik", "kat")  # ɡ and ɣ both between vowels, k never: only one can be k's
    segs = list(dict.fromkeys(s for f in forms for s in f))
    al = I.phonemic(forms, segs)
    assert sum(1 for x in ("ɡ", "ɣ") if al.get(_seg(x), (None,))[0] == _seg("k")) == 1
