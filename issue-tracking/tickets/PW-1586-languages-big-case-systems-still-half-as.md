---
id: PW-1586
title: "Languages: big case systems still half as common as WALS 49A after the case catalogue grew (6+ cases 16% vs 32%)"
type: task
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: low
found_by: language lane 4 (PW-1569)
blocked_by: []
relates: [PW-1569]
refs: ["planet/language/grammar.py (PULL_GROUP", LOCAL_FORM, CASE_MANY), "scratch pass lane4/pass2", docs/review/language/calibration.md]
created: 2026-11-09
updated: 2026-11-09
---

## Description

In plain words: after lane 4 added the local cases ('in, into, out of, on, onto, off') and three more, languages with
six or more cases rose from 3.5% to 16% of living languages in a24559, and 8 or more from 0% to 5%. Real languages
(WALS 49A, 261 languages): 32% have six or more, 18% eight or more. The middle band is still too full (2-4 cases 40%
against WALS's ~16%).

If never done: the label and the bins are honest now, but a reader looking for Finnish- or Hungarian-size systems will
find them about half as often as in the world's languages.

Where the gap is: in a 700-generation grammar harness with no sound change (40 protos, L2 share 0.3) the same code
reaches 6+ cases in ~40%; the full run damps that by adult-learner stripping, generations too short for long-lived
peoples and inherited small systems. Levers, in order of how much they move the harness: (1) every oblique case of a
'many' system pulled on its own (`PULL_GROUP`; harness: 6+ ~42%, but bimodal, 10+ 35-42% and 6-7 0%); (2) the series rate
`LOCAL_FORM` 0.01 -> 0.02; (3) thin the 2-4 band (GEN/LOC/DAT bind early in 'few' systems). One small screen pass each.

## Updates
- 2026-11-09: Lane 7 (b50a316c): oblique case now drawn conditioned on core case (Grambank pairing). 6+ cases 19.2→21.3% in the full pass (WALS 32%). Remaining cause: protos start with no case and grow it over hundreds of generations. Next: seed each proto's case endings to its aim at birth, as _deep_past does.
- 2026-11-09: Created from inbox draft draft-language-big-case-systems-still-short.md (found by language lane 4 (PW-1569)).
