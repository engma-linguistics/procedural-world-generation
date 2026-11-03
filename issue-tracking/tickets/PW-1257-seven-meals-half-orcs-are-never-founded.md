---
id: PW-1257
title: "Seven Meals half-orcs are never founded on af2677 in 3 of 5 tries: a hybrid people needs its parents to meet 10 kyr ago"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: peoples
effort: s
impact: med
found_by: lane101
blocked_by: []
relates: [PW-1239, PW-1240, PW-752]
refs: [planet/lineages/history/origins.py, planet/lineages/samples/seven_meals.toml, docs/review/peoples-leader/data.json]
created: 2026-11-01
updated: 2026-11-01
---

## Description
**In plain words.** In Seven Meals the half-orcs are a people of their own, born 10,000 years ago "where the humans and orcs meet".
On world af2677 the orcs are small (0.4-1% of all people) and often do not touch the humans at that moment, and then the half-orcs are
never founded at all. It happened in 1 try on main (j1) and in 3 of the 5 af2677 Seven Meals tries after lane 101's in-fighting
(s7, s13, j1). The in-fighting did not kill them (no brake ends a people now); it thinned the orcs a little and moved where they meet
the humans. The half-orcs were already the suite's most brittle people (their share swings 2,000x).

The fix belongs to the founding, not the brakes: a hybrid whose parents do not touch at its date could found where their lands come
nearest (as a split with no room founds at the nearest country it can live in, `_origin_fallback`).

- [ ] a hybrid people founds at its parents' nearest approach when they do not meet; a test with two parents a few cells apart
- [ ] the suite: no "never founded" half-orcs in Seven Meals

## Updates
- 2026-11-01: Created from inbox draft draft-half-orcs-never-founded-when-parents-do-not-meet.md (found by lane101).
- 2026-10-31: Created by lane 101.
