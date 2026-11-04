# Languages from scratch: the overnight demo (lane report, 2026-11-04)

Branch `lang-design`, worktree `.claude/worktrees/lang-design`. Run **a24559** (dnd preset, world dba204). Everything below is
committed on the branch; nothing is merged. The viewer is `viewer/languages.html` (a "Languages" link sits in the peoples
workbench header). Start the server from the worktree (`uv run python -m planet serve`, or on another port if yours is
up) and pick a24559.

## Rule on these first

1. **The horizon target.** An automatic comparative method on the output goes blind at @@HORIZON@@ kyr; the design said 6-10.
   Speeding the engine up to hit 6-10 makes sister dialects that split 2 kyr ago fall below "recognisably related". The
   lane's lean: widen the target to 6-13 and keep sisters recognisable, because the blind measure (100 words, edit distance
   plus recurrence) is more generous than a real comparative method with real data. Draft:
   `issue-tracking/inbox/draft-language-rates-and-horizon.md` (needs-decision). Details in §6 and `calibration.md`.
2. **Per-generation scaling at exponent 1** (your ruling) does what it says: aarakocra (5.8-year generations) change
   about five times faster per year than humans, kobolds (11.7) twice; aarakocra sister lects 5 kyr apart share almost no
   core roots, and their own horizon is 2-3 kyr. Elves (145-year generations) look like ~3 kyr of human change over 20 kyr;
   dragons (430) keep 85-88% of their proto core words. Keep it, or soften it (0.7) for the very-short-generation peoples?
   Numbers in §7.
3. **Voice profiles.** `docs/review/language/voice-profiles.md` holds the drafted numbers and the sources per species. Three
   choices you may want to overturn: humans can make harsh (growled) voice at a high cost (contrastive in !Xóõ and Bai)
   rather than never; birds keep a larynx (a valve, no phonation) and voice with the syrinx, so voicing rules apply to them;
   tortles hear front vowels poorly. Dragons' sub-bass register is dropped by every human-eared listener, as designed.
4. **Rivers are named by the people with the most heads on them** (square-root weighted), so dragons name a river now and
   then rather than most of them (they covered most cells at 20 kyr). Your call if you want more draconic hydronyms.
5. **Romanization for the book** is a lossy "book mode" (tones dropped, nasal vowels as plain vowel + n, one diacritic per
   word, ü/ö only where a lect contrasts them); the workbench shows the full spelling beside it. Uvulars: q, qh, ġ (ʁ, DIN
   31635), gq, nq. Endonyms came out like *Mïzhekheema* 'the real people' (humans), *Ïthe'ee* 'the river people' (kobolds).

## What works and what doesn't

@@VERDICT@@

## 1. What was built (PW-1423 and PW-986, and most of PW-982)

`planet/language/` (14 modules, ~12k lines, 500+ tests, all not-slow):

