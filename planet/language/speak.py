"""Hear a generated word: IPA in, WAV out (audio lane, 2026-11-03; research and choices in docs/review/language/audio.md).

speak(ipa, profile=None, out_path=None, backend="auto") -> WAV bytes (22.05 kHz mono, 16-bit).

1. Tokenize the IPA (longest match over data/ipa_to_speech.tsv base rows, prenasal prefixes before, modifiers after; input is
   NFD-normalized with percepts' aliases). Each segment gets a backend token and a set of effects.
2. A backend renders the plain segments and reports where each one sits in time:
   - "espeak": eSpeak NG through ctypes from the `espeakng-loader` wheel (libespeak-ng + data, no system install), phoneme
     mnemonics in [[ ]] on the 'hi' voice's phoneme table; segment times from its phoneme events. The always-there baseline.
   - "piper": a Piper VITS voice (data/language/tts/piper/, patched to output per-phoneme durations) fed IPA characters
     straight into its phoneme_id_map, bypassing text. Sounds much more natural, English-accented: sounds English lacks are
     replaced by the nearest one it was trained on.
   "auto" = piper when its model is on disk, else espeak.
3. numpy post-processing on each segment's span: tones (pitch shift), clicks and percussives (synthesized transients over the
   backend's glottal closure), growl ‼ (~80 Hz AM + noise), purr ᵣ (~28 Hz AM), second source ᴖ (a copy a fifth up), sub ˯ /
   ultra ˰ (octave shifts + an audible stand-in rumble / whistle: the real registers are outside human hearing), breathy,
   creaky. Then the profile's register: the whole word resampled down (bigger, slower) or up (smaller, quicker).
"""
from __future__ import annotations

import ctypes
import difflib
import hashlib
import io
import threading
import unicodedata
import wave
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import percepts as P

SR = 22050
DATA = Path(__file__).parent / "data"
MAP_PATH = DATA / "ipa_to_speech.tsv"
REPO = Path(__file__).resolve().parents[2]
PIPER_DIR = REPO / "data" / "language" / "tts" / "piper"
PIPER_VOICE = "en_US-lessac-medium"
ESPEAK_VOICE = "hi"
MAX_WORD_S = 1.0  # longest rendering per word (the server's cap); longer words are cut with a fade
MAX_WORDS = 12
BACKENDS = ("espeak", "piper")


class BackendUnavailable(RuntimeError):
    pass


# ---- the mapping table and tokenizer ----------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Row:
    ipa: str
    kind: str
    espeak: str
    piper: str
    fit: str
    effect: str
    note: str


@lru_cache(maxsize=1)
def table() -> dict[str, Row]:
    out = {}
    for line in MAP_PATH.read_text(encoding="utf-8").split("\n"):
        if not line or line.startswith("#") or line.startswith("ipa\t"):
            continue
        f = line.split("\t")
        f += [""] * (7 - len(f))
        r = Row(unicodedata.normalize("NFD", f[0]), *f[1:7])
        out[r.ipa] = r
    return out


@lru_cache(maxsize=1)
def _bases() -> tuple[dict[str, Row], int]:
    b = {k: r for k, r in table().items() if r.kind == "base"}
    return b, max(map(len, b))


IGNORED = P._COMBINING_IGNORED | P._SPACING_IGNORED
TONE_LEVEL_SEMIS = {1: -6.0, 2: -3.0, 3: 0.0, 4: 3.0, 5: 6.0}  # IPA tone letters ˩..˥ (pitch levels 1..5)
TONE_CODE_SEMIS = {1: (-3, -3), 2: (0, 0), 3: (3, 3), 4: (-3, 4), 5: (4, -3), 6: (6, 6), 7: (-6, -6)}  # percepts tone codes


@dataclass
class Seg:
    ipa: str
    espeak: str
    piper: str
    vowel: bool
    effects: set = field(default_factory=set)
    tone: tuple | None = None  # (start, end) semitones
    stress: str = ""


VOWEL_CHARS = set("iyɨʉɯuɪʏʊeøɘɵɤoəɛœɜɞʌɔæɐaɶɑɒ")


