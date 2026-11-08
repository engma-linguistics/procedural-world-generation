# For Daniel (set aside overnight, 2026-11-07 → 11-08)

Everything here has a working default in the code already. Nothing is blocked; change any of them in one place.

## Decisions (defaults taken)
1. **Synthesis level** (how affix-heavy languages are): the measurement against WALS 22A comes from grammar A. Default: unchanged until you rule.
2. **Species leanings in grammar** (like kenku → tone): the lane's guessed table, marked as guesses.
3. **Letters for non-human sounds** in book spellings (the purr vs trill rr): names lane's guess.
4. **Merger veto / homophony; spread of change rates between lects:** current settings kept.
5. **After a shift: how long minority speech lives, L2 share levels, how much dialect continuity:** current settings kept, with the reviews' numbers alongside.
6. **A shifting people keeps the old language's sounds, or reshapes them by its own voice:** current behaviour (keeps them) kept.

## Weirdness noticed
- **The demo page has glitches** (a full read before publishing found them). Merchants are glossed as things in two languages, a dual marker is described but missing from its example, one note quotes the wrong verb, and some agent jargon shows. None is in the data model's core. All are queued as the first item of grammar B in queue.md.
- See each lane's section below for more.

## Demos waiting
- **Languages demo page** (10 languages, 255 audio clips, complexity tab): https://claude.ai/artifact/GQUxhWHnErqn3zx7MTaFUs (private). Live viewer: `uv run python -m planet langserve a24559 --host 0.0.0.0 --port 8790`.

## Finish lane (lang-finish, 2026-11-07)

**Decisions taken by default**
- **Rounding harmony.** Only high vowels copy the root's rounding, as in Turkish (göz-ün, but göz-ler, not *göz-lör). A non-high vowel takes the root's backness. After an unrounded root it may lose its rounding, but it never gains it. Before this, a > ɒ made ɒ a living vowel in a fifth of all lects.
  - Change it in `planet/language/rules.py` `_produce` (the `first_vowel` branch).
- **New ways out of ɖ.**
  - S215: ɖ > ɽ between vowels (Hindi-Urdu ghoṛā).
  - S216: ɽ > ɾ (Eastern Bengali).
  - S217: ɖ > r at the start of a word (Romani rom < ḍomba).
  - These live in `tools/language/knowledge_tables.py`.
- **Non-human voices now feel ease drag from their own species' make costs.** Before, they had none, so u > y and l > ɫ ran unchecked in kenku, aarakocra, kobold and dragonborn lects. Their voice profiles do not favour y or ɫ.
  - The steepness is `EASE_K`, the same for every voice, in `planet/language/lect.py`.
- **u‼ is a non-human sound.** The two-voiced (harsh) u‼ is now treated as non-human, so the overuse check skips it.
- **p is left as it is.** It is rare across all lects because beaked and lipless mouths find labials dear: aarakocra labial cost 5, reptilian 4. Human lects have p in about 0.7 (PHOIBLE 0.85). I did not force it.
- **Measure for "Languages getting more and less complex".** I used `grammar.complexity`: bound functions + mean gram level + 4 × allomorphy share + 0.5 × bound class markers. It comes from the 0.5 kyr snapshots, joined through the parent chain.
  - The window is the last 0.5–3 kyr. A change of at least 1.0 points counts as "clear".
  - These are `CX_WINDOW` and `CX_CLEAR` in `tools/language/demo_page.py`.
- **Piper speech threads are capped at 8 by default.** Set `PIPER_THREADS` to change it.

**Your call when you are back**
- About 22% of word meanings share a form with another meaning on a 700-meaning list. Almost all of it is polysemy attested in CLICS. Is that acceptable? This is also in the inbox draft on realism leftovers.

