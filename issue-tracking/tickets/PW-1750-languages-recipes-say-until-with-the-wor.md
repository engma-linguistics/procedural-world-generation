---
id: PW-1750
title: "Languages: recipes say 'until' with the word for 'when' (the core list has no UNTIL or THEN)"
type: task
status: todo
parent: PW-1736
milestone: null
subsystem: culture
effort: s
impact: low
found_by: lang-lane19
blocked_by: []
relates: [PW-1739]
refs: ["planet/language/texts.py::recipe", "planet/language/texts.py::UNTIL", planet/language/lexicon.py, docs/review/language/for-daniel.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: lane 19 gave recipes "First, ... Then ... until it is soft". The concept list has no UNTIL and no THEN,
so 'then' is said with the lect's word for AFTER and 'until' with its word for WHEN (texts.py UNTIL, SEQ_*). A linguist
reading the interlinear sees `until` glossed on the word for 'when': plausible (many languages build 'until' from 'when',
'boundary' or 'reach'), but it is a stand-in, and every lect makes the same choice.

What breaks if never done: the recipe gloss line claims a word for 'until' that the lexicon does not have; nothing else.

Fix (lexicon lane, lane 20's files): add UNTIL as a grammaticalising concept (from REACH, WHEN or BOUNDARY, by lect), or a
converb gram, and let texts.recipe use it when present.
- [ ] UNTIL (and THEN, if wanted) in the concept list with per-lect sources
- [ ] texts.recipe uses them, the WHEN fallback only where missing

## Updates
- 2026-11-11: Created from inbox draft draft-language-until-then-concepts.md (found by lang-lane19).
- 2026-11-11: Lane 20 adds THEN and UNTIL as function-word concepts (commit 9a960503, merging); close when lane 20 is in main.