def tokenize(ipa: str) -> list[list[Seg]]:
    """IPA -> words of segments. Unknown characters raise ValueError (the table must cover symbols.tsv; tests check)."""
    s = P._normalize(ipa)
    t = table()
    bases, maxlen = _bases()
    words: list[list[Seg]] = [[]]
    pre, stress, i, n = "", "", 0, len(s)
    attach = False  # just after a segment: a prenasal letter there is a nasal release (ignored), as in percepts
    levels: list[int] = []

    def flush_levels():
        nonlocal levels
        if levels:
            w = words[-1]
            target = next((x for x in reversed(w) if x.vowel), None) or (w[-1] if w else None)
            if target is not None:
                target.tone = (TONE_LEVEL_SEMIS[levels[0]], TONE_LEVEL_SEMIS[levels[-1]])
            levels = []

    while i < n:
        ch = s[i]
        if ch in P._TONE_LETTERS:
            levels.append(P._TONE_LETTERS[ch])
            i += 1
            continue
        flush_levels()
        if ch.isspace() or ch in "‿-":
            if words[-1]:
                words.append([])
            attach = False
            i += 1
            continue
        if ch in "ˈˌ":
            stress = ch
            attach = False
            i += 1
            continue
        if ch == "{" and "}" in s[i:]:  # percepts' axis escape: not renderable, skipped
            i = s.index("}", i) + 1
            continue
        r = t.get(ch)
        if r is not None and r.kind == "sep":
            attach = False
            i += 1
            continue
        if r is not None and r.kind == "pre" and not attach:
            pre += ch
            i += 1
            continue
        m = next((L for L in range(min(maxlen, n - i), 0, -1) if s[i:i + L] in bases), None)
        if m is not None:
            b = bases[s[i:i + m]]
            pr = [t[c] for c in pre]
            seg = Seg(ipa=pre + b.ipa, espeak="".join(r.espeak for r in pr) + b.espeak,
                      piper="".join(r.piper for r in pr) + b.piper, vowel=b.ipa[0] in VOWEL_CHARS, stress=stress)
            if b.effect:
                seg.effects.add(b.effect)
            words[-1].append(seg)
            pre, stress, attach = "", "", True
            i += m
            continue
        if r is not None and r.kind == "mod":
            if words[-1]:
                seg = words[-1][-1]
                seg.ipa += ch
                seg.espeak += r.espeak
                seg.piper += r.piper
                if r.effect.startswith("tone_"):
                    seg.tone = TONE_CODE_SEMIS[int(r.effect[5:])]
                elif r.effect:
                    seg.effects.add(r.effect)
            i += 1
            continue
        if ch in IGNORED:
            i += 1
            continue
        raise ValueError(f"no speech mapping for {ch!r} (U+{ord(ch):04X}) in {ipa!r}")
    flush_levels()
    return [w for w in words if w]


# ---- backends: render plain segments, report each segment's (start, end) sample ---------------------------------------------

class _Espeak:
    lock = threading.Lock()
    lib = None
    buf: list = []
    events: list = []

    class EV(ctypes.Structure):
        _fields_ = [("type", ctypes.c_int), ("unique_identifier", ctypes.c_uint), ("text_position", ctypes.c_int),
                    ("length", ctypes.c_int), ("audio_position", ctypes.c_int), ("sample", ctypes.c_int),
                    ("user_data", ctypes.c_void_p), ("id", ctypes.c_char * 8)]

    @classmethod
    def load(cls):
        if cls.lib is not None:
            return cls.lib
        try:
            import espeakng_loader as L
            lib = ctypes.CDLL(L.get_library_path())
            data = L.get_data_path()
        except Exception as e:  # noqa: BLE001 - any failure means the backend is missing
            raise BackendUnavailable(f"espeak-ng not available (uv add espeakng-loader): {e}") from e
        CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.POINTER(cls.EV))

        def cb(wav, n, ev):
            if n > 0:
                cls.buf.append(np.ctypeslib.as_array(wav, (n,)).copy())
            k = 0
            while ev and ev[k].type != 0:
                if ev[k].type == 7:  # espeakEVENT_PHONEME
                    cls.events.append((ev[k].audio_position, ev[k].id.split(b"\0")[0].decode("latin1")))
                k += 1
            return 0
        cls._cb = CB(cb)
        sr = lib.espeak_Initialize(1, 0, data.encode(), 0x0001)  # AUDIO_OUTPUT_RETRIEVAL, phoneme events
        if sr <= 0:
            raise BackendUnavailable("espeak_Initialize failed")
        lib.espeak_SetSynthCallback(cls._cb)
        if lib.espeak_SetVoiceByName(ESPEAK_VOICE.encode()) != 0:
            raise BackendUnavailable(f"espeak voice {ESPEAK_VOICE!r} missing")
        cls.sr = sr
        cls.lib = lib
        return lib

    @classmethod
    def render(cls, words: list[list[Seg]], rate: float) -> tuple[np.ndarray, int, list[list[tuple[int, int]]]]:
        with cls.lock:
            lib = cls.load()
            lib.espeak_SetParameter(1, int(np.clip(150 * rate, 80, 450)), 0)  # espeakRATE, words per minute
            text = "[[" + " ".join("".join(x.stress.replace("ˈ", "'").replace("ˌ", ",") + x.espeak for x in w)
                                   for w in words) + "]]"
            cls.buf, cls.events = [], []
            b = text.encode()
            lib.espeak_Synth(b, len(b) + 1, 0, 1, 0, 0x101, None, None)  # espeakCHARS_UTF8 | espeakPHONEMES
            lib.espeak_Synchronize()
            audio = np.concatenate(cls.buf).astype(np.float32) / 32768 if cls.buf else np.zeros(1, np.float32)
            events = list(cls.events)
            sr = cls.sr
        return audio, sr, _align_espeak(words, events, len(audio), sr)


