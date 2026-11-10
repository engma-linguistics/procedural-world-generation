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


def test_coda_liquids_are_allophones():
    """Dark ɫ and approximant ɹ only before a consonant or word-finally, plain l and trilled r elsewhere: allophones (the
    English and Dutch pattern), not extra phonemes; once ɹ stands before a vowel it contrasts."""
    forms = _forms("lata", "ilu", "pali", "kaɫ", "taɫka", "rapa", "kira", "paɹ", "taɹku", "ruki")
    segs = list(dict.fromkeys(s for f in forms for s in f))
    al = I.phonemic(forms, segs)
    assert al.get(_seg("ɫ")) == (_seg("l"), "coda")
    assert al.get(_seg("ɹ")) == (_seg("r"), "coda")
    assert _seg("ɹ") not in I.phonemic(forms + _forms("ɹa"), segs)


def test_allophones_stay_allophones_in_word_building():
    """Lane 14b: word building works on the phonemes (a coda ɹ that a suffix puts before a vowel is r again, Dutch maar
    [maːɹ] / mare [maːrə]), and the allophone rule stays productive (a new coda r is said ɹ), so the pair keeps its
    complementary distribution."""
    forms = _forms("rapa", "kira", "paɹ", "taɹku", "ruki", "tama")
    inv = I.Inventory(consonants=[_seg(x) for x in "rptkm"], vowels=[_seg(x) for x in "aiu"],
                      shapes={"CV": 0.6, "CVC": 0.4}, max_coda=1)
    ob = I.observed(inv, forms)
    assert ob.allophones.get(_seg("ɹ")) == (_seg("r"), "coda")
    assert I.allophonic(tuple(from_ipa("paɹa")), ob, underlying=True) == tuple(from_ipa("para"))
    assert I.allophonic(tuple(from_ipa("paɹa")), ob) == tuple(from_ipa("paɹa"))   # (a sound change's stranding stays)
    assert I.allophonic(tuple(from_ipa("kurta")), ob) == tuple(from_ipa("kuɹta"))
    assert I.realize(tuple(from_ipa("paɹi")), ob) == tuple(from_ipa("pari"))


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


def test_legal_rejects_vowel_runs_and_initial_geminates(draws):
    """No run of three vowels, no two vowels of one quality (that is a long vowel), no word-initial geminate; repair
    resolves them by fusion, glide formation or elision (Casali 1997)."""
    inv = next(d for d in draws if not d.onset_required and from_ipa("j")[0] in d.consonants
               and {from_ipa(v)[0] for v in "aeiou"} <= set(d.vowels) and not d.tones)
    for bad in ("kaa", "kaiea", "ppa", "kioua"):
        assert not I.legal(tuple(from_ipa(bad)), inv), bad
        r = I.repair(tuple(from_ipa(bad)), inv)
        assert I.legal(r, inv) and I._vowel_trouble(r) is None and not I._initial_geminate(r), (bad, to_ipa_word(r))
    assert to_ipa_word(I.repair(tuple(from_ipa("kiao")), inv)) in ("kjao", "kao", "kio", "kijao")
    assert I.hiatus_in(tuple(from_ipa("kai"))) == 0 and I.hiatus_in(tuple(from_ipa("kia"))) == 1
    assert I.hiatus_in(tuple(from_ipa("kaia"))) == 1


def test_fuse_vowels():
    """Identical vowels side by side are one: long where the lect has long vowels, short where not; two level tones make a
    contour (H + L falling, L + H rising)."""
    f = lambda s, lo=True: to_ipa_word(I.fuse_vowels(tuple(from_ipa(s)), lo))   # noqa: E731
    assert f("kaa") == "kaː" and f("kaa", False) == "ka" and f("kaaa") == "kaː" and f("kaːa", False) == "kaː"
    assert f("kai") == "kai" and f("kãa") == "kãː"
    hl = I.fuse_vowels(tuple(from_ipa("ka˦a˨")))
    assert len(hl) == 2 and hl[1].tone == 5 and I.fuse_vowels(tuple(from_ipa("ka˨a˦")))[1].tone == 4


# ---------------------------------------------------------------------------------------------- sound lane, 2026-11-08
def test_pool_reads_multi_letter_phoible_rows():
    """PHOIBLE writes k͡p as kp and ᵐb as mb: the pool reads them whole (they were dropped, so no proto had them)."""
    pool = {to_ipa(s) for s, _ in I.phoible_pool()[0]}
    assert {"k͡p", "ɡ͡b", "ᵐb", "ⁿd", "ᵑɡ"} <= pool


def test_series_shares_near_phoible():
    """Series come whole and at PHOIBLE's rate: the share of protos with any member (retroflex, long vowels, ejectives,
    labial-velars, prenasalized stops) is near PHOIBLE's, not the 75% a segment-by-segment draw gave retroflexes."""
    rng = np.random.default_rng(7)
    n = 600
    invs = [I.draw_inventory(rng, P.HUMAN) for _ in range(n)]
    sh = I.series_shares()
    for k in ("retroflex", "long_v", "ejective", "labial_velar", "prenasal", "implosive"):
        got = sum(any(I.SERIES[k](s) for s in v.consonants + v.vowels) for v in invs) / n
        assert abs(got - sh[k]) < max(0.06, 0.35 * sh[k]), (k, got, sh[k])
    ej = [v for v in invs if any(I.SERIES["ejective"](s) for s in v.consonants)]
    assert ej and sum(sum(I.SERIES["ejective"](s) for s in v.consonants) for v in ej) / len(ej) >= 3  # (pʼ tʼ kʼ, not a lone kʼ)


