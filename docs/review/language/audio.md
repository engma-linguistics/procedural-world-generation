# Hearing generated words: IPA to audio (audio lane, 2026-11-03)

Daniel wants to *hear* words of the generated languages. Their internal form is IPA, plus a few house percepts for
non-human voices (symbols.tsv `source` house / voqs / extipa): growl ‼, purr ᵣ, a second simultaneous voice ᴖ, sub-bass ˯
and ultra ˰ registers, and the percussives ʬ ʭ ʞ. This note covers what can turn raw IPA into sound offline on this machine
(Linux, no GPU, 48 cores, no sudo), what was built (`planet/language/speak.py`), and what it cannot do.

## In plain words

- Two engines now work. **Piper** (a small neural voice, about as fast as speech) is the default and sounds like a person.
  It is an English voice, though, so sounds English lacks are swapped for the nearest English sound (ʁ comes out as an
  English r, x as h, y as i). **eSpeak NG** is the always-there fallback: robotic, but it has more of the world's sounds
  built in (retroflexes, uvulars, χ, ɣ, ɬ, nasal vowels).
- Neither engine can make clicks or any of the non-human sounds. Those are added afterwards in numpy: a click or knock is
  synthesized and dropped over a short silence the engine leaves; growl, purr, the second voice, and tones are effects on
  that sound's slice of the recording.
- Sub-bass and ultra are, by definition, outside human hearing. What you hear is a stand-in: the sound an octave down plus
  a ~42 Hz rumble (sub), or an octave up plus a faint high whistle (ultra).
- Each people's voice profile sets pitch and speed: dragons about 9 semitones lower and 1.5 times slower, small folk higher
  and a little quicker. Peoples whose profile has the same register (human, elf) get a small fixed offset so they don't
  sound identical. That offset is voice colour, not a claim about them.

## Research: what turns raw IPA into speech today