**Odd output noticed**
- **Grams that are lost outright.** A whole function such as NEG, PAST or PL sometimes drops out with nothing to replace it. For example, the goliath lect d152 loses NEG about 1.5 kyr ago. Real languages renew negation rather than lose it. The hobgoblin lect d641 ends with a complexity score of 0.38, almost no grammar left. Worth a look: maybe loss should need a renewal path for the core functions.
- **One sentence set for all.** All 617 living lects get the same English sentences ("The woman sees the dog.", "My older brother catches three fish."). Only the tense sentence varies (build / carve). That is good for comparing lects, but dull to read through. A per-lect pick is easy if you prefer it.
- **A click spelt "|" in names.** Elvish click names such as "Pxeyag|he" broke the markdown tables in the sketches. They are now escaped in tables only. The romanization itself is unchanged.
- **The pass is not faster.** It still takes about 21 minutes. The file is much smaller: 36 MB main, 126 MB in three files, against 241 MB in one.

## Sound lane (lang-sound, 2026-11-08)

**Decisions taken by default**
- **Series-based inventory draw.** A proto first draws which series it has (labial-velar, prenasal, retroflex, aspirated, ejective, implosive, uvular, labialized, long vowels, nasal vowels and so on). Each series is drawn with PHOIBLE's share among inventories of the same size, so a 12-consonant language almost never has ejectives. Then about 3/4 of PHOIBLE's mean member count for that series is filled, and the free picks follow.
  - Table: `planet/language/data/phoible_series.tsv` (built by `tools/language/build_reference_tables.py`).
  - Knobs: `SERIES_FILL` 0.75, `SERIES_BOOST_MAX` 12, `SERIES_FLOOR` 0.002 in `planet/language/inventory.py`.
- **Tonemes.** A contour found only on long vowels counts as two level tones, not a toneme (`lect.tonemes`). Tone sets go up to 7.
- **Dragon sub-bass.** Dragon vowels can carry a sub-bass register. Its make cost is `sub_register = 0.5` for the chromatic and metallic dragon profiles in `planet/language/data/voice_profiles.toml`. Most dragon protos now have at least one sub-bass vowel (about 9 in 10 in proto draws). Raise the cost if you want it rarer.
- **Stress.** IPA in sketches and pages carries ˈ. Speech (`/api/speak?stress=`) puts the stress on the right syllable. Stress is the lect's pattern (initial, penult, final), not stored per word yet.
- **Sound-change catalogue** (a helper did this on my branch):
  - 14 of the 21 refused rows now parse. 7 stay refused with a reason: S106 haplology (needs two identical syllables), S132 and S133 suffix harmony (handled by the harmony machinery, not the catalogue), S170 and S172 (pitch accent and tone loss, which are not segment rewrites), S183 and S184 (analogy, which is not sound change).
  - `X` means any segment (long-distance dissimilation `r > l / _X*r`, Grassmann).
  - ATR harmony S134 is approximated on height (ɪ ʊ ɛ ɔ > i u e o in a word with i u e o). This is said in the row.
- **Line drift.** Each proto line draws a lognormal liking per rule family (σ 0.7) and per row (σ 1.0). Daughters keep it, with a small jitter at budding (σ 0.2). Named laws (Grimm, Verner, Grassmann, the Great Vowel Shift and similar) fire at most once per line. Other rows wait 4 kyr before re-firing (was 3).
  - Knobs: `LINE_FAMILY_SIGMA`, `LINE_ROW_SIGMA`, `LINE_BUD_SIGMA`, `ONE_OFF_IDS`, `ONE_OFF_MAX`, `REFIRE_KYR` in `planet/language/lect.py`. Chain shifts count half (`history.RULE_WEIGHT["family:chain_shift"]`).
  - Effect in the helper's harness: rows found in at least 80% of lects 45 → 19; Grimm fires in about a quarter of lines, the whole Great Vowel Shift in 29%.