def _strip(m: str) -> str:
    return m.replace("'", "").replace(",", "").replace(":", "")


def _align_espeak(words, events, n, sr) -> list[list[tuple[int, int]]]:
    """Map espeak phoneme events onto our segments by matching mnemonic characters (difflib), interpolating the rest."""
    ev = [(int(t * sr / 1000), _strip(m)) for t, m in events if _strip(m) and m not in ("_", "_:", "_!", "||", "|")]
    evchars, evtime = [], []
    for k, (t0, m) in enumerate(ev):
        t1 = ev[k + 1][0] if k + 1 < len(ev) else n
        for j, c in enumerate(m):
            evchars.append(c)
            evtime.append((t0 + (t1 - t0) * j / len(m), t0 + (t1 - t0) * (j + 1) / len(m)))
    tok, owner = [], []
    for wi, w in enumerate(words):
        for si, x in enumerate(w):
            for c in _strip(x.espeak) or "?":
                tok.append(c)
                owner.append((wi, si))
    times: list = [None] * len(tok)
    for a, b, size in difflib.SequenceMatcher(None, tok, evchars, autojunk=False).get_matching_blocks():
        for k in range(size):
            times[a + k] = evtime[b + k]
    known = [k for k, v in enumerate(times) if v is not None]
    if not known:  # nothing matched: spread evenly
        times = [(n * k / len(tok), n * (k + 1) / len(tok)) for k in range(len(tok))]
    else:
        for k in range(len(tok)):
            if times[k] is None:
                lo = max((j for j in known if j < k), default=None)
                hi = min((j for j in known if j > k), default=None)
                a = times[lo][1] if lo is not None else 0.0
                b = times[hi][0] if hi is not None else float(n)
                gap = [j for j in range(len(tok)) if (lo is None or j > lo) and (hi is None or j < hi)]
                q = gap.index(k)
                times[k] = (a + (b - a) * q / len(gap), a + (b - a) * (q + 1) / len(gap))
    spans = [[[None, None] for _ in w] for w in words]
    for k, (wi, si) in enumerate(owner):
        sp = spans[wi][si]
        sp[0] = times[k][0] if sp[0] is None else min(sp[0], times[k][0])
        sp[1] = times[k][1] if sp[1] is None else max(sp[1], times[k][1])
    return [[(int(a), max(int(a) + 1, int(b))) for a, b in w] for w in spans]


