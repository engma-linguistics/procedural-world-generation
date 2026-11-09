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
- **Not every second-voice lect has it.** A proto with second-voice vowels gets a second-voice tone set with probability
  `inventory.TONE2_SHARE` (0.5) x hear.tone2 / make_cost.tone2 (1 for the avian stem), else its second voice moves in
  parallel, as before; later lects can gain one by sound change.
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
2. **A phrase-final rise frozen onto the second voice** (`tone2.final_rise`, weight 1): the last syllable's second voice
   rises, as boundary prosody became lexical pitch accent in Swedish; later apocope makes it unpredictable. (An onset-voicing
   split onto the second voice was considered and left out: it needs the voicing contrast lost lect-wide, a large change
   to pin on the rarer tier.)
3. All of these touch only a second-voice vowel with no tone of its own yet (`tone2=0`), and they phonemicize only through
   `lect.voice2_hygiene`: parallel motion counts as a category, so the contrast stands with two or more categories over the
   lexicon's second-voice vowels and marks on at least `TONE2_MIN_MARKED` (10%) of them; otherwise the marks are stripped.

### How it is lost
- **Contour levelling** (as S227/S228): a rising or falling second voice levels to high (`tone2.contour_level`, weight 1,
  below S227's 3: the duration argument for levelling short contours, Zhang 2002, is weak for a voice that sweeps in tens
  of milliseconds).
- **Merger onto parallel motion**: the second voice stops moving on its own (`tone2.parallel`: Vᴖ˦ > Vᴖ; the commonest way
  out, a whole category merging).
- **Merger onto one voice**: the second voice is lost in unstressed syllables, word by word (`voice2.loss`, diffusing).
  Before this lane no change removed a second voice at all; only the inventory cap could. (Written for every second-voice
  vowel at once, it fired in 23 lines of pass A and left 1 living lect of 52 with a second voice.)
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
- `lect.py`: `voice2_hygiene` beside `tone_hygiene` (counts the whole lexicon: second-voice vowels are rare); the inventory
  cap's units set the second voice's tone aside as they set the first's (pass C: 30 new second-voice tones folded back as
  "rare new units" right after a coda rule made them, a gate the first voice's tone never met).
