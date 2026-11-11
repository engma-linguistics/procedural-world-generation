---
id: PW-1685
title: Place names are built from the founders' words as they are today, not as they were at the founding
type: task
status: todo
parent: PW-1736
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: coordinator (owner question, 2026-11-10)
blocked_by: []
relates: [PW-1658, PW-1654, PW-1656]
refs: ["run a24559", "planet/language/personal.py::Personal.founding", "planet/language/personal.py::Personal._founder_lect", "planet/language/personal.py::Personal.settlement", "planet/language/names.py::Names.inherits", tools/language/places_page.py, runs/a24559/languages-snapshots.json]
created: 2026-11-10
updated: 2026-11-11
---

## Description
In plain words: a town's native name really is built from its founders' words (Daniel's check: Keuyefigeu,
"Littlecombe", site 3782, is kɯjɛ- from human d561 SMALL kɯjɛijɯ + -fiɡɯ from VALLEY fiɡɯbɯ). But it is built from
those words as they are now, though the town was founded 8.7 kyr ago. A real 8,700-year-old name would have gone
through every sound change since and would usually no longer match the living words at all (Eoforwic > York).
Old names are too transparent. `founding` takes the Lect object alive at the founding, but a lect keeps one id
from birth to now and its lexicon is the final one; snapshots keep only the core 100 concepts.

Two smaller faults found with it:
- `Names.inherits` ignores time. Halflings of d375.2 shifted 1 kyr ago to a human language that split from d561 19 kyr
  ago (d604), before the founding, yet the name counts as their own inheritance and is never "heard" (adapted). 44 of
  1,430 settlements on a24559 are such cousins.
- places_page.py lists the name beside the holders' lect (d375.2) with no word that the founders' language, not the
  locals', gives the meaning; Daniel read it as the locals' words. Show "named by d561 (human), 8.7 kyr ago; today's
  locals would say ʒilar tital".

What breaks if never done: every old name is a transparent compound of living words, so maps lack the opaque,
worn-down names that make old lands feel old, and the page misleads about whose words they are.
- [ ] coin from the founder's forms at the founding (store the needed words at the founding, or run the lect's later
      rules over the coined form), so old names drift like any word
- [ ] inheritance checks the split date against the founding
- [ ] the places page says whose words the meaning comes from

## Updates
- 2026-11-10: Created from inbox draft draft-place-names-coined-from-todays-words.md (found by coordinator (owner question, 2026-11-10)).
- 2026-11-11: Moved under the language finish-line epic PW-1736 (assessment docs/review/language/assessment-2026-11-11.html; owner agreed 11-11).
- 2026-11-11: PW-1547 merged in (same mechanism: names coined at their own date and aged through each language's sound changes since; covers river, peak and old personal names too). Assessment: 232 of 233 own-line settlements read exactly as coined.
