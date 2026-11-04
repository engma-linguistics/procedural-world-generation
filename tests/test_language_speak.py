"""planet/language/speak.py: IPA -> WAV (the mapping table covers the percept symbol table; WAVs are valid; backends skip
cleanly when missing)."""
import io
import json
import wave

import numpy as np
import pytest

from planet.language import percepts as P
from planet.language import speak as S

NONHUMAN = ["a‼", "aᵣ", "aᴖ", "a˯", "i˰", "aʬa", "aʭa", "aʞa", "ǃa", "ma˥˩"]


def _backend_or_skip(name: str):
    if name == "espeak":
        try:
            S._Espeak.load()
        except S.BackendUnavailable as e:
            pytest.skip(f"espeak backend unavailable: {e}")
    elif not S._Piper.available():
        pytest.skip(f"piper backend unavailable: no piper-tts or no voice at {S._Piper.model_path()}")


def _check_wav(b: bytes) -> np.ndarray:
    assert b[:4] == b"RIFF" and b[8:12] == b"WAVE"
    with wave.open(io.BytesIO(b)) as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == S.SR
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2")
    assert len(x) > S.SR * 0.05 and np.abs(x).max() > 1000
    return x


def test_mapping_covers_every_symbol_row():
    for row in P.symbols():
        words = S.tokenize(row.symbol)  # raises on any unmapped character
        if row.seg.kind == "T":  # a bare tone letter has no segment to carry it: nothing to say, but no error
            continue
        assert words and all(x.espeak and x.piper for w in words for x in w), row.symbol


def test_mapping_rows_are_well_formed():
    t = S.table()
    assert {r.kind for r in t.values()} <= {"base", "mod", "pre", "sep"}
    assert {r.fit for r in t.values()} <= {"exact", "near", "sub", "effect"}
    for r in t.values():
        if r.kind in ("base", "pre"):
            assert r.espeak and r.piper, r.ipa
    for sym in "‼ᵣᴖ˯˰":
        assert t[sym].effect, sym
    assert {t[c].effect for c in "ʬʭʞ"} == {"percussive_lip", "percussive_teeth", "percussive_beak"}


def test_piper_tokens_in_voice_id_map():
    cfg = S.PIPER_DIR / f"{S.PIPER_VOICE}.onnx.json"
    if not cfg.exists():
        pytest.skip(f"no piper voice config at {cfg}")
    idmap = json.loads(cfg.read_text())["phoneme_id_map"]
    missing = {(r.ipa, c) for r in S.table().values() for c in r.piper if c not in idmap}
    assert not missing


def test_tokenize_effects_and_tones():
    w = S.tokenize("s‼a mᵣa tsiʔᴖ ŋ˯ i˰ ma˥˩ ká")
    eff = [x.effects for ww in w for x in ww]
    assert {"growl"} in eff and {"purr"} in eff and {"source2"} in eff and {"sub"} in eff and {"ultra"} in eff
    tones = [x.tone for ww in w for x in ww if x.tone]
    assert tones == [(6.0, -6.0), (3, 3)]
    with pytest.raises(ValueError):
        S.tokenize("ka☃")


@pytest.mark.parametrize("backend", S.BACKENDS)
def test_speak_plain_word(backend, tmp_path):
    _backend_or_skip(backend)
    out = tmp_path / "w.wav"
    b = S.speak("kalima", out_path=out, backend=backend)
    _check_wav(b)
    assert out.read_bytes() == b


@pytest.mark.parametrize("backend", S.BACKENDS)
@pytest.mark.parametrize("ipa", NONHUMAN)
def test_speak_nonhuman_symbols(backend, ipa):
    _backend_or_skip(backend)
    _check_wav(S.speak(ipa, backend=backend))


@pytest.mark.parametrize("backend", S.BACKENDS)
def test_profile_register_lowers_and_slows(backend):
    _backend_or_skip(backend)
    human = _check_wav(S.speak("kalima", None, backend=backend))
    dragon = _check_wav(S.speak("kalima", S.profile_for_people("red_dragon"), backend=backend))
    assert len(dragon) > 1.2 * len(human)
    assert len(S.render("ka " * 4, None, backend)) <= S.MAX_WORD_S * S.SR * 4


def test_server_route_caches_wav():
    try:
        S._backend("auto")
        if not S.available_backends():
            pytest.skip("no speech backend available")
    except S.BackendUnavailable as e:
        pytest.skip(str(e))
    from planet import server
    b, code = server.speak("ipa=kalima&people=elf")
    assert code == 200 and b[:4] == b"RIFF"
    assert server.speak("ipa=kalima&people=elf")[0] is b
    assert server.speak("ipa=")[1] == 400
    assert server.speak("ipa=ka%E2%98%83")[1] == 400