- `rules.py`: ᴖ and second-voice tone letters in rule notation (Vᴖ˨˦; `[V source2=1 tone2=0]`); seven demo rules
  `tone2.*` / `voice2.loss` (demo rules rather than tsv rows, as the first voice's coda tonogenesis is: they need a focus
  plus a lost coda, which the tsv's single-change rows do not write; the knowledge-table generator is untouched).
- `romanize.py`, `speak.py` (`second_voice`), `data/voice_profiles.toml`, `checks.py` (`second_voice`: no one-voiced lect
  has a second voice; shares of syrinx lects with a second voice and with its own tone, shown), `tools/language/sketch.py`
  (the demo's tonal-bird pick prefers a lect with second-voice tones), `demo_page.py` legend.

## 4. Measurements

Run a24559, `planet languages --workers 8` to scratch (never into runs/). Baseline = runs/a24559/languages.json (main
before this lane), read-only. Four passes: A (first design), B (voice2.loss weak syllables only), C (contour levelling
weight 1), D (cap units set tone2 aside) = the committed code. Numbers below are pass D unless named.

### Checks
All pass except "scholars' horizon (human lects)", which fails on the baseline too (human 10.67 kyr in both). The new check
"second voice only where there is a syrinx" passes: 0 one-voiced lects with ᴖ. Pass A once tipped "loans follow
borrowability" (pronoun loans 0.088 vs cap 0.08; baseline 0.076, B 0.077, C 0.070, D 0.076): run-to-run noise in human lects.

### Shares (living lects; 25 aarakocra + 27 kenku = 52)

| | baseline | pass A | pass B | pass C | pass D |
|---|---|---|---|---|---|
| with a second voice | 22 | 1 | 17 | 18 | 16 |
| with second-voice tone contrast | (none possible) | 0 | 4 | 2 | **8** (6 aarakocra, 2 kenku) |
| categories (parallel counted) | - | - | 2,2,2,2 | 2,2 | 3,3,3,2,2,2,2,2 |

Pass D: 15% of syrinx lects (24% of aarakocra, 7% of kenku), half of the lects that kept a second voice. The kenku share
is lower because fewer kenku lects keep a second voice at all (5 of 27; baseline 10).

### Tone-bearing units (vowel phonemes x first-voice tones), living syrinx lects, pass D

| group | lects | vowel phonemes | tone-bearing units (mean / median) |
|---|---|---|---|
| second-voice tone | 8 | 12.8 | 35.0 / 34.5 |
| second voice, parallel only | 8 | 10.2 | 25.2 / 22 |
| no second voice | 36 | 8.4 | 17.1 / 15 |
| baseline, second voice (all parallel) | 22 | 11.4 | 25.6 / 21 |
| baseline, no second voice | 30 | 7.6 | 14.2 / 13 |

### Word length ("that complexity might also create shorter words, no?")

Yes, mechanically, and it is automatic: `lexicon._space` counts vowels x tones, and iᴖ˨˦, iᴖ˦ are vowels of their own,
so the syllable space grows with no change to the word-length code. But the effect is small, because only one to three
vowel qualities of a proto carry a second voice:

- Controlled (same 130 aarakocra protos, drawn with second-voice tone vs the same inventories flattened to parallel):
  syllable space median 3,120 -> 4,000 (+28%), vowel phonemes 10 -> 13, `length_scale` 0.970 -> 0.949: roots
  **about 2% shorter**. If every vowel could carry a second voice with three tones, the space would be about four times
  larger and roots about 10% shorter (estimate from LENGTH_EXP = 0.7 at ln sigma ~ 8).
- In the run the differences are larger but confounded (8 lects, different histories, and the run's chaos moves the bird
  means by 0.1-0.4 syllables between passes):

| group | mean syllables/word | mean segments/word |
|---|---|---|
| pass D, second-voice tone (8) | 1.95 | 4.15 |
| pass D, second voice, parallel (8) | 1.76 | 4.11 |
| pass D, no second voice (36) | 2.13 | 4.38 |
| pass D, all aarakocra / kenku | 2.07 / 2.02 | 4.40 / 4.20 |
| baseline, all aarakocra / kenku | 2.03 / 2.38 | 4.28 / 4.61 |
| baseline, second voice (22) / none (30) | 2.18 / 2.23 | 4.36 / 4.52 |
| pass D, all other lects (564) | 2.12 | 4.36 |

So: lects with a second voice have somewhat shorter words than one-voiced bird lects in pass D (about 0.2-0.4 syllables),
in the predicted direction, but the controlled number says most of that gap is not the syllable space; second-voice tone
adds about 2%.

### Example words (pass D, aarakocra 34, the north of Sothasor, lect d726; first-voice tones low, high, rising)

| gloss | IPA | house spelling | the two voices |
|---|---|---|---|
| egg | i˦ᴖ˨˦ | íw̌h | first high and level, second rising (oblique) |
| stone, rock | o˨˦ᴖ˦˨ | ǒŵh | first rising, second falling (contrary: the lines cross) |
| new | nu˨˦ᴖ˨˦ | nǔw̌h | both rising (parallel contours on two staffs) |
| mud | e˨ᴖ˨˦ | èw̌h | first low, second rising |
| be alive | se˦ᴖ | séwh | first high, second in parallel (no tone of its own) |
| forehead | k͡pi˨jndi˦ᴖ˦˨ru˨˦ | kpìyndíŵhrrǔ | a second voice falling in the middle syllable |

(egg i˦ᴖ˨˦ and call i˨˦ᴖ are a near pair: the same vowel, the rise on the other voice.) Iulahad (d292, the lect Daniel
named) now has three second-voice categories too: parallel, high, rising (iᴖ˦, iᴖ˨˦, oᴖ˦ ...). Its recurring epenthetic
u˨ᴖ came from `epenthetic_vowel` taking the rarest high vowel, which was a second-voice one; fixed.

### Audio demo
`tools/language/demo_page.py` on pass D (all languages; it has no people filter; its tonal-bird pick now prefers a lect
with second-voice tones): /tmp/claude-1000/-data-personal-repos-procedural-world-generation/78e89d74-f837-4b74-a7da-25a178d37d96/scratchpad/syrinx/syrinx-demo.html
(scratch, tmpfs: 10 languages, 488 Piper clips). Its tonal bird language is Iulahad (d292: 3 first-voice tones and a
second voice in parallel, high or rising); a kenku language (d135) is also on it.


## 5. Decisions for Daniel

Each is implemented as the recommended default; say if you want another.

1. **How often a second voice gets its own tone.** At the proto draw, half of the second-voice protos (`TONE2_SHARE`
   0.5); after 20 kyr, 8 of 52 living bird lects (15%; half of those that kept a second voice). Recommended: keep. Raise it
   if you want second-voice tone to be a hallmark of bird speech rather than one feature among many.
2. **The second voice's staff.** Its tone letters are read on its own staff, a fifth above the first voice's: a˦ᴖ˦ is two
   high notes a fifth apart, not a unison. Recommended: keep (each side of a syrinx has its own range, and it keeps
   "high/low/rising" meaning the same for both voices). The alternative, one shared pitch scale, would make a˦ᴖ˦ a unison,
   which a listener cannot hear as two voices.
3. **Parallel motion is a category.** A second voice with no tone of its own (aᴖ) counts as one of the second-voice
   tones (the unmarked one), so a single coda change can start a contrast (aᴖ vs aᴖ˨˦), and a language need not mark every
   second-voice vowel. Recommended: keep. The stricter reading (every second-voice vowel must carry a tone once there is a
   contrast, as every syllable does for the first voice) would make second-voice tone rarer and harder to start.
4. **Spelling.** The second voice's tone is the first voice's tone mark on the w of wh: áw̌h, ǒŵh; book mode drops both,
   as it drops first-voice tone (awh). Recommended: keep. Alternative: digits or a second letter (awh2, awhr), uglier.
5. **Fantasy sound changes.** The coda pathways onto the second voice, the frozen final rise and the ways out are
   analogues, not attested changes (no human language has a second voice). Their weights (3, 3, 1; losses 1, 2, 1, 1) are
   judgement. Recommended: keep and judge by ear and by the shares above.
6. **The second voice is stored on the vowel, not as a tier.** iᴖ˦ and iᴖ˨ are listed as two vowels (as a nasal vowel is),
   so bird inventories with second-voice tone list 12-13 vowels. The first voice's tones stay a tier (listed apart). This is
   what made the word-length effect automatic. Recommended: keep; the inventory display could list them as "iᴖ with ˦ ˨˦"
   later if the long lists bother you.
