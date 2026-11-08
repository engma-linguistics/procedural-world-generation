---
title: "Decisions: language defaults to confirm, part 2 of 3: words, contact, faiths and names"
type: task
status: needs-decision
parent: PW-767
subsystem: culture
effort: s
impact: med
found_by: lang-design (core, lexicon & contact, faiths, names, polish lanes, 2026-11-07/08)
blocked_by: []
relates: [PW-982, PW-984, PW-1308]
refs: [docs/review/language/for-daniel.md, docs/review/language/calibration.md, docs/review/language/lexicon-gaps.md, docs/review/language/contact-gaps.md, docs/review/language/names-spelling-gaps.md, planet/language/lexicon.py, planet/language/lexicon.py::core_repair, planet/language/lexsys.py, planet/language/history.py, planet/language/inputs.py, planet/language/faiths.py, planet/language/faiths.py::Plan, planet/language/names.py, planet/language/personal.py, "run a24559"]
---

## Description
In plain words: the lanes that built vocabulary, borrowing, kinship, gods and names picked many rates and tables by
judgement while Daniel was away. They all work and each sits in one place. This ticket lists them for a yes or a change.
If it is never done, guesses about how fast words are borrowed, how gods are named and how long minority speech lives
become the design without a linguist having looked at them.

Numbers are from full scratch passes of run a24559 on 11-08 (`for-daniel.md`: Finish lane, Lexicon & contact lane,
Pass 2, Faiths & contact pass 3, Names & spelling lane, Polish lane).

**Real calls**
- A. **Polysemy.** With 712 meanings per lect, about 22% of meanings share a form with another (median); almost all of
  it CLICS-attested (NOW/TODAY, POT/BOWL), accidental homophones under 1%, the core 100 at 0.12. Acceptable? If too
  much: lower the shift draw weight for WOLD meanings (`lexicon.SHIFT_GAP` and shift weights) or have shifts vacate the
  source. Lean: accept.
- B. **Gods get a sex from kin titles** ('sky-father', 'earth-mother'), drawn 50/50; gods.json has no sex
  (`faiths.KIN_TITLES`). Options: keep; drop kin titles; or wait for gods.json to carry sex. Lean: keep.
- C. **When a liturgy freezes.** At the faith's first temples, so liturgies in a24559 are up to ~6.6 kyr old (Latin,
  Sanskrit, Ge'ez are 1.5-4 kyr). Freezing at writing would make them younger, but the techtree has no usable writing
  step yet (PW-1512). Lean: keep until writing exists, then switch.
- D. **After a shift** (contact-gaps 8-10): how long minority speech lives (`history.SHIFT_DECAY` 0.01, `SHIFT_AT`
  0.5, no tipping-point speed-up), the adult-L2 levels (`inputs.L2_SHARED` 0.6, `L2_MAX` 0.7, median L2 share 0.53),
  and how much dialect continuity at deme grain is wanted (same-language neighbours now drift into separate
  languages fast). Lean: keep for now; dialect continua are in the contact backlog draft.
- E. **Segment borrowing is frequent.** 205 of 618 living lects carry a borrowed-segment log, 142 at the cap of 4;
  266 of 697 borrowed consonants survive today (`lexicon.SEG_BORROW_MIN` 0.5, `SEG_BORROW_K` 0.15,
  `SEG_BORROW_MAX` 4). The areal inventory signal barely moved (-0.004 -> +0.003). Lean: halve `SEG_BORROW_K`.
- F. **Town names are mostly substrate**: about two thirds of a24559's towns were founded by another people, so most
  names are older people's names. Follows the settlement history; Daniel to say if it reads too high.

**Confirm or change**
| default | value | where |
| --- | --- | --- |
| Fresh root (word of unknown origin) when nothing can renew a frequent meaning; Swadesh rate held by compensation 1.0 | `KEEP_COIN` 1.0, `KEEP_COIN_FREQ` 2, `KEEP_COMPENSATION` 1.0 | `lexicon.py` |
| Loans vs contact: steepness of the WOLD borrowability curve | `LOAN_CONTACT` 0.1, `LOAN_MAX` 1.0, gamma 1.5 -> 0.5 | `history.py`, `lexicon.py` |
| Pronoun/numeral/question-word merges repaired the next step (plural before singular, 3rd before 1st) rather than vetoed | on | `lexicon.core_repair`, `repair` rows in `data/derivations.tsv` |
| Numeral systems inside grammar's "other" label | 60% restricted / 40% five-based; restricted -> five-based above 20,000 speakers | `lexsys.py` |
| Proto colour stage weights and split rate (by eye, not the World Color Survey) | `STAGE_WEIGHTS`, `COLOUR_SPLIT` 0.0008 | `lexsys.py` |
| Kinship system pulled by marriage rules (Murdock read, not fitted) | `KIN_PULL`, `KIN_PULL_MAX` 3 | `lexsys.py` |
| Name taboos speed word loss (Dixon, no rate given) | +30% dead-soundalike, +20% ruler's name | `lexsys.SPEECH_TABOO_X` |
| Avoidance register: 20 everyday meanings, half neighbour's words; today only, not inherited | `AVOID_CONCEPTS`, `AVOID_LOAN` 0.5 | `lexsys.py` |
| Areal feature copying x10 | `AREAL_K` 0.015 | `history.py` |
| Shift substrate: 10-30% of local words kept, accent replaces 80% of missing sounds | `ACCENT_P` 0.8 | `history.py` |
| Four gods named per culture | `GODS_PER_CULTURE` 4 | `faiths.py` |
| God-name half-life against an epithet ('the lord') | `NAME_HALF_KYR` 12 (6-15 defensible) | `faiths.py` |
| Learned loans from the liturgy | `LEARNED_RATE` 0.0025 / generation / sacred meaning | `faiths.py` |
| Unrelated peoples sharing a faith from the start name its gods independently (calques, not loans) | on | `faiths.Plan` |
| Petition gifts per god domain (sea gives fish, sky rain ...) | `GIFT` | `faiths.py` |
| A god name may sound like a grammatical marker (Moow) | not vetoed | `faiths.coin_name` |
| Naming traditions: dithematic 50 / sentence 25 / one-word 25; bynames patronymic 35 / clan 30 / epithet 25 / matronymic 10; 12% drift | | `personal.py` |
| Old names coined ~4 kyr back; wear to two syllables up to 60% | `OLD_NAME_KYR`, `OPAQUE_CAP` 0.6, `OPAQUE_KYR` 8 | `personal.py` |
| Towns: 3 per deme; generic worn to one syllable after 3 kyr; newcomers add their own generic 25% | `SUFFIX_KYR`, `SUBSTRATE_TAUTOLOGY` 0.25 | `personal.py` |
| E10 faith ethnonyms rare | `FAITH_W` (0.15, 0.6) | `names.py` |
| Pattern-code mapping to Daniel's taxonomy (first settlers -> E2, totem -> E9, 'the many' -> E11, cave/sea people -> X7, scholars' name `scholarly`, relay X4) | | `names.py` |
| Two lexicon test bounds moved (homophone max 0.24 -> 0.25; derivation margin 0.05 -> 0.04; coinage bound 6% -> 8%) | | `tests/test_language_lexicon.py` |

- [ ] Daniel answers A-F
- [ ] Daniel confirms or changes the table rows (silence = keep)
