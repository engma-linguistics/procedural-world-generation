# Two voices: second-voice tone for syrinx-voiced peoples (syrinx lane, 2026-11-08)

Daniel asked for realistic handling of what a syrinx can do: the two sides are independent sound sources, so a bird can
sound two unrelated pitches, and two pitch contours, at once. Before this lane the second voice (`source2`, ᴖ) was one
binary feature, rendered as a copy of the vowel a perfect fifth up: it always moved in parallel with the first voice.
This note is the diagnosis and design, then the implementation and the measurements.

## 1. What a syrinx does (the physics we model)

- **Two independent sources.** The songbird syrinx sits where the trachea splits into the two bronchi; each side has its
  own pair of labia, its own muscles and its own nerve branch, so each side can vibrate, stay silent, or vibrate at its own
  fundamental (F0). Greenewalt (1968, *Bird Song: Acoustics and Physiology*) inferred the "two-voice" theory from
  spectrograms; Suthers (1990, Nature 347: 473) confirmed it by measuring airflow through each bronchus separately.
  [Greenewalt from memory; Suthers 1990 title confirmed by search.]
- **Two pitches and two contours at once.** In brown thrashers and grey catbirds the overlapping sounds of the two sides are
  seldom harmonically related; the result is "two-voice" syllables with audible difference tones (Suthers, Goller & Hartley
  1994, J Neurobiol 25, "Motor dynamics of song production by mimic thrushes": abstract via search). One side can hold a
  level note while the other sweeps, or the two can sweep in opposite directions; the wood thrush's terminal trill is the
  textbook example of an internal duet [memory].
- **Ranges.** Across most species studied the left side makes the lower frequencies and the right side the higher. The
  northern cardinal's down-sweep from ~6-7 kHz to ~2 kHz starts on the right side and hands over to the left at about
  3.5-4 kHz, mid-syllable, without an audible seam (Suthers & Goller; summarized by Cornell's Bird Academy and the
  "Lateralization of bird song" survey, via search). The mockingbird is an exception (left side higher during two-voice
  syllables; Zollinger & Suthers 2004 [search snippet]). So: each voice has its own range, the ranges overlap partly, and
  switching sides is fast (milliseconds).
- **Shared constraints.**
  - Both sides are driven by one air-sac pressure (one breath), so loudness and duration are largely shared: two voices
    start and stop together on a syllable, and a breath group bounds both.
  - Both pass through one vocal tract. Birds tune the tract to the fundamental (Riede et al. 2006, PNAS, "Songbirds tune
    their vocal tract to the fundamental frequency of their song": the oropharyngeal-esophageal cavity tracks F0;
    Nowicki 1987 on tract resonance, helium experiments [memory]). The filter can track one fundamental, not two: the
    second voice is filtered "wrongly" and is the weaker, purer-sounding line. That is why the vowel quality (the tract
    shape) belongs to the syllable and only the pitch is doubled.
  - Interval choice: hermit thrushes favour harmonic-series intervals between successive notes (Doolittle et al. 2014,
    PNAS) [memory]; the thrasher/catbird data say simultaneous voices need not be harmonic. We take no harmonic constraint.

## 2. How far a language would use it (design)

A spoken language does not use everything a singer can. The fantasy-plausible use is a **second tone tier**: the second
voice carries its own tone category, drawn from the same small vocabulary of tones the first voice uses (level high, mid,
low; rising; falling). Relations between the two (parallel, contrary, oblique motion) then fall out of the pair:

| first voice | second voice | written | heard as |
|---|---|---|---|
| high level | high level | a˦ᴖ˦ | parallel (the old default: the second line a fifth above) |
| high level | rising | a˦ᴖ˨˦ | oblique: one holds while the other climbs |
| rising | falling | a˨˦ᴖ˦˨ | contrary: the lines cross |
| low | high | a˨ᴖ˦ | a wide interval held |

- **Its own staff.** Second-voice tone letters are read on the second voice's own staff, which sits about a fifth above
  the first voice's (each side has its own range). So a˦ᴖ˦ is not a unison: it is the two voices each at the top of their
  own range, a fifth apart. This keeps the letters meaning "high/low/rising" for each voice, as a speaker would think of
  them, rather than absolute pitch.
- **A small set.** A language draws a 2-4 member second-voice tone set (`inventory.TONE2_SETS`): {high, low} (the commonest,
  like simple tone systems), {level, rising, falling} (contour-based: what birds do best, sweeps), or {high, low, rising,
  falling}. Not every combination of first and second tone is a word of the language, as not every C x V is.
- **Not every second-voice lect has it.** A lect with second-voice vowels has a second-voice tone contrast with probability
  `inventory.TONE2_SHARE` (0.5) x hear/make terms, else its second voice moves in parallel, as before.
- **A segmental tier.** Where the first voice's tone is a tier over every syllable (`inv.tones`), the second voice's tone
  rides only on second-voice vowels, so it is stored on the vowel (`Segment.tone2`), as nasality or the second voice
  itself are. The inventory lists iᴖ˦ and iᴖ˨ as two vowels. That makes the syllable space (Nettle's S, `lexicon._space`,
  vowels x tones) multiply by itself: no change to the word-length code was needed.