def test_vowel_qualities_follow_phoible():
    """Vowel series take slots: the number of distinct vowel qualities stays near PHOIBLE's (median 6) whether or not a
    proto has long or nasal vowels, and each quality's share is near PHOIBLE's (i, a, u near-universal; ɑ not twice its
    share), sound lane pass 2."""
    rng = np.random.default_rng(11)
    n = 800
    invs = [I.draw_inventory(rng, P.HUMAN) for _ in range(n)]
    nq = [len({I._quality(v) for v in inv.vowels}) for inv in invs]
    assert 5.5 <= float(np.median(nq)) <= 6.5 and 5.8 < float(np.mean(nq)) < 7.0, (np.median(nq), np.mean(nq))
    with_long = [q for q, inv in zip(nq, invs) if any(v.length for v in inv.vowels)]
    assert with_long and float(np.median(with_long)) <= 6.5
    cnt = collections.Counter(to_ipa(I._quality(v)) for inv in invs for v in {I._quality(x) for x in inv.vowels})
    for q, lo, hi in (("i", 0.9, 1.0), ("a", 0.88, 1.0), ("u", 0.88, 1.0), ("ɑ", 0.03, 0.17), ("ə", 0.12, 0.36)):
        assert lo <= cnt[q] / n <= hi, (q, cnt[q] / n)


def test_small_inventories_use_common_sounds():
    """Small inventories are built from common sounds (PHOIBLE: ~7% of the consonants of a <= 12-consonant inventory are
    in fewer than 10% of languages)."""
    rng = np.random.default_rng(8)
    freq = I._pool_freq()
    shares = []
    for _ in range(400):
        inv = I.draw_inventory(rng, P.HUMAN, size_hint=(int(rng.integers(7, 13)), 5))
        shares.append(np.mean([freq.get(s, 0.0) < 0.1 for s in inv.consonants]))
    assert np.mean(shares) < 0.12, np.mean(shares)


def test_dragons_draw_sub_bass():
    """The dragon profile's cheap sub-bass register appears in its protos (it was in none)."""
    par = {"chromatic_dragon": ["draconic"], "draconic": ["reptilian"]}
    prof = P.resolve_profile("chromatic_dragon", lambda l: par.get(l, []))
    rng = np.random.default_rng(9)
    invs = [I.draw_inventory(rng, prof) for _ in range(60)]
    assert sum(any(v.register < 0 for v in inv.vowels) for inv in invs) > 20
    assert not any(v.register for inv in [I.draw_inventory(rng, P.HUMAN) for _ in range(60)] for v in inv.vowels)


def test_stress_marked():
    w = tuple(from_ipa("patakan"))
    assert I.stress_marked(w, "penult") == "paˈtakan"
    assert I.stress_marked(w, "initial") == "ˈpatakan"
    assert I.stress_marked(w, "final") == "pataˈkan"
    assert I.stress_marked(w, "none") == "patakan"
    assert I.stressed_ipa("ostro ta", "final") == "osˈtro ta"


def test_contour_on_long_vowel_is_two_levels():
    from planet.language.lect import tonemes
    a = from_ipa("a")[0]
    segs = [replace(a, tone=1), replace(a, tone=3), replace(a, tone=5, length=1)]
    assert tonemes(segs) == [1, 3]
    assert tonemes(segs + [replace(a, tone=4)]) == [1, 3, 4]


def test_tonal_lect_hears_loans_with_tone():
    inv = I.Inventory(consonants=list(from_ipa("ptk")), vowels=list(from_ipa("aiu")), tones=[1, 3])
    a_hi = replace(from_ipa("a")[0], tone=3)
    heard = P.hear_word((from_ipa("p")[0], a_hi), P.HUMAN, I.segments(inv))
    assert heard[1].tone == 3


def test_drawn_marked_stops_have_their_plain_partner(draws):
    """PW-1537 R3 (lane 9): no drawn proto has an aspirated or ejective stop or affricate without a plain partner at its
    place (lateral affricates aside: PHOIBLE has tɬʼ beside ɬ more often than tɬ)."""
    for inv in draws:
        have = {replace(x, length=0) for x in inv.consonants}
        for s in inv.consonants:
            if s.larynx in (1, 2) and s.manner in (0, 1) and not s.lateral:
                assert I.plain_partners(s) & have, (to_ipa(s), [to_ipa(x) for x in inv.consonants])



def test_token_priors_follow_lexical_counts():
    """PW-1623: phonemes are drawn by their token class's busyness in words (data/token_frequency.tsv, from NorthEuraLex),
    not by how many inventories have them: a is busier than u, t and k than p, b and g; a class the table lacks keeps
    its presence weight."""
    from planet.language import inventory as INV
    from planet.language.percepts import parse_segment as P
    t = INV.token_priors()
    assert t and t[INV.token_class(P("a"))] > t[INV.token_class(P("u"))]
    assert t[INV.token_class(P("t"))] > t[INV.token_class(P("p"))] > t[INV.token_class(P("ɡ")) ] * 0.9
    assert INV.token_class(P("ǃ")) not in t and INV._lexical(P("ǃ"), 0.04) == pytest.approx(0.2)
