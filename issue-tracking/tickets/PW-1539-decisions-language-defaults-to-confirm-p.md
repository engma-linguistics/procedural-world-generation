---
id: PW-1539
title: "Decisions: language defaults to confirm, part 1 of 3: sounds, sound change and spelling"
type: task
status: needs-decision
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lang-design (finish, sound, names lanes, 2026-11-07/08)
blocked_by: []
relates: [PW-982, PW-1423]
refs: [docs/review/language/for-daniel.md, docs/review/language/calibration.md, docs/review/language/phonology-gaps.md, docs/review/language/soundchange-gaps.md, docs/review/language/names-spelling-gaps.md, planet/language/phonology.py, "planet/language/rules.py::_produce", planet/language/rules.py, planet/language/lect.py, planet/language/inventory.py, planet/language/history.py, planet/language/romanize.py, planet/language/data/sound_changes.tsv, planet/language/data/voice_profiles.toml, planet/language/data/phoible_series.tsv, tools/language/knowledge_tables.py, "run a24559"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: while Daniel was away the language lanes had to pick many settings for how languages sound, how they
change and how they are spelled. Each pick works and is in the code as one constant or table. This ticket lists them so
Daniel can say "fine" or "change X to Y" in one sitting. If it is never done, these guesses quietly become the design,
and a few of them (marked **call**) shape what every language page looks like.

Numbers are from full scratch passes of run a24559 (the fantasy D&D run) on 11-08; the source sections are in
`docs/review/language/for-daniel.md` (Finish lane, Sound lane, Sound lane pass 2, Names & spelling lane).

**Real calls (the lane had no evidence to settle them)**
- A. **Live phonological rules die young.** A live rule has a median life of 6 kyr and a lect keeps at most 8
  (`phonology.LIFE_KYR`, `MAX_LIVE`, `OPAQUE_MAX` 0.2). Real languages keep some rules far longer (Celtic mutations,
  Sanskrit sandhi). Options: (a) keep, the Bermúdez-Otero life-cycle reading; (b) a long-tail life (lognormal sigma up)
  so a few rules last 15+ kyr. Lean: (b), cheap.
- B. **Dragon sub-bass in about 9 of 10 dragon lines** (`sub_register = 0.5` in `data/voice_profiles.toml`). Hallmark
  of every dragon tongue, or rarer (cost 1.0-1.5)? Lean: keep as a hallmark.
- C. **S221 (palatalization before i) at weight 0.4**, so whole palatalized series are rare (lʲ fell 17% -> 3% of living
  lects, PHOIBLE 2%). The alternative counts a palatalized consonant found only before i as an allophone. Lean: keep.
- D. **A people that shifts language keeps the old language's sounds** (a fire-giant lect descended from bronze-dragon
  speech keeps no labials and a growled a). Option: run the new speakers' `profiles.hear_word` over the lexicon at the
  shift so the language takes on their accent (phonology-gaps rec. 16). The accent already replaces 80% of missing
  sounds (`history.ACCENT_P` 0.8) but only for words the shift brings in. Lean: nativise, partially.
- E. **Merger veto and rate spread.** A sound change that would merge busy contrasts is vetoed with probability
  1 - exp(-15 x load) (`rules.FL_K` 15); lects differ in rate by lognormal sigma 0.3 (`lect.RATE_SIGMA`). The review
  suggested sigma about 0.6 plus a burst after a shift or founder split, so some lines change fast (a Hawaiian-type
  collapse). Lean: keep FL_K, try sigma 0.5 with the horizon check watched.

**Confirm or change (one constant each)**
| default | value | where |
| --- | --- | --- |
| Rounding harmony copies rounding onto high vowels only (Turkish type) | on | `rules._produce`, `first_vowel` branch |
| Backness harmony: front e going back opens to ɑ (-ler/-lar) | on | `rules._produce` |
| Harmony never coins a vowel the lect lacks; nearest vowel or neutral | on | `rules.harmony_onto`, `HARMONY_SNAP_MAX` |
| Exits from ɖ: S215 ɖ > ɽ / V_V, S216 ɽ > ɾ, S217 ɖ > r word-initially | rows | `tools/language/knowledge_tables.py` |
| S226 labialized coronals lose labialization (no attested case checked) | row | `data/sound_changes.tsv` |
| Non-human voices feel ease drag from their own species costs | `EASE_K` 0.5 for all | `lect.py` |
| p left rare in beaked and lipless mouths (aarakocra, reptilian); humans p 0.77 vs PHOIBLE 0.85 | not forced | `data/voice_profiles.toml` |
| Series-first inventory draw | `SERIES_FILL` 0.75, `SERIES_BOOST_MAX` 12, `SERIES_FLOOR` 0.002 | `inventory.py` |
| Tone sets up to 7; a contour only on long vowels counts as two level tones | | `lect.tonemes` |
| Line drift: per-family and per-row liking, inherited | sigma 0.7 / 1.0 / 0.2 at budding | `lect.LINE_FAMILY_SIGMA`, `LINE_ROW_SIGMA`, `LINE_BUD_SIGMA` |
| Named laws (Grimm, Verner, GVS) fire at most once per line; other rows wait | `REFIRE_KYR` 4 | `lect.ONE_OFF_IDS`, `ONE_OFF_MAX` |
| Chain shifts count half in the rule rate | 0.5 | `history.RULE_WEIGHT["family:chain_shift"]` |
| New sound changes start phrase-level, then word, then stem | 1 kyr / 3 kyr | `phonology.PHRASE_KYR`, `WORD_KYR` |
| Tonal lines with one tone-sandhi rule | 70% | `phonology.SANDHI_SHARE` |
| Prenasal-stop source S142 weight 3 -> 1; S068 weight 2 -> 1 | | `data/sound_changes.tsv` |
| Book letters for non-human sounds: purr `vr`, growl `rh`, second voice `wh`, sub-bass `mh`, ultra `ih` | | `romanize.NH_MARKS` |
| Book spelling keeps 2 diacritic letters per language, folds the rest | 2 | `romanize.BOOK_DIACRITIC_BUDGET` |
| Dental beside alveolar written t̮ d̮ n̮ l̮ (workbench only) | | `romanize._DENTAL` |
| Small vowel shifts written plain unless they contrast | | `romanize._SHIFT_MARK` |
| Pinyin b/p only where there are no voiced stops | | `romanize.py` |
| Clicks as ǀ ǁ ǃ ǂ, no Bantu c q x option; bilabial ʘ still `px` | | `romanize.py`, `data/romanization.tsv` |
| In-word letter guard is a middle dot (irh·ll); null/none/undefined re-spelled | | `romanize.BOOK_GUARD`, `RESERVED_SPELLINGS` |

- [ ] Daniel answers A-E
- [ ] Daniel confirms or changes the table rows (silence = keep)

## Updates
- 2026-11-08: Created from inbox draft draft-language-defaults-sounds-spelling.md (found by lang-design (finish, sound, names lanes, 2026-11-07/08)).
