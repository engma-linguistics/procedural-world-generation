---
id: PW-1547
title: River names, old personal names and peak names should age through each language's own sound changes, as god names already do
type: task
status: wontdo
parent: PW-767
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lang-design (names & spelling lane, faiths & contact pass 3, 2026-11-08)
blocked_by: []
relates: [PW-972, PW-1436]
refs: [docs/review/language/names-spelling-gaps.md, docs/review/language/architecture.md, docs/review/language/for-daniel.md, planet/language/names.py, planet/language/personal.py, "planet/language/faiths.py::coin_name", planet/language/lexicon.py, planet/language/history.py, "run a24559"]
created: 2026-11-08
updated: 2026-11-11
---

## Description
In plain words: real place and personal names are old words worn down by the language's sound changes: *Wilhelm* from
'will + helmet', *Avon* from a word for river. God names in the generator already work this way (they are lexicon
words that go through every sound change). River names, old personal names and peak names do not: they are made from
today's words at output time, with an approximation for age. So a river name never shows the language's own history,
sister languages do not share old names in regularly different shapes, and the "name history" a reader looks for in
the workbench is missing.

**Now.**
- God names: `name:god:<key>` lexicon entries with part of speech NAME (faiths pass 3), inherited, carried through shift,
  borrowed by converts. This is the pattern to copy.
- Old personal names: coined ~4 kyr back from the lect's reflexes of their themes, a replaced theme stays as a fossil,
  wear to two syllables up to 60% (`personal.OLD_NAME_KYR`, `OPAQUE_CAP`), but not replayed through the lect's own
  rules (names-spelling-gaps rec. 9, marked partial).
- River and lake names: substrate tautologies exist ('Avon river' type); the name itself is not aged. Peaks get no
  tautologies (no substrate path).

**Wanted.**
- [ ] `name:river:<id>` (and old given-name themes) injected into lexicons at their coining time, as for gods, so they
  go through sound change, inheritance, shift and borrowing
- [ ] peak names with a substrate path and tautologies ('Pendle Hill')
- [ ] the workbench shows a name's history (coined as X 'meaning' at t, now Y)
- [ ] sister lects show cognate names in regularly different shapes (spot-check two families)

## Updates
- 2026-11-09: Language wrap-up 11-09: realism polish, parked as later (owner: language good enough to move forward).
- 2026-11-08: Created from inbox draft draft-language-names-through-sound-history.md (found by lang-design (names & spelling lane, faiths & contact pass 3, 2026-11-08)).
- 2026-11-11: Merged into PW-1685 (same mechanism), per the 11-11 assessment.
