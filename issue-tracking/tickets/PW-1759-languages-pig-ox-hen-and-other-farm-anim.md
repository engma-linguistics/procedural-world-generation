---
id: PW-1759
title: "Languages: pig, ox, hen and other farm-animal words are gated only when the world stocks that animal"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: xs
impact: low
found_by: lang-lane20
blocked_by: []
relates: [PW-1745]
refs: ["planet/language/lexicon.py::_all_concepts", planet/language/history.py, planet/lineages/animal_defs.py, planet/lineages/animals.py, docs/review/language/for-daniel.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: lane 20 (PW-1745) gates animal words by wild range and herd spread for the animals the run stocks (meta.animals.stocks). Core-list words for farm animals the run does not stock (PIG, OX, HEN and the like, which come from the Concepticon lists, not animal_defs) stay proto words everywhere, so a world with no pigs still has a native 'pig' in every language. Gate them like wild fauna (by a wild-range proxy from animal_defs where one exists), or drop them from lexicons when the run lacks the animal.
- [ ] no lect has a native word for a farm animal its world never had

## Updates
- 2026-11-11: Created.
