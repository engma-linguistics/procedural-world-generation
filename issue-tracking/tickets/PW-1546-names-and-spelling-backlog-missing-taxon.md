---
id: PW-1546
title: "Names and spelling backlog: missing taxonomy patterns (X9, P1, P3, P5-P7), spelling traditions per family, name length by tradition, landmass and dish names"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: l
impact: med
found_by: lang-design (names & spelling lane, 2026-11-08)
blocked_by: []
relates: [PW-972, PW-1436, PW-984]
refs: [docs/review/language/names-spelling-gaps.md, docs/review/language/architecture.md, docs/review/language/for-daniel.md, planet/language/names.py, planet/language/personal.py, planet/language/romanize.py, planet/language/data/romanization.tsv, planet/names.py]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: the names lane did the items needed before the merge (pattern codes matching Daniel's taxonomy doc,
one spelling per sound per language, personal and town names). What is left is new capability: the name-change
processes from the taxonomy that never fire, a "look" per language family (Polish *sz* vs English *sh*), and names
that fit their tradition in length. Without it, all languages share one house spelling, so unrelated languages look
alike on the page, and peoples never pick up a conqueror's or a neighbour's name for themselves.

Open items from names-spelling-gaps.md §7 (numbers are its ranks):
- [ ] 15: X9 misattributed origin, P1 conquerors' name (from `shifts` with a ruler deme), P3/E12 adopted exonym,
  P5 renaming, P6 ethnonym > word, P7 split by borrowing; find why X4 relay never fires (no `borrowed_from` in a24559).
  (E11 and X6 wait for polities: see the polities draft.)
- [ ] 12: orthographic profiles per family (digraphs vs diacritics, ʃ as sh/sz/š/x, length doubled or macron), drawn at
  the proto and inherited, with reforms. Romanization only; keep clear of Daniel's writing-systems repo.
- [ ] 13: orthographic depth: freeze book spelling at a standardisation date (a polity founding), *knight*-type letters
- [ ] 14: name length by tradition (`names.MAX_SYLL` into the tradition: Malagasy-long, Chinese-short)
- [ ] 16: glossonym drift ('our speech', a place, a manner adverb)
- [ ] 18: landmass names from the first settlers' language (Daniel's own names, PW-867, still win)
- [ ] 19: scholars' names with more bases (type site, *Bantu*-type, *Indo-European*-type, *Proto-*)
- [ ] 20: dish and food names (eponyms, toponyms, exonyms for foreign dishes along food routes; PW-692)
- [ ] bilabial click ʘ still spelled `px`; a Bantu c q x click option

## Updates
- 2026-11-08: Created from inbox draft draft-language-names-backlog.md (found by lang-design (names & spelling lane, 2026-11-08)).
