---
title: "Language lane rulings: sisters vs horizon (one rate, two checks), per-generation exponent for short-lived peoples, felt vs etymological word families"
type: task
status: done
parent: PW-767
subsystem: culture
effort: s
impact: med
found_by: lang-design (rounds of 2026-11-04)
blocked_by: []
relates: [PW-986, PW-982, PW-1423]
refs: [planet/language/history.py::RATE_SCALE, planet/language/lect.py::resolve_hiatus, planet/language/families.py::horizon_read, planet/language/checks.py, planet/language/lexicon.py::felt_roots, planet/language/lexicon.py::refresh_roots, planet/language/output.py::EtymTable.note_roots, tools/language/sketch.py, docs/review/language/calibration.md, docs/review/language/demo.md, "scratchpad hiatusI/sis.py (two-sister harness)", "scratchpad compJ/family.py", "run a24559 (runs/a24559/languages.json)"]
---

## Description
In plain words: three judgement calls are left from the language rounds. Each changes what the language pages show.
They are Daniel's to make, and the lane's lean is given for each.

Already ruled (Daniel, 11-04), so it is not reopened here: horizon target 6-10 kyr for humans, longer for long-lived
peoples; two low windows in a row; strictness and the sisters bar are the lane's call (strict share, bar 0.5).

**1. Sisters vs horizon.** On the shipped run (all rounds of 11-04, run a24559), sisters split under 2 kyr ago share
0.494 of their core words by the strict measure (bar 0.5; it was 0.502 before the hiatus round). The human horizon is
12.0 kyr (target 6-10; it was 10.5). Word families and the hiatus repairs moved the two checks in opposite directions.
The single overall rate (`history.RATE_SCALE`) cannot fix both: a lower rate helps sisters but lengthens the horizon,
and a higher rate does the reverse. The hiatus repairs cost about 0.01-0.02 strict share in the two-sister harness, with
one repair per change after 8+ new hiatus junctions. Further tweaks were within the harness noise of about 0.01.
- A: accept both as they are and report them (0.494 is within noise of the bar).
- B: lower the sisters bar to 0.45 and look for a horizon lever that doesn't change young sisters, such as faster
  replacement of non-core words only.
- C: retune the rate against both checks together. This is likely to fail one of them.
- Lean: A for now and B later. Real sister languages around 1-2 kyr apart (Spanish/Portuguese, Swedish/Danish) are
  well over half cognate, so 0.49 reads as real. The 12 kyr horizon comes from shared word families keeping old
  sisters recognisable.

**2. Generation exponent.** Daniel ruled exponent 1 on 11-03, so change is per generation. Kobolds (11.7-yr
generations) change about twice as fast per year as humans, and a third of their living lects keep no proto core word
after 20 kyr. Aarakocra now have 18.6-yr generations (adult 12, lifespan 60, like kenku). Keep exponent 1 for everyone,
or soften it below human generation length (rate x (28 / generation) ** 0.7)? Lean: keep 1. Fast-churning kobold
tongues are a fair fantasy result.

**3. Felt vs etymological word families.** A word's `roots` now list only the roots a speaker still feels: a
derivation or compound younger than 3 kyr whose parts are still in use. So 'egg' no longer sits under 'tree', but
living languages show small families: 9 families of 3+ words, the largest 5 words, 25% of words in a family. Before,
it was 32 families, the largest 15 words, 62%. Most proto derivations are older than 3 kyr.
- A: felt roots only (now).
- B: also store the historian's families as a second per-word field, `etym_roots`, set when the word is made and
  carried forward (the PIE-style *bher- 'carry' > burden view), with the pages showing both. This adds about 5 MB.
- C: a longer opacity (6-10 kyr) for roots only.
- Lean: B. A linguist reader wants both the speaker's view and the reconstruction view.

## Rulings (Daniel, 2026-11-07)
Final run numbers at the time of ruling: sisters strict share 0.499 (bar 0.5), human horizon 10.7 kyr (target 6-10).
1. **A: accept both** as within noise. No rate retune.
2. **Soften below human generation length**: rate x (28 / generation) ** 0.7 for generations shorter than 28 years;
   per-generation (exponent 1) at and above it.
3. **B: store both** felt `roots` and historian's `etym_roots`; pages show both.

Next round (all chosen): shift polysemy guard (brother = sister, I = we) and tone re-phonemicisation; diminutive
overuse together with coinage share; overused segments (sound check over all lects, attested exits for ɹ ʁ ɫ ɦ);
languages.json size and pass speed; larger vocabulary, more grammar per language, sample utterances; first-class
audio in the UI (utterances, not only single words).

- [x] rulings recorded
- [x] generation softening and `etym_roots` in the pass (round 5 core lane, commit eec089ac; per-word `etym_roots`
  beside `roots` in lexicon entries, the doc `roots` table covers both)
- [x] the pages show both families (demo page `families(..., "etym_roots")`, viewer `langmore.js` rootView)

All three rulings are carried out; this draft is a record. Intake can file it as done or reject it as recorded in
`docs/review/language/for-daniel.md` and calibration.md.
