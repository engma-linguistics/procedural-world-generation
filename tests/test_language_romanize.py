"""planet.language.romanize: the house spelling (not slow)."""
import collections
import itertools
from dataclasses import replace

import pytest

from planet.language import romanize as R
from planet.language.percepts import core, from_ipa, is_nonhuman, symbols, to_ipa


def test_table_rows_parse():
    for ipa in R.table():
        assert len(from_ipa(ipa)) == 1, ipa


def test_rulings():
    r = R.romanize
    assert r("ŋa") == "nga" and r("ʃa") == "sha" and r("tʃa") == "cha" and r("ʒa") == "zha" and r("dʒa") == "ja"
    assert r("θa") == "tha" and r("ða") == "dha" and r("xa") == "kha" and r("ɣa") == "gha"
    assert r("qa") == "qa" and r("χa") == "qha" and r("ʁa") == "ġa" and r("ɢa") == "gqa"
    assert r("ʔa") == "'a" and r("aː") == "aa" and r("kʼa") == "k'a"
    assert r("ǃa") == "!a" and r("ǀa") == "|a" and r("ǁa") == "||a"
    assert r("á") == "á" and r("à") == "à" and r("a˧") == "a"
    assert r("ənə", {"schwa"}) == "ënë" and r("ənə", set()) == "ene"
    assert r("pʰapa") == "phapa" and r("pʰa") == "pa"  # aspiration written only where it contrasts
    assert r("θa", {"aspiration"}) == "þa" and r("χa", {"aspiration"}) == "x̣a"  # no clash with th, qh as aspirates


def test_velar_and_uvular_never_share():
    for cs in (set(), {"aspiration"}):
        for v, u in (("x", "χ"), ("ɣ", "ʁ"), ("k", "q"), ("ɡ", "ɢ"), ("ŋ", "ɴ")):
            assert R.romanize(v + "a", cs) != R.romanize(u + "a", cs)


def test_hyphen_where_a_digraph_would_mislead():
    assert R.romanize("nɡa", inventory=from_ipa("nŋɡa")) == "n-ga"
    assert R.romanize("nɡa", inventory=from_ipa("nɡa")) == "nga"  # no ŋ in the lect: nothing to misread
    assert R.romanize("tsa", inventory=from_ipa("tsa")) == "tsa"
    assert R.romanize("t.sa", inventory=from_ipa("tsa ts")) == "t-sa"
    assert R.romanize("kʔa", inventory=from_ipa("kʔakʼ")) == "k-'a"


def test_title_name():
    assert R.title_name("'aba") == "'Aba" and R.title_name("!xu") == "!Xu" and R.title_name("ørn") == "Ørn"


def _pool():
    base = [r.seg for r in symbols() if r.seg.kind == "C" and not is_nonhuman(r.seg)]
    pool = set(base)
    for b in base:
        if b.manner in (0, 1, 2) and b.place != 8:
            pool.add(replace(b, phonation=1) if b.voice else replace(b, larynx=1))
            if not b.voice:
                pool.add(replace(b, larynx=2))
            pool.add(replace(b, secondary=1))
            if b.place != 4:
                pool.add(replace(b, secondary=2))
        pool.add(replace(b, length=1))
    return pool


CONTRAST_SETS = [frozenset(), frozenset({"aspiration"}), frozenset({"dark_l", "beta", "breathy_h"}),
                 frozenset({"aspiration", "dark_l", "beta", "breathy_h"}), R.ALL_CONTRASTS - {"tone"}, R.ALL_CONTRASTS]


@pytest.mark.parametrize("cs", CONTRAST_SETS, ids=lambda c: "+".join(sorted(c)) or "none")
def test_injective_over_consonants(cs):
    """No two distinct consonants share a spelling under one contrast set, except the documented MERGES (and the contrasts
    the set says the lect lacks: aspiration not written, dentals not marked)."""
    groups = collections.defaultdict(set)
    for s in _pool():
        if "aspiration" not in cs and (s.larynx == 1 or s.phonation == 1):
            continue
        if "dental" not in cs and s.place == 1 and to_ipa(core(s)) not in R.table():
            continue
        groups[R.spell(s, cs)].add(to_ipa(s))
    bad = {k: v for k, v in groups.items() if any(not R.merged(a, b, cs) for a, b in itertools.combinations(sorted(v), 2))}
    assert not bad, bad


