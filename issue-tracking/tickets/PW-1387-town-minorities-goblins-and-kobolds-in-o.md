---
id: PW-1387
title: Town minorities (goblins and kobolds in other peoples' towns) wait for a towns and minorities model
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: m
impact: low
found_by: lane 139 (PW-1369)
blocked_by: []
relates: [PW-1369, PW-889, PW-1357, PW-1011]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/settlements.py, planet/lineages/spec.py, planet/lineages/brief.py, viewer/globe/settlements.js, "git show HEAD~ -- planet/lineages/history/cities.py (the removed CitiesMixin)", docs/review/cultures-proposal/owner-notes-r1.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the city goblins and city kobolds of the D&D preset are gone (PW-1369, ruling B, 11-02). They were the last
"groups" in the preset, a way to put a few goblins and kobolds into the towns of humans and dwarves (Forgotten Realms style). A
group per minority does not scale: every people living in every other people's towns would need one. So the whole `cities = true`
mechanism went with them (history CitiesMixin, spec `cities` / `hosts`, the settlements' "quarters", the brief's and viewer's quarter
lines). A tree that still says `cities` or `hosts` is refused with a pointer to PW-1369.

What a later towns model could do instead: give each town or city a mix of minorities drawn from the peoples within reach of it
(by distance, trade, and each people's leaning to live among others: tabaxi wanderers, goblin and kobold outcasts), as a share of
the townsfolk, without any per-minority line in the tree. The settlement ledger (settlements.py `who`) already knows who lives in
a town and its ring; minorities would add to that. The old PW-889 numbers (a 2-3% share in the densest twentieth of peopled land
within 1000 km of the minority's own country) are a starting point.
- [ ] a towns-and-minorities design (no per-minority lines), for Daniel's yes
- [ ] the quarters back in the settlement ledger, the brief and the viewer

## Updates
- 2026-11-02: Created from inbox draft draft-town-minorities-model.md (found by lane 139 (PW-1369)).
