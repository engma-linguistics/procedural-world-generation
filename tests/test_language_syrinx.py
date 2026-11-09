"""Second-voice tone for syrinx-voiced peoples (syrinx lane, 2026-11-08; docs/review/language/syrinx.md)."""
from dataclasses import replace

import numpy as np

from planet.language import inventory as INV
from planet.language import profiles as P
from planet.language import romanize as RO
from planet.language import speak as SP
from planet.language.percepts import Segment, distance, from_ipa, to_ipa, word_ipa


def _profile(lid: str, chain: tuple) -> P.VoiceProfile:
    parents = {a: [b] for a, b in zip(chain, chain[1:])}
    return P.resolve_profile(lid, lambda l: parents.get(l, []), None, P.load_profiles())


AARAKOCRA = _profile("aarakocra", ("aarakocra", "avian"))
DWARF = _profile("dwarf", ("dwarf",))


def test_notation_reads_second_voice_tone_after_the_mark():
    (v,) = from_ipa("a˦ᴖ˨˦")
    assert (v.tone, v.source2, v.tone2) == (3, 1, 4)
    (v,) = from_ipa("aᴖ˨")
    assert (v.tone, v.source2, v.tone2) == (0, 1, 1)
    (v,) = from_ipa("a˦ᴖ")
    assert (v.tone, v.source2, v.tone2) == (3, 1, 0)
    assert from_ipa("a˨˦")[0].tone2 == 0  # (no ᴖ: the letters are the first voice's)


def test_notation_round_trips():
    base = from_ipa("a")[0]
    for t in range(8):
        for t2 in range(8):
            for ln in (0, 1):
                v = replace(base, tone=t, source2=1, tone2=t2, length=ln)
                assert from_ipa(to_ipa(v)) == [v], to_ipa(v)
    w = tuple(from_ipa("ki˨ᴖ˦˨ta˦ᴖ.u"))
    assert tuple(from_ipa(word_ipa(w))) == w
    assert to_ipa(from_ipa("a˦ᴖ˨˦")[0]) == "a˦ᴖ˨˦"


def test_second_voice_tone_is_drawn_for_syrinx_peoples_only():
    t2 = sum(any(v.tone2 for v in INV.draw_inventory(np.random.default_rng(s), AARAKOCRA).vowels) for s in range(60))
    assert 5 <= t2 <= 50  # about half of the protos with a second voice (TONE2_SHARE)
    for prof in (None, P.HUMAN, DWARF):
        for s in range(60):
            inv = INV.draw_inventory(np.random.default_rng(s), prof)
            assert not any(v.source2 or v.tone2 for v in inv.vowels)


def test_drawn_second_voice_tones_are_a_set_on_every_second_voice_vowel():
    for s in range(80):
        inv = INV.draw_inventory(np.random.default_rng(s), AARAKOCRA)
        s2 = [v for v in inv.vowels if v.source2]
        if any(v.tone2 for v in s2):
            sets = {tuple(sorted(v.tone2 for v in s2 if replace(v, tone2=0) == q)) for q in {replace(v, tone2=0) for v in s2}}
            assert len(sets) == 1 and tuple(sorted(sets.pop())) in {tuple(sorted(x)) for x, _ in INV.TONE2_SETS}
            assert all(v.tone2 for v in s2)


def test_epenthetic_vowel_is_never_a_second_voice_one_when_a_plain_one_exists():
    i, u, us = from_ipa("i")[0], from_ipa("u")[0], from_ipa("uᴖ˨")[0]
    inv = INV.Inventory(consonants=list(from_ipa("ptk")), vowels=[i, u, from_ipa("a")[0], us],
                        freq={i: 0.9, u: 0.9, us: 0.001})
    assert not INV.epenthetic_vowel(inv).source2


def test_humans_flatten_the_second_voice():
    human_inv = INV.segments(INV.Inventory(consonants=list(from_ipa("ptkmn")), vowels=list(from_ipa("aiu"))))
    heard = P.hear_word(from_ipa("ta˦ᴖ˨˦"), P.HUMAN, human_inv)
    assert word_ipa(heard) == "ta"
    # a human hears the second voice's contour at 0.3: two contours are nearer for a human ear than for a bird's
    a, b = from_ipa("aᴖ˨˦")[0], from_ipa("aᴖ˦˨")[0]
    assert distance(a, b, P.HUMAN.hear_weights()) < distance(a, b, AARAKOCRA.hear_weights())


def test_birds_keep_or_park_the_second_voice_tone():
    plain = list(from_ipa("aiu")) + list(from_ipa("aᴖ"))
    no_t2 = INV.segments(INV.Inventory(consonants=list(from_ipa("ptk")), vowels=plain))
    assert word_ipa(P.hear_word(from_ipa("taᴖ˨˦"), AARAKOCRA, no_t2)) == "taᴖ"  # (parallel: no contrast to keep)
    t2 = INV.segments(INV.Inventory(consonants=list(from_ipa("ptk")),
                                    vowels=list(from_ipa("aiu")) + list(from_ipa("aᴖ˦.aᴖ˨.aᴖ˨˦"))))
    assert word_ipa(P.hear_word(from_ipa("taᴖ˨˦"), AARAKOCRA, t2)) == "taᴖ˨˦"
    assert word_ipa(P.hear_word(from_ipa("taᴖ˥"), AARAKOCRA, t2)) == "taᴖ˦"  # (the nearest one it has)


def test_costs_and_keys():
    v = from_ipa("aᴖ˨˦")[0]
    assert "tone2" in P.keys_of(v) and "source2" in P.keys_of(v)
    assert P.human_cost(v) == float("inf")
    assert np.isfinite(P.species_cost(AARAKOCRA, v))
    assert P.human_voiced(P.HUMAN) and P.human_voiced(DWARF) and not P.human_voiced(AARAKOCRA)


def test_spelling_puts_the_second_tone_on_the_w():
    assert RO.romanize_word(tuple(from_ipa("ka˦ᴖ˨˦"))) == "káw̌h"
    assert RO.romanize_word(tuple(from_ipa("kaᴖ˨"))) == "kaẁh"
    assert RO.romanize_word(tuple(from_ipa("kaᴖ"))) == "kawh"
    assert RO.romanize_word(tuple(from_ipa("ka˦ᴖ˨˦")), book=True) == "kawh"


def test_speech_reads_the_second_contour():
    (k, a) = SP.tokenize("ka˦ᴖ˨˦")[0]
    assert a.tone == (3.0, 3.0) and a.tone2 == (-3.0, 3.0) and "source2" in a.effects
    (k, a) = SP.tokenize("kaᴖ")[0]
    assert a.tone is None and a.tone2 is None
    sr = SP.SR
    t = np.arange(int(0.4 * sr)) / sr
    x = np.sin(2 * np.pi * 200 * t).astype(np.float32)

    def f0(y, q):
        c = int(len(y) * q)
        sp = np.abs(np.fft.rfft(y[c - 1024:c + 1024] * np.hanning(2048), 16384))
        return np.fft.rfftfreq(16384, 1 / sr)[np.argmax(sp)]
    up, down = SP.second_voice(x, (-3, 3), (0, 0)), SP.second_voice(x, (3, -3), (0, 0))
    assert f0(up, 0.15) < f0(up, 0.85) and f0(down, 0.15) > f0(down, 0.85)
    assert 280 < f0(SP.second_voice(x, None, None), 0.5) < 320  # (parallel: a fifth up, 200 Hz -> ~300 Hz)
