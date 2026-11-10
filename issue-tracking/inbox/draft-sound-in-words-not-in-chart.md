---
title: "Language pages: 5 of 620 languages use a consonant in a word or two that their sound chart does not list"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: s
impact: low
found_by: lang-lane11
blocked_by: []
relates: [PW-1548]
refs: ["planet/language/inventory.py::observed", "planet/language/history.py::generate", "planet/language/history.py::offense_pass", "planet/language/lexsys.py::avoidance", "planet/language/faiths.py::learned_register", "planet/language/output.py::lect_json", "tools/language/sketch.py::vowel_chart", "tools/language/demo_page.py", "run a24559"]
---

## Description
In plain words: PW-1548 listed a dwarf vowel ä seen in words but missing from the vowel chart. On a24559 (stored,
lane 10) no language has a vowel in its words that its chart lacks, so that slip is gone. But 5 of the 620 living
languages have one consonant in one or two words that their chart (the inventory in languages.json) does not list:
d479 (halflings) /v/ in 'beak' and 'hunt'; d785 (humans) /tʃ/ in 'wall'; d269 (hobgoblins) /h/ in 'carve' and
'medicine'; d294 (kenku) /tʃ/; d151.2 (dragonborn) /k/. If never done, a reader of those languages' pages sees a
sound in the words that the sound chart says the language does not have, which reads as a bug.

Likely cause, not yet confirmed: a word that came in after the inventory was last observed (a loan in the last
interval, or one of the after-the-history steps: the avoidance register, the offence renewals, the late god names),
so the inventory never took the sound in. Check with the etymologies in languages-etym.json; then either re-observe the
inventory once after `offense_pass` in `history.generate`, or have the pages list "sounds only in loans" under the
chart.

- [ ] no living lect on a24559 has a segment in its lexicon that its inventory (and allophones) lacks, or the page
  says which sounds occur only in loans