class _Piper:
    lock = threading.Lock()
    voice = None

    @classmethod
    def model_path(cls) -> Path:
        return PIPER_DIR / f"{PIPER_VOICE}.align.onnx"

    @classmethod
    def available(cls) -> bool:
        try:
            import piper  # noqa: F401
        except Exception:  # noqa: BLE001
            return False
        return cls.model_path().exists() and Path(str(cls.model_path()) + ".json").exists()

    @classmethod
    def load(cls):
        if cls.voice is None:
            if not cls.available():
                raise BackendUnavailable(f"piper voice missing: uv add piper-tts onnx, then download {PIPER_VOICE} into "
                                         f"{PIPER_DIR} and patch it (docs/review/language/audio.md)")
            from piper import PiperVoice
            cls.voice = PiperVoice.load(str(cls.model_path()))
        return cls.voice

    @classmethod
    def render(cls, words, rate: float):
        from piper.config import SynthesisConfig
        with cls.lock:
            v = cls.load()
            idmap = v.config.phoneme_id_map
            chars, owner = [], []
            for wi, w in enumerate(words):
                if wi:
                    chars.append(" ")
                    owner.append(None)
                stressed = any(x.stress for x in w)
                first_v = next((k for k, x in enumerate(w) if x.vowel), None)
                for si, x in enumerate(w):
                    st = "ˈ" if (x.stress == "ˈ" or (not stressed and si == first_v)) else ("ˌ" if x.stress else "")
                    for c in st + (x.piper or "ʔ"):
                        if c in idmap:
                            chars.append(c)
                            owner.append((wi, si))
            ids = v.phonemes_to_ids(chars)
            audio, per_id = v.phoneme_ids_to_audio(ids, SynthesisConfig(length_scale=1.0 / rate, noise_scale=0.5,
                                                                         noise_w_scale=0.6), include_alignments=True)
        audio = np.asarray(audio, np.float32)
        sr = v.config.sample_rate
        if per_id is None:
            per_id = np.full(len(ids), len(audio) / max(1, len(ids)))
        ends = np.cumsum(per_id)
        starts = ends - per_id
        spans = [[[None, None] for _ in w] for w in words]
        for k, o in enumerate(owner):  # ids: ^ _ c0 _ c1 _ ... c_n _ $  -> char k at id 2 + 2k (its pad after it)
            if o is None:
                continue
            j = 2 + 2 * k
            a, b = starts[j], ends[min(j + 1, len(ends) - 1)]
            sp = spans[o[0]][o[1]]
            sp[0] = a if sp[0] is None else min(sp[0], a)
            sp[1] = b if sp[1] is None else max(sp[1], b)
        out = []
        for w in spans:
            row, last = [], 0
            for a, b in w:
                if a is None:
                    a = b = last
                row.append((int(a), max(int(a) + 1, int(b))))
                last = int(b)
            out.append(row)
        return audio, sr, out


def available_backends() -> list[str]:
    out = []
    try:
        _Espeak.load()
        out.append("espeak")
    except BackendUnavailable:
        pass
    if _Piper.available():
        out.append("piper")
    return out


def _backend(name: str):
    if name == "auto":
        return _Piper if _Piper.available() else _Espeak
    if name == "espeak":
        return _Espeak
    if name == "piper":
        return _Piper
    raise ValueError(f"backend must be auto, espeak or piper, not {name!r}")


# ---- DSP helpers --------------------------------------------------------------------------------------------------------------

def resample(x: np.ndarray, factor: float) -> np.ndarray:
    """Linear-interpolation resample to len(x) * factor samples."""
    n = max(1, int(round(len(x) * factor)))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def stretch(x: np.ndarray, n_out: int, sr: int = SR) -> np.ndarray:
    """WSOLA time-stretch x to n_out samples (pitch kept)."""
    win = int(0.03 * sr)
    if len(x) < 2 * win or n_out < 2 * win:
        return resample(x, n_out / max(1, len(x)))[:n_out]
    hop = win // 2
    w = np.hanning(win).astype(np.float32)
    out = np.zeros(n_out + win, np.float32)
    norm = np.zeros(n_out + win, np.float32)
    ratio = (len(x) - win) / max(1, n_out - win)
    tol = hop // 2
    prev = None
    for o in range(0, n_out - win + 1, hop):
        c = int(o * ratio)
        if prev is not None:
            lo, hi = max(0, c - tol), min(len(x) - win, c + tol)
            if hi > lo:
                ref = x[prev + hop:prev + hop + win] if prev + hop + win <= len(x) else None
                if ref is not None and len(ref) == win:
                    cands = np.lib.stride_tricks.sliding_window_view(x[lo:hi + win], win)[:, :hop]
                    c = lo + int(np.argmax(cands @ ref[:hop]))
        c = min(max(0, c), len(x) - win)
        out[o:o + win] += x[c:c + win] * w
        norm[o:o + win] += w
        prev = c
    norm[norm < 1e-3] = 1.0
    return (out / norm)[:n_out]