| Layer | Module | What it does |
| --- | --- | --- |
| Sounds as heard | `percepts.py`, `data/symbols.tsv` | one percept space for every species (place, manner, voicing, larynx, phonation incl. harsh and purr, secondary, vowel height/back/round/nasal, length, tone, second source, register); 274 symbols: IPA, extIPA, VoQS and a few house symbols; injective rendering |
| Voice profiles (PW-1423) | `profiles.py`, `data/voice_profiles.toml`, `spec.py::voice` | make cost per percept class, hear resolution per axis, articulators, modality; inherited key by key along the lineage tree like `body`; human default from PHOIBLE frequencies; nativization = hear a word through a profile and an inventory |
| Inventories | `inventory.py` | PHOIBLE-weighted draws with feature economy and vowel dispersion, scaled by the species' make costs; sonority-sequenced syllable shapes; repair |
| Sound change | `rules.py`, `data/sound_changes.tsv` | 28 hand-written demo rules plus 150 parsed from the catalogue, each with its cause (coarticulation, effort, perception, prosody, tonogenesis, dispersion) and needs (articulators or hear axes); a species keeps the rules it can cause; Wedel-style functional-load veto; regular vs diffusing |
| Words | `lexicon.py`, `data/concepts.tsv`, `data/clics_edges.tsv` | ~330 concepts (Leipzig-Jakarta, Swadesh, food from the run's crops and animals, landscape, kin, numbers, god domains); frequency-dependent replacement (Pagel 2007 shape, 86%/kyr Swadesh retention at human generations); derivation, compounding along CLICS edges, colexification shifts, borrowing, taboo, substrate; every word carries its etymology |
| Grammar | `grammar.py`, `data/grambank_*.tsv`, `data/wals_wordorder.tsv`, `data/grammaticalization_paths.tsv` | 39 typology features drawn with their correlations and drifting at stability-class rates; grams recruited along Heine-Kuteva paths and moving free > clitic > affix > fused > lost; sound change runs on inflected exemplar cells so alternations arise; analogy levels; complexity measured, never stored; L2 share, population and isolation push the rates |
| The driver | `history.py`, `lect.py`, `inputs.py` | one lect per deme; proto-languages per connected component of same-people demes in contact at 20 kyr; budding copies; wave spread of fired rules over the contact record weighted by contact and prestige; language shift on elite rule, swamping, city mixing and trade, with substrate words, an accent and calqued features; food words borrowed hop by hop along the crop and animal spread; city koine; batched per 0.5-kyr frame, never per generation |
| Families | `families.py`, `checks.py` | true lect tree with shift edges; blind cognate shares; language clustering; the scholars' UPGMA tree and the horizon; the six checks |
| Names (PW-972) | `names.py` | endonym patterns E1-E12 and exonyms X1-X9 from the owner's taxonomy, built through each lect's grammar (class markers, compound order, locatives); relayed exonyms mangled hop by hop; hydronyms kept as substrate across shifts; the Common and its exonyms; scholars' names for dead families |
| Output | `output.py`, `run.py` | `runs/<id>/languages.json`; `planet languages RUN [--out] [--workers]`; a guarded hook in `output.save`; a placeholder export for the writing repo |
| Romanization | `romanize.py`, `data/romanization.tsv` | the house spelling (full and book modes) |
| Audio | `speak.py`, `data/ipa_to_speech.tsv`, `/api/speak`, `planet speak` | IPA to WAV: eSpeak NG baseline, Piper fed raw IPA; growl, purr, second voice, sub-bass and ultra registers and percussives as numpy effects; the voice profile sets pitch and pace. Samples in `docs/review/language/audio/`; research in `audio.md` |
| Viewer | `viewer/languages.html`, `viewer/lang*.js` | six tabs, below |
| Brief | `brief.py` | a "Names and words" section per people (headword, glossonym, exonyms, three etymologies, food words with routes) |

Reference data (`planet/language/data/`, sources and licences in `reference-data.md`): PHOIBLE 2.0+ (CC-BY-SA), Grambank 1.0.3,
WALS, CLICS3, Concepticon lists (Leipzig-Jakarta, Swadesh, Pagel 2007 rates, Holman). The sound-change and grammaticalization
tables are written from knowledge, not downloaded, and say so in their headers.

## 2. The viewer

Screenshots in `docs/review/language/screens/`.

- **Families**: the true lect tree on a 20-kyr axis (bud solid, shift dashed, arrival dotted, coloured by people) beside the
  scholars' tree, with the 6-10 kyr band and the measured horizon. `lang-families.png`
- **A language over time**: pick a lect, scrub 20 kyr: the consonant grid and vowel trapezoid animate (sounds that came flash
  green, sounds that went are struck out), the core words change in IPA and spelling, the grams sit on their ladder, the
  typology line, complexity over time, the change log with causes. Play buttons on words. `lang-time.png`, `lang-time-now.png`
- **Continuum and intelligibility**: a map of living lects with contact edges coloured by intelligibility at the scrubbed
  frame (green > 0.7, amber, red < 0.4), chain cards ("the middle understands both neighbours, the two ends do not"), when
  a chain broke, and a who-understands-whom heatmap. `lang-continuum.png`, `lang-continuum-chain.png`
- **Names and etymologies**: endonym, glossonym, the land/people/person/language set, exonyms by whom and why, each with its
  etymology chain; deme place and river names; what the Common calls them; scholars' names. `lang-names.png`
- **Food words and shifts**: each route hop by hop with the form at each hop; each shift case with trigger, substrate and
  accent. `lang-routes.png`, `lang-shifts.png`
- **Checks and voices**: the checks table and a voice card per species. `lang-checks.png`

Load is ~2 s for the 140 MB file; every tab draws under 0.2 s; scrubbing is 5-15 ms a frame.

## 3. Sample proto-inventories next to PHOIBLE

@@INVENTORIES@@

## 4. Cognates, etymologies, a food word's route, a shift, paradigms

@@SAMPLES@@

## 5. Sound change over time in one lect

@@CHANGELOG@@

## 6. The checks, as measured

@@CHECKS@@

## 7. Species

@@SPECIES@@

## 8. What is still wrong (honest list)

@@DEFECTS@@

## 9. Judgement calls the lane made (beyond the five above)

- **Proto-languages at 20 kyr**: one per connected component of same-people demes in contact at the start frame
  (320 components on a24559), so continua start as continua; isolated demes get their own; arrivals (elves, gnomes, tritons)
  get a fresh proto-language at their first deme because `demes.json` gives them a wrong deme parent.
- **One lect per deme, always**; a "language" is a cluster of lects measured afterwards (blind cognate share > 0.7).
- **Shift triggers** are derived, not stored: incursions located through `demes_all`, settlement holder changes aggregated
  per ruler/ruled deme, mixed cities, long trade contact. Elite rule needs the ruler to out-prestige the ruled (population,
  cities, writing, law); the other way round is swamping. A deme may shift only to a different language and not within
  3 kyr of its last shift.
- **Rates are calibrated by the horizon check**, with the tension described above. Final constants in `calibration.md`.
- **Inventories are capped** at 1.5x the proto count (45 consonants, 20 vowel qualities); rules that would add a new
  segment are drawn at 0.3 weight; a rule fires at most twice in a lect's life and not twice within 3 kyr.
- **Only nouns compound**; verbs replace by derivation, shift or a fresh root. Compounds take a head from the concept's own
  domain and a modifier from a CLICS neighbour.
- **The check "proto inventories vs PHOIBLE"** was redefined: medians inside PHOIBLE's interquartile range and 35-75% of
  protos inside it on each measure, since a PHOIBLE-like draw puts half of them inside by definition.
- **Hydrids, templates and overlays** (half-elves, tieflings, genasi, aasimar) have no demes in the run, so no lects.
- **Writing hand-off**: `output.export_writing` gives IPA, morpheme breaks and glosses per word; nothing about scripts.

## 10. Tickets

Updates for the coordinator to put on the board after merging:

- **PW-1423** (done for the demo): percept space, profile schema in the lineage spec (`voice`, inherited like `body`),
  human profile from PHOIBLE, inheritance tested, the demo runs on it, non-human profiles drafted with sources
  (`voice-profiles.md`) for Daniel to react to. Open: the variant-share draft (`draft-language-nonhuman-variant-share.md`).
- **PW-986** (the demo stands; the owner rules): all slice items built; checks 5 of 6 pass; the horizon check and the rates
  need the ruling above; the brief section renders but `brief.build` crashes on a24559 on current code before reaching it
  (the stored tree no longer parses under PW-1275: "tortle: density and band_km2 are no longer given"), so the brief could
  only be checked on a synthetic run - a main-branch issue, not the lane's.
- **PW-982**: the full catalogue (178 rules after dedup), the lexicon processes and the grammar ladder are in; what is
  left of it is quality (the defects list) rather than scope.
- **PW-972**: name stacks filled with word forms; 6% of exonym rows are plain 'foreigners' (the bar was a third).
- **PW-984**: food routes are in the output and the brief (172 routes on a24559); the donor-form issue in §8.
- **PW-985**: sociolinguistic pressure acts on the gram rates; the "hubs simpler, isolated richer" check passes on this run.
- **Drafts** (3): `draft-language-rates-and-horizon.md` (needs-decision), `draft-languages-json-size-and-cost.md`,
  `draft-language-nonhuman-variant-share.md`. Folded into this write-up instead of drafts: the two knowledge tables deserve a
  spot-check of their examples (`reference-data.md` lists the doubtful rows); koine has fired only on synthetic data;
  `brief.build` on a24559.

## 11. How to run it

- `uv run python -m planet languages a24559 --out DIR --workers 12` (15 min; writes `DIR/a24559/languages.json`); without
  `--out` it writes into the run and adds `meta.languages` to run.json.
- `uv run python -m planet speak "kalima" --people human --out k.wav`
- Tests: `uv run pytest -q tests/test_language_*.py tests/test_languages_viewer.py` (@@TESTS@@).