VOWEL_SETS = [frozenset(), frozenset({"schwa"}), frozenset({"open_e", "open_o", "back_a", "lax_i", "lax_u"}),
              frozenset({"open_e", "open_o", "back_a", "lax_i", "lax_u", "tone"}), R.ALL_CONTRASTS - {"tone"}, R.ALL_CONTRASTS]


@pytest.mark.parametrize("cs", VOWEL_SETS, ids=lambda c: "+".join(sorted(c)) or "none")
def test_injective_over_vowels(cs):
    groups = collections.defaultdict(set)
    tones = (0, 1, 3) if "tone" in cs else (0,)
    for r in symbols():
        if r.seg.kind == "V" and not is_nonhuman(r.seg) and r.seg.tone == 0:
            for t in tones:
                groups[R.spell(replace(r.seg, tone=t), cs)].add(r.symbol + str(t))
    bad = {k: v for k, v in groups.items()
           if any(not R.merged(a[:-1], b[:-1], cs) or a[-1] != b[-1] for a, b in itertools.combinations(sorted(v), 2))}
    assert not bad, bad


def test_reader_spellings():
    """ASCII first: the open, back and lax vowels and the odd consonants are plain letters unless the lect contrasts them."""
    r = R.romanize
    assert r("ɛ") == "e" and r("ɔ") == "o" and r("ɑ") == "a" and r("ɒ") == "a" and r("ɪ") == "i" and r("ʊ") == "u"
    assert r("ɫa") == "la" and r("βa") == "va" and r("ɦa") == "ha"
    assert r("eɛ") == "eè" and r("oɔ") == "oò" and r("aɑ") == "aå" and r("iɪ") == "iì" and r("uʊ") == "uù"
    assert r("é ɛ̀ ɔ́ o") == "éẹ̀ọ́o"  # a tonal lect: dot below, so the grave stays a tone mark
    assert r("lalɫa") == "lal-lla" and r("lːaɫa") == "l·lalla"  # ll = ɫ; a long l takes the Catalan middle dot
    assert r("vaβa") == "vabha" and r("vaβapʰap", {"beta", "aspiration"}) == "vaḇaphap"
    assert r("hɦa") == "h-hha" and r("hːaɦa") == "h·hahha"
    assert r("ə") == "e" and r("eə") == "ea" and r("eəa") == "eëa"
    assert r("ã") == "ã"  # nasal vowels: always a tilde


def test_nonhuman_spellings_are_ascii_letters():
    """The book reader must be able to say a non-human sound: ASCII letters only, the exact symbol stays in the IPA."""
    seen = {}
    for row in symbols():
        if is_nonhuman(row.seg):
            sp = R.romanize(row.symbol)
            assert sp.isascii() and sp.isalpha(), (row.symbol, sp)
            assert sp not in seen, (row.symbol, seen.get(sp), sp)
            seen[sp] = row.symbol
    assert R.romanize("a‼") == "arh" and R.romanize("aᵣ") == "arr" and R.romanize("aᴖ") == "awh"
    assert R.romanize("a˯") == "amh" and R.romanize("i˰") == "iih" and R.romanize("ʞa") == "cka"
    assert R.romanize("ma‼") == "marh" and R.romanize("ʁ‼a") == "grha"
    assert R.romanize("ar", inventory=from_ipa("aᵣ a r")) == "a-rr"  # a + trill is not the purred a


def test_contrasts_of():
    assert R.contrasts_of(from_ipa("ppʰa")) == {"aspiration"}
    assert R.contrasts_of(from_ipa("eəa")) == {"schwa"} and R.contrasts_of(from_ipa("eə")) == {"schwa_a"}
    assert R.contrasts_of(from_ipa("eɛ")) == {"open_e"} and R.contrasts_of(from_ipa("ɛ")) == set()
    assert R.contrasts_of(from_ipa("lɫ")) == {"dark_l"} and R.contrasts_of(from_ipa("ɫ")) == set()
    assert R.contrasts_of(from_ipa("á")) == {"tone"}
    assert "dental" in R.contrasts_of(from_ipa("t̪t"))
    assert R.contrasts_of(from_ipa("pʰa")) == set()