def pitch_shift(x: np.ndarray, semis: float, sr: int = SR) -> np.ndarray:
    """Pitch (and formants) shifted by semitones, length kept."""
    if abs(semis) < 0.05 or len(x) < 8:
        return x.copy()
    f = 2 ** (semis / 12)
    return stretch(resample(x, 1 / f), len(x), sr)


def envelope(x: np.ndarray, sr: int = SR, ms: float = 12.0) -> np.ndarray:
    k = max(1, int(sr * ms / 1000))
    return np.convolve(np.abs(x), np.ones(k) / k, mode="same").astype(np.float32)


def _rng(key: str) -> np.random.Generator:
    return np.random.default_rng(int.from_bytes(hashlib.sha1(key.encode()).digest()[:8], "little"))


def _bandnoise(n: int, lo: float, hi: float, rng, sr: int = SR) -> np.ndarray:
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / sr)
    spec[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(spec, n).astype(np.float32)
    return y / (np.abs(y).max() + 1e-9)


def _modes(n: int, freqs, decays_ms, amps, sr: int = SR) -> np.ndarray:
    t = np.arange(n) / sr
    y = sum(a * np.exp(-t / (d / 1000)) * np.sin(2 * np.pi * f * t) for f, d, a in zip(freqs, decays_ms, amps))
    return np.asarray(y, np.float32)


TRANSIENTS = {  # name -> (duration ms, modes (Hz, decay ms, amp), noise band (Hz), noise amp)
    "ʘ": (25, [(700, 6, 1.0), (1500, 3, 0.4)], (300, 2500), 0.3),       # bilabial click: a kiss
    "ǀ": (30, [(3500, 3, 0.5)], (2500, 9000), 0.9),                     # dental: a tsk, noisy and high
    "ǃ": (25, [(1600, 4, 1.0), (2600, 2, 0.4)], (800, 4000), 0.25),      # alveolar: a hollow pop
    "ǁ": (45, [(2200, 6, 0.4)], (1500, 7000), 0.8),                      # lateral: a giddy-up cluck, noisy
    "ǂ": (20, [(2800, 3, 1.0)], (2000, 6000), 0.3),                      # palatal: a sharp snap
    "percussive_lip": (35, [(450, 8, 1.0), (1100, 4, 0.3)], (200, 2000), 0.4),     # lip smack
    "percussive_teeth": (12, [(4800, 1.5, 1.0), (7000, 1, 0.5)], (4000, 10000), 0.5),  # teeth clack
    "percussive_beak": (40, [(900, 9, 1.0), (2300, 5, 0.5), (3900, 2, 0.2)], (600, 4000), 0.15),  # beak clap: hollow knock
}


def transient(kind: str, rng, sr: int = SR) -> np.ndarray:
    ms, modes, band, na = TRANSIENTS[kind]
    n = int(sr * ms / 1000)
    y = _modes(n, *zip(*modes), sr=sr)
    t = np.arange(n) / sr
    y = y + na * _bandnoise(n, band[0], band[1], rng, sr) * np.exp(-t / (ms / 3000))
    return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)


# ---- effects on spans --------------------------------------------------------------------------------------------------------

def _apply_span(y: np.ndarray, a: int, b: int, fn, fade: int) -> None:
    """y[a:b] := fn(y[a-fade:b+fade]) with raised-cosine crossfades at both ends."""
    a0, b0 = max(0, a - fade), min(len(y), b + fade)
    seg = y[a0:b0]
    new = fn(seg.copy(), a - a0, b - a0)
    w = np.ones(len(seg), np.float32)
    ra, rb = a - a0, b0 - b
    if ra > 0:
        w[:ra] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ra))
    if rb > 0:
        w[len(seg) - rb:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, rb))
    y[a0:b0] = seg * (1 - w) + new[:len(seg)] * w


