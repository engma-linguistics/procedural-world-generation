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
    assert R.title_name("'aba") == "'Aba" and R.title_name("!xu") == "!Xu" and R.title_name("ǫrn") == "Ǫrn"


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


@pytest.mark.parametrize("cs", [frozenset(), frozenset({"aspiration"}), R.ALL_CONTRASTS], ids=lambda c: "+".join(sorted(c)) or "none")
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
    bad = {k: v for k, v in groups.items() if any(not R.merged(a, b) for a, b in itertools.combinations(sorted(v), 2))}
    assert not bad, bad


def test_injective_over_vowels():
    groups = collections.defaultdict(set)
    for r in symbols():
        if r.seg.kind == "V" and not is_nonhuman(r.seg) and r.seg.tone in (0, 3):
            groups[R.spell(r.seg, R.ALL_CONTRASTS)].add(r.symbol)
    bad = {k: v for k, v in groups.items() if any(not R.merged(a, b) for a, b in itertools.combinations(sorted(v), 2))}
    assert not bad, bad


def test_contrasts_of():
    assert R.contrasts_of(from_ipa("ppʰa")) == {"aspiration"}
    assert R.contrasts_of(from_ipa("eə")) == {"schwa"}
    assert "dental" in R.contrasts_of(from_ipa("t̪t"))
    assert R.contrasts_of(from_ipa("pʰa")) == set()