- **Chain shifts are one staged event in drag order.** "a > b > c" now means a > b, then b > c. Grimm S177 (after sonorants too), High German S178, the Great Vowel Shift S179 (top down), Northern Cities S182.
- **New common rows S218-S225.** t > k; k > ʔ; ŋ > n; secondary palatalization before front vowels; aː > ɔː; ɪ ʊ > i u; t k > s before i; k > tʃ before a. S174 diphthongizes only in stressed open syllables.
- **The synchronic rule layer** (new `planet/language/phonology.py`; architecture.md 5b):
  - Each lect keeps an ordered list of live rules, inherited by daughters. Rules come from its allophones (phonetic level) and its conditioned sound changes.
  - A new sound change starts as a phrase-level rule. It narrows to the word level after `PHRASE_KYR` 1 kyr and to the stem level after `WORD_KYR` 3 kyr. This is Bermúdez-Otero's life cycle.
  - A rule dies when it is old (lognormal life around `LIFE_KYR` 6 kyr), when it is opaque (more than `OPAQUE_MAX` 20% of the words it should touch break it), or when it is crowded out (more than `MAX_LIVE` 8 rules).
  - 70% of tonal lines (`SANDHI_SHARE`) draw one tone-sandhi rule: Meeussen's rule, a Mandarin-type low-low rule, high spread, or contour simplification.
  - Rules apply to new words, derivations, compounds, loans and names (`inventory.realize`). In sentences they apply at morpheme joins (word level) and across word joins (phrase level).
  - Sketches have a "Phonological rules" section, and the viewer's time tab shows "Phonological rules today". Both use plain notation (e.g. "/t/ → [ɾ] / V_V") with a worked example from the lect's own words where one exists.

**Your call when you are back**
- **Rule death.** Is a 6 kyr median life and 8 live rules at most a sensible picture? Real languages keep some rules for very long (Celtic mutations, Sanskrit sandhi). I took the life-cycle reading: most rules end as stem-level or lexicalized.
- **Dragon sub-bass.** About 9 in 10 dragon lines have it. Should it be rarer, or a hallmark of every dragon tongue?

**Odd output noticed**
- **Two checks fail on a24559 with the sound lane** (pass D, `planet languages a24559` into scratch, never into runs/). Before this lane: the horizon at 10.7 kyr already failed, and the overuse check passed.
  - **Scholars' horizon (human lects): 12 kyr** (target 6-10; base 10.7). The rule rate is 11.2 per kyr against 14.6 at base. Line drift, the once-a-line named laws and the 4 kyr re-fire wait all mean fewer changes fire.
    - I raised `rules.PICK_REDRAWS` from 8 to 16. That took the horizon from 17 to 12.
    - `LANG_RATE_SCALE=7` alone only went from 17 to 13.5, so I left `RATE_SCALE` at 5.
    - The horizon is thinly resolved: 3-6 splits per bin past 10 kyr. It read 9, 11 and 13 on base code in earlier rounds.
  - **Overused segments: ɑ 26% (PHOIBLE 7%), lʲ 17% (2%), ɤ 13%, ä 12%, ɘ 10%.** The vowels come from the proto draw. With the series draw, a proto without a long-vowel or nasal-vowel series fills all its vowel slots with distinct qualities, so rarer qualities enter. In human proto draws ɑ is 0.18 against 0.10 on base code. History then spreads them through big families.
    - The fix I would try next: draw the vowel count after the vowel series, or let the free vowel picks take a long or nasal partner of a chosen quality even without the series, as PHOIBLE's counts include those.
    - lʲ is mostly one big family (16 living lects from proto p286) plus S221.
  - Fixed on the way:
    - prenasal stops: 43% of living lects → 27% (S142 weight 3 → 1);
    - tʷ and lʷ: no longer overused (S068 weight 2 → 1);
    - S221 (secondary palatalization) now fires before i only, at weight 1.
- **Five-tone systems are still the commonest** among tonal living lects (53%; base 85%). Protos are fine: tone counts 2-5 are 28/31/23/18%. History adds contour tones on short vowels (tonogenesis rows), and nothing merges tones back. This is "tone evolution", task 4, not done.
- **Line preferences are keyed by proto id** (`hiatus_key`), so two runs with the same proto ids share them. That is harmless within a run.
- **Paradigm cells don't run the live rules.** Grammar paradigm cells (`grammar.py`, grammar A's file) don't apply them yet. Only new coinages, derivations, compounds, loans, names (`realize`) and sentences do.
- **Viewer speech uses the selected lect's stress** pattern. Per-word stress is not stored.