### Markedness and cost
- Make cost: a new percept key `tone2` (`profiles.PERCEPT_KEYS`), inf for humans (as `source2`), 1.0 for the avian stem
  (pitch control is a bird's strength: the avian `tone` cost is already 0.7). A toned second-voice vowel costs its vowel x
  the source2 multiplier x the tone2 multiplier.
- Hearing: `hear.tone2` (avian 1.0; human 0.3, the same faint resolution as `source2`): humans hear the second voice as
  timbre and barely hear its contour.

### How it arises (tonogenesis analogues; rules.py demo rules, family "tone")
1. **A lost coda consonant leaves its pitch on the second voice**: Vᴖ + ʔ# > Vᴖ˨˦ (rising) and Vᴖ + h# > Vᴖ˦˨ (falling), the
   Vietnamese pathway (Haudricourt 1954) with the second voice, not the first, taking up the perturbation. Why the second
   voice: in a lect where the first voice already carries tone, the free tier is the second one.
2. **Onset voicing splits the second voice**: Vᴖ after a voiced obstruent > Vᴖ˨, after a voiceless one > Vᴖ˦, then the
   voicing contrast is lost (the Middle Chinese yin/yang split on the second tier).
3. Both only touch a second-voice vowel with no second-voice tone yet (`tone2=0`), and they phonemicize only through the
   same hygiene as first-voice tone (`lect.voice2_hygiene`: under 2 distinct second-voice tones, or under
   `TONE_MIN_MARKED` of the core list's second-voice vowels marked, the marks are stripped; otherwise every second-voice
   vowel takes the commonest second-voice tone).

### How it is lost
- **Contour levelling** (as S227/S228): a rising or falling second voice levels to high (`tone2.contour_level`).
- **Merger onto parallel motion**: the second voice stops moving on its own (`tone2.parallel`: Vᴖ˦ > Vᴖ; the commonest way
  out, a whole category merging).
- **Merger onto one voice**: the second voice is lost (`voice2.loss`: Vᴖ > V). Before this lane no change removed a second
  voice at all; only the inventory cap could.
- **Contact**: humans and other one-voiced listeners hear the second voice faintly (0.3), so loans into their languages
  lose it entirely (nearest inventory vowel); a bird lect without the second-voice tone contrast hears a toned second voice
  as its plain second-voice vowel.

### Perception and borrowing
`percepts.distance` gives `tone2` the same pitch-pair distance as `tone`, weighted by the listener's `hear.tone2`. A loan
passes through `profiles.hear_word` to the nearest segment of the listener's inventory, so:
- bird to bird with a tone2 contrast: the nearest second-voice tone is kept;
- bird to bird without: the plain second voice (parallel);
- bird to human, dwarf, dragon...: the plain vowel (no second voice in their inventory). Nothing in a human lect changes.

### Notation
IPA-like and readable, as Daniel suggested: the second voice's tone letters follow ᴖ.
`a˦ᴖ˨˦` = first voice high level, second voice rising. `aᴖ` = second voice in parallel (no tone of its own).
`percepts.from_ipa` reads tone letters after ᴖ as the second voice's; `to_ipa` writes tone letters, ᴖ, second-voice tone
letters, register, in that order; the two round-trip (tests).

### Spelling (house romanization)
The second voice stays ‹wh›; its tone is the same diacritic the first voice uses, on the ‹w›: high ẃ, low ẁ, rising w̌,
falling ŵ (mid unmarked, as for the first voice). So a˦ᴖ˨˦ is ‹áw̌h›, aᴖ˨ is ‹aẁh›. Book mode drops tone marks as it does
for the first voice: ‹awh›.

### Audio
`speak.py` reads tone letters after ᴖ as the second voice's contour. The second voice is a copy of the untoned vowel
shifted to the second staff (+7 semitones) plus its own contour in 6 crossfaded steps, with a slight 6 Hz vibrato (+-0.25
semitone) so the ear separates it as its own stream (common onset, separate pitch motion: what makes two lines, Bregman
1990 on auditory streams [memory]). A second voice with no tone of its own still follows the first voice a fifth up.

## 3. Implementation map
- `percepts.py`: `Segment.tone2`, parse/write order, distance, `tone2` natural class.
- `profiles.py`: key `tone2` (cost, hearing), `_nonhuman_core`.
- `inventory.py`: `TONE2_SHARE`, `TONE2_SETS`, the draw; `epenthetic_vowel` no longer picks a marked (second-voice,
  register, growl, purr) vowel when a plain one exists (Iulahad's recurring u˨ᴖ epenthesis was this).
- `lect.py`: `voice2_hygiene` beside `tone_hygiene`.
- `rules.py`: ᴖ and second-voice tone letters in rule notation; demo rules for genesis and loss.
- `romanize.py`, `speak.py`, `data/voice_profiles.toml`, `checks.py` (diagnostic: share of syrinx lects with a second-voice
  tone contrast).

## 4. Measurements
(filled after pass A; see below)

## 5. Decisions for Daniel
(see below)