| Option | IPA input? | Coverage (clicks / ejectives / tone / length / nasal V) | Install without sudo | Licence | Quality | Speed per word | Verdict |
|---|---|---|---|---|---|---|---|
| **eSpeak NG** (formant synth) | Phoneme mnemonics in `[[ ]]` (flag `espeakPHONEMES`) per voice's phoneme table, not raw IPA. Needs a mapping table. | No clicks in any table; ejectives only in `am`/`qu` tables; tones only in tone-language tables; length yes; nasal vowels in `hi`/`fr`/`pt` | **Yes**: the `espeakng-loader` wheel ships `libespeak-ng.so` + `espeak-ng-data` (no `espeak-ng` binary on this machine; not needed), called through ctypes | GPL-3 | Robotic but clear | ~1-20 ms | **Baseline** |
| **Piper TTS** (`piper-tts` 1.8.0, Sep 2026, OHF-Voice/piper1-gpl; VITS in ONNX) | **Yes, raw IPA characters**: a voice's `phoneme_id_map` is keyed by the IPA characters eSpeak emits; `PiperVoice.phonemes_to_ids(list_of_chars)` then `phoneme_ids_to_audio(ids, include_alignments=True)` bypasses text entirely. (`[[ ]]` raw-phoneme blocks in text also exist since 1.3.) | The id map has 154 symbols including ǀ ǁ ǂ ǃ ʘ ɓ ɗ ʄ ɠ ʛ ʔ ʕ ħ χ, nasalization, length, ʲ ʰ, but a voice only learned the ones its language's eSpeak output used. No tone input. | **Yes**: pip wheel (abi3, works on 3.14), bundles its own eSpeak; voices from HuggingFace `rhasspy/piper-voices` (~63 MB). Per-phoneme durations need `onnx` + `python -m piper.patch_voice_with_alignment`. | GPL-3 code; lessac voice is a public-domain-ish dataset (check the voice's MODEL_CARD before redistributing) | Natural (English-accented) | ~50 ms warm, 1.5 s cold load | **Higher-quality option, the default** |
| Meta MMS-TTS (VITS, 1,100+ languages) | Characters of each language's orthography (uroman for non-Latin scripts), one checkpoint per language | Only what a language's spelling encodes; no IPA path | pip `transformers` + torch (heavy) | **CC-BY-NC 4.0** | Good per language | ~0.2-1 s on CPU | Rejected: no IPA input, non-commercial |
| Coqui XTTS-v2 (idiap `coqui-tts` fork maintained) | Text only (BPE); no phoneme path for XTTS | 17 languages' spellings | pip + torch, ~2 GB | **CPML (non-commercial; Coqui shut down Jan 2024)** | Very good | ~1-3 s CPU | Rejected |
| Kokoro-82M (StyleTTS2) | Yes: misaki/espeak IPA phonemes, `[word](/ipa/)` overrides | Trained on English (and a few others): an English IPA subset; no clicks | pip `kokoro` + torch | Apache-2.0 weights; GPL phonemizer | Very good | ~0.1-0.3 s CPU | Viable later; same English-subset problem as Piper with more weight |
| Chatterbox, F5-TTS, Orpheus, Dia, Fish | Text (BPE / LLM tokens); no documented phoneme input (open_tts_tracker leaves the phoneme column blank) | n/a | torch, GBs | MIT / Apache; F5 weights CC-BY-NC | Very good | slow on CPU | Rejected: no IPA path |
| "Universal phone TTS" research (IPA-based cross-lingual TTS, 2021; zero-shot multilingual TTS, Saeki 2023) | Some IPA-conditioned | Research checkpoints, not packaged | n/a | varies | n/a | n/a | Nothing installable found in Nov 2026 |
| **ZIPA** (2025, ACL) | IPA *recognition* (speech -> IPA), 64M/300M models, permissive licence | n/a | k2/icefall stack | permissive | n/a | n/a | Not a synthesizer; the right round-trip checker later (see below) |
| Praat KlattGrid via `praat-parselmouth` | No: formant tracks by hand through `parselmouth.praat.call` | Anything you can describe acoustically | pip | GPL-3 | Klatt-robotic | fast | Fallback if we ever write our own IPA -> formant targets |
| Python Klatt (`tdklatt`, PyKlatt) | PyKlatt has IPA input but is Python 2; tdklatt is a single file, parameters only | as above | copy a file | MIT-ish | robotic | fast | Same as above |
| Pink Trombone (JS; `pink-trombone-mod` is MIT) | No: a tract-shape model you drive with tongue/lip positions | Species-agnostic by construction (tract length is a parameter) | npm, runs in the browser | MIT (mod) | Charming, vowel-ish, weak consonants | real time | A fun viewer toy for non-human tracts, not word rendering |
| VocalTractLab (`vocaltractlab` pip, alpha) | Gestural scores, segment-to-gesture API since VTL 2.3 | Human articulatory; best physical realism | pip (alpha, Linux .so) | GPL-3 | Best articulatory | slow | Too heavy for tonight; worth a look for a v2 "real tract" voice |

**Recommendation.** Baseline: eSpeak NG through `espeakng-loader` (guaranteed offline: a pip wheel, no system install, no
model download). Better: Piper with `en_US-lessac-medium`, fed IPA characters straight to its phoneme ids. Both are in.
`backend="auto"` uses Piper when its voice is on disk.

## What was built

- `planet/language/data/ipa_to_speech.tsv`: one table, one row per base symbol, modifier, prenasal prefix and separator,
  with an `espeak` column (mnemonics on the `hi` phoneme table: chosen because it has nasal vowels, aspirated and breathy
  stops, retroflexes, long vowels), a `piper` column (IPA characters the English voice was trained on), a `fit` grade
  (exact / near / sub / effect) and the post-processing `effect`. Every symbols.tsv row tokenizes through it (tested), and
  every Piper character is in the voice's id map (tested). One file rather than `ipa_to_<backend>.tsv` per backend, so a
  single tokenizer serves both.
- `planet/language/speak.py`: `speak(ipa, profile=None, out_path=None, backend="auto") -> bytes` (22.05 kHz mono 16-bit
  WAV). Tokenize -> backend renders plain segments and reports each segment's time span (eSpeak phoneme events aligned to
  our tokens with difflib; Piper's patched model returns samples per phoneme id) -> numpy effects per span -> profile
  register (resample: lower pitch and formants, longer) -> trim, cap at 1 s per word, normalize.
- `GET /api/speak?ipa=<url-encoded>&people=<lineage id>[&backend=auto|espeak|piper]` in `planet/server.py`: `audio/wav`,
  cached in memory by (ipa, people, backend), 512 entries; 400 for unmappable IPA, 503 when the backend is missing.
- `planet speak "<ipa>" [--people id] [--out file.wav] [--backend ...]` (run as `uv run python -m planet speak ...`).
- `tests/test_language_speak.py` (29 tests): table coverage, Piper id-map coverage, tokenizer effects and tones, valid WAV
  for a plain word and for every non-human symbol on both backends, dragon longer than human, the server route and its
  cache. Backend tests skip with the reason when the library or voice is missing.
- Samples in `docs/review/language/audio/`: `<people>.wav` (Piper) and `<people>_espeak.wav` for human "kalima", elf
  "elaːθiən", red_dragon "ɣaːrˤum˯", aarakocra "tsiʔᴖriːk", tabaxi "mᵣaːrin", lizardfolk "s‼aχɬa" (21-37 KB each).

### Setting up the Piper voice (data, not code; under the shared data root)

```
uv run python -c "from pathlib import Path; from piper.download_voices import download_voice; download_voice('en_US-lessac-medium', Path('data/language/tts/piper'))"
uv run python -m piper.patch_voice_with_alignment data/language/tts/piper/en_US-lessac-medium.onnx --output data/language/tts/piper/en_US-lessac-medium.align.onnx
cp data/language/tts/piper/en_US-lessac-medium.onnx.json data/language/tts/piper/en_US-lessac-medium.align.onnx.json
```

### Effects (numpy, on the segment's span with 8 ms crossfades)

| Symbol | Effect |
|---|---|
| tone letters ˥˦˧˨˩, diacritics ̋ ́ ̄ ̀ ̏ ̌ ̂ | pitch shift (resample + WSOLA, length kept): levels -6/-3/0/+3/+6 semitones; contours in 4 crossfaded steps |
| ‼ growl | 85 Hz amplitude modulation (depth 0.7) + band noise (80-3000 Hz) following the envelope |
| ᵣ purr | 28 Hz amplitude modulation + a 56 Hz rumble |
| ᴖ second source | the span plus a copy a fifth up (+7 st) |
| ˯ sub | octave down + 42/84 Hz rumble (stand-in: the real register is below ~20 Hz) |
| ˰ ultra | octave up + a faint warbling 7.5 kHz whistle (stand-in: the real register is above hearing) |
| clicks ʘ ǀ ǁ ǃ ǂ | backend renders a glottal closure; a synthesized burst (damped modes + band noise, per click type) goes on top |
| ʬ ʭ ʞ | as clicks: lip smack (450 Hz wet), teeth clack (4.8 kHz, 12 ms), beak clap (900/2300/3900 Hz hollow knock) |
| ̤ ̥ ̊ | breathy: band noise mixed in |
| ̰ | creaky: irregular 30-50 Hz pulsing |
| ʼ | stop + glottal stop, with a small sharp burst |
| implosives | plain voiced stop with a -2 st dip |

### What the baseline cannot render, and the substitutes

eSpeak (`hi` table): no clicks (closure + synthesized burst), no front rounded vowels (y ʏ -> i/ɪ; ø -> e; œ -> ɛ; hi's
`y` renders as silence), no ɯ ɤ ɘ ɵ ɞ ɶ (nearest of i u e o @ a), no ɢ ɴ (velar), no ʡ (ʔ), no ʕ ɰ (ɣ), no ɸ (f), no ʙ
(b + tap), no ɺ ɮ ʟ ɫ (l), ɹ ɻ as taps, no ejectives (stop + ʔ), no implosives (plain stop), no labial-velars (k-p
sequences), ɥ ʍ as j-w / h-w sequences, no pharyngealization or velarization (dropped), no tones (numpy pitch). Piper
(English voice) additionally swaps uvulars and velar fricatives (q -> k, x χ ç -> h, ɣ -> ɡ, ʁ ʀ -> ɹ), retroflexes to
alveolars, ʂ ʐ ɕ ʑ to ʃ ʒ, palatal stops to tʲ dʲ, trills to a flap; the per-row choices are in the table.

## Benchmark (5 words, this machine, warm; cold load in brackets)

| Word | eSpeak | Piper |
|---|---|---|
| kalima | 1 ms | 49 ms |
| ɣaːrˤum˯ | 2 ms | 45 ms |
| tsiʔᴖriːk | 1 ms | 51 ms |
| mᵣaːrin | 1 ms | 52 ms |
| s‼aχɬa | 22 ms | 74 ms |
| cold start | (0.02 s) | (1.5 s, model load) |

No listening was possible, and neither backend has a recognizer, so no round-trip test. Checks done instead, on the
sample files: the spectrograms show clean harmonic vowels and formant movement for both backends; the human Piper voice
(lessac, a female speaker) sits near 190 Hz and eSpeak's default near 100 Hz; red_dragon has 16% of its energy below
100 Hz (human: under 0.1%) and harmonics spaced ~110 Hz in its vowel; tabaxi's purred m shows a 27 Hz modulation peak
(target 28); the eSpeak lizardfolk growl span peaks near 100 Hz modulation (target 85, blurred by the noise); durations
human 0.48 s vs dragon 0.68 s (Piper). Ear verdict deferred to Daniel: expect Piper to sound like a fluent English speaker
reading a foreign word, and eSpeak like a 1990s screen reader that gets more of the consonants right.

A real round trip would run the WAV through ZIPA (speech -> IPA) and compare with the input by percept distance; ZIPA's
k2/icefall stack was too heavy for tonight.

## Sources

Opened or read tonight:
- piper-tts on PyPI (1.8.0, Sep 2026, GPL-3, abi3 wheels): https://pypi.org/project/piper-tts/
- piper1-gpl docs and release notes (raw `[[ ]]` phonemes; `synthesize` takes `SynthesisConfig`, `synthesize_raw` removed):
  https://raw.githubusercontent.com/OHF-Voice/piper1-gpl/main/docs/CLI.md, https://github.com/OHF-Voice/piper1-gpl/releases
- The installed `piper/voice.py` (`phonemes_to_ids`, `phoneme_ids_to_audio(include_alignments=True)`),
  `piper/patch_voice_with_alignment.py`, and the lessac voice's `phoneme_id_map` (154 symbols) - read locally.
- espeakng-loader on PyPI (bundles the library and data; `get_library_path`, `get_data_path`):
  https://pypi.org/project/espeakng-loader/
- eSpeak NG `phontab` parsed locally (134 phoneme tables; per-table inventories) and every mapped mnemonic checked by
  phoneme trace on the `hi` voice.
- MMS-TTS (VITS per language, uroman, CC-BY-NC-4.0): https://huggingface.co/docs/transformers/model_doc/mms
- XTTS-v2 model card (CPML): https://huggingface.co/coqui/XTTS-v2
- open_tts_tracker (per-model phoneme alphabet and licences): https://huggingface.co/datasets/Pendrokar/open_tts_tracker
- Kokoro on PyPI (misaki G2P, IPA overrides): https://pypi.org/project/kokoro/
- ZIPA (Zhu et al. 2025, multilingual phone recognition): https://arxiv.org/abs/2505.23170
- Parselmouth KlattGrid via `praat.call`: https://groups.google.com/g/parselmouth/c/iI5ly3B2uu0 ; Praat manual
  https://www.fon.hum.uva.nl/praat/manual/Create_KlattGrid_from_vowel___.html
- tdklatt: https://github.com/guestdaniel/tdklatt ; PyKlatt: https://code.google.com/p/pyklatt/
- pink-trombone-mod (MIT): https://www.npmjs.com/package/pink-trombone-mod
- VocalTractLab Python (alpha): https://pypi.org/project/vocaltractlab/0.5.8/
- Saeki et al. 2023, zero-shot multilingual TTS: https://arxiv.org/pdf/2301.12596.pdf

[memory], not re-opened: Chatterbox / F5-TTS / Orpheus / Dia input formats beyond the tracker's blank phoneme column.