def _effects(y: np.ndarray, sr: int, words, spans, key: str) -> np.ndarray:
    rng = _rng(key)
    fade = int(0.008 * sr)
    t_all = np.arange(len(y)) / sr
    overlay = np.zeros_like(y)
    for w, sp in zip(words, spans):
        for x, (a, b) in zip(w, sp):
            a, b = max(0, min(a, len(y) - 1)), max(1, min(b, len(y)))
            if b - a < 4:
                b = min(len(y), a + 4)
            if x.tone:
                s0, s1 = x.tone

                def tone(s, i, j, s0=s0, s1=s1):
                    if s0 == s1:
                        return pitch_shift(s, s0, sr)
                    k = 4  # a contour in 4 steps, crossfaded
                    out = s.copy()
                    edges = np.linspace(0, len(s), k + 1).astype(int)
                    for q in range(k):
                        st = s0 + (s1 - s0) * (q + 0.5) / k
                        lo, hi = edges[q], edges[q + 1]
                        out[lo:hi] = pitch_shift(s, st, sr)[lo:hi]
                    return out
                _apply_span(y, a, b, tone, fade)
            for e in sorted(x.effects):
                if e == "implosive":
                    _apply_span(y, a, b, lambda s, i, j: pitch_shift(s, -2, sr) * 1.1, fade)
                elif e == "growl":
                    def growl(s, i, j, a=a):
                        t = t_all[a - i:a - i + len(s)] if a - i >= 0 else np.arange(len(s)) / sr
                        am = 1 + 0.7 * np.sin(2 * np.pi * 85 * t[:len(s)])
                        nz = _bandnoise(len(s), 80, 3000, rng, sr) * envelope(s, sr) * 1.2
                        return (s * am + nz).astype(np.float32)
                    _apply_span(y, a, b, growl, fade)
                elif e == "purr":
                    def purr(s, i, j, a=a):
                        t = np.arange(len(s)) / sr
                        am = 0.5 + 0.5 * np.sin(2 * np.pi * 28 * t)
                        rumble = np.sin(2 * np.pi * 56 * t) * envelope(s, sr) * am * 0.8
                        return (s * (0.25 + 0.75 * am) + rumble).astype(np.float32)
                    _apply_span(y, a, b, purr, fade)
                elif e == "source2":
                    _apply_span(y, a, b, lambda s, i, j: (0.75 * s + 0.6 * pitch_shift(s, 7, sr)).astype(np.float32), fade)
                elif e == "sub":
                    def sub(s, i, j):
                        t = np.arange(len(s)) / sr
                        env = envelope(s, sr, 25)
                        r = (np.sin(2 * np.pi * 42 * t) + 0.5 * np.sin(2 * np.pi * 84 * t)) * env * 2.0
                        return (pitch_shift(s, -12, sr) + r).astype(np.float32)
                    _apply_span(y, a, b, sub, fade)
                elif e == "ultra":
                    def ultra(s, i, j):
                        t = np.arange(len(s)) / sr
                        wh = np.sin(2 * np.pi * (7500 + 400 * np.sin(2 * np.pi * 9 * t)) * t) * envelope(s, sr) * 0.6
                        return (pitch_shift(s, 12, sr) * 0.8 + wh).astype(np.float32)
                    _apply_span(y, a, b, ultra, fade)
                elif e == "breathy":
                    _apply_span(y, a, b, lambda s, i, j: (0.6 * s + _bandnoise(len(s), 500, 6000, rng, sr)
                                                          * envelope(s, sr) * 1.5).astype(np.float32), fade)
                elif e == "creaky":
                    def creak(s, i, j):
                        n = len(s)
                        pulses = np.zeros(n, np.float32)
                        p = 0
                        while p < n:
                            pulses[p:p + int(sr * 0.004)] = 1.0
                            p += int(sr / rng.uniform(30, 50))
                        sm = np.convolve(pulses, np.hanning(int(sr * 0.006)), "same")
                        return (s * (0.3 + 0.9 * sm / (sm.max() + 1e-9))).astype(np.float32)
                    _apply_span(y, a, b, creak, fade)
                elif e == "ejective":
                    k = transient("ǂ", rng, sr) * 0.25
                    p = min(len(y) - len(k), max(0, b - len(k)))
                    overlay[p:p + len(k)] += k
                elif e == "click" or e.startswith("percussive"):
                    kind = e if e.startswith("percussive") else unicodedata.normalize("NFC", x.ipa.lstrip("ᵐⁿᵑᶯᶮᶬᶰ"))[0]
                    k = transient(kind if kind in TRANSIENTS else "ǃ", rng, sr)
                    peak = float(np.abs(y).max() + 1e-9)
                    c = (a + b) // 2
                    p = min(max(0, c - len(k) // 4), len(y) - len(k))
                    y[max(0, p - fade):min(len(y), p + len(k))] *= 0.3  # quiet the backend's closure under the burst
                    overlay[p:p + len(k)] += k * peak * 0.9
    return y + overlay


# ---- profile -> register and rate --------------------------------------------------------------------------------------------

def voice_shape(profile) -> tuple[float, float]:
    """(semitones, final duration factor) for a VoiceProfile (None = human). register is in rough octaves: dragons -2 low and
    slow, small folk +1 higher and quicker. A small, fixed per-people offset (from the id, +-1.5 st) keeps peoples with the
    same register (human, elf) from sounding identical; it is voice colour, not a claim about them."""
    if profile is None:
        return 0.0, 1.0
    r = float(getattr(profile, "register", 0) or 0)
    semis = 5.0 * r
    dur = 1.0 + 0.25 * -r if r < 0 else 1.0 - 0.1 * r
    pid = getattr(profile, "id", "") or ""
    if pid and pid not in ("human", "human_default"):
        semis += (int(hashlib.sha1(pid.encode()).hexdigest()[:4], 16) / 65535 - 0.5) * 3.0
    return semis, max(0.6, dur)


# ---- the entry point ---------------------------------------------------------------------------------------------------------

def render(ipa: str, profile=None, backend: str = "auto") -> np.ndarray:
    """IPA -> float32 mono at SR."""
    words = tokenize(ipa)
    if not words:
        raise ValueError(f"nothing to say in {ipa!r}")
    if len(words) > MAX_WORDS:
        raise ValueError(f"at most {MAX_WORDS} words per call")
    semis, dur = voice_shape(profile)
    f = 2 ** (semis / 12)
    B = _backend(backend)
    audio, sr, spans = B.render(words, rate=1.0 / (dur * f))
    y = audio.astype(np.float32)
    y = y / (np.abs(y).max() + 1e-9) * 0.8
    y = _effects(y, sr, words, spans, ipa + "|" + str(getattr(profile, "id", "")))
    if abs(semis) > 0.05:
        y = resample(y, 1 / f)  # lower: longer, lower pitch and formants (a bigger tract); higher: the reverse
    if sr != SR:
        y = resample(y, SR / sr)
    nz = np.flatnonzero(np.abs(y) > 0.01 * (np.abs(y).max() + 1e-9))  # trim silence, keep 40 ms margins
    if len(nz):
        m = int(0.04 * SR)
        y = y[max(0, nz[0] - m):nz[-1] + m]
    cap = int(MAX_WORD_S * SR * len(words))
    if len(y) > cap:
        y = y[:cap]
        k = int(0.05 * SR)
        y[-k:] *= np.linspace(1, 0, k)
    y = y / (np.abs(y).max() + 1e-9) * 0.9
    return y.astype(np.float32)


def to_wav(y: np.ndarray, sr: int = SR) -> bytes:
    bio = io.BytesIO()
    with wave.open(bio, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    return bio.getvalue()


def speak(ipa: str, profile=None, out_path=None, backend: str = "auto") -> bytes:
    """Render an IPA string (words separated by spaces) as 22.05 kHz mono 16-bit WAV bytes; also written to out_path if
    given. profile: a planet.language.profiles.VoiceProfile (register and id), None = human. backend: auto | espeak | piper.
    Raises BackendUnavailable when the asked-for backend is missing, ValueError for IPA the table cannot map."""
    b = to_wav(render(ipa, profile, backend))
    if out_path is not None:
        Path(out_path).write_bytes(b)
    return b


@lru_cache(maxsize=1)
def _sample_tree():
    from planet.lineages import spec
    return spec.load(REPO / "planet" / "lineages" / "samples" / "dnd.toml")


def profile_for_people(people: str | None):
    """A lineage id -> VoiceProfile, resolved on the dnd sample tree (voice profiles are keyed by its ids); an id the tree
    lacks resolves on its own (its voice_profiles.toml table if any, else human)."""
    from . import profiles as PR
    if not people:
        return None
    tree = _sample_tree()
    if people in tree.lines:
        return PR.profile_for(tree, people)
    return PR.resolve_profile(people, lambda _l: [])
