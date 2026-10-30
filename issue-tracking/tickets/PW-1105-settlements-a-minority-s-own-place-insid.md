---
id: PW-1105
title: "Settlements: a minority's own place inside another people's land (a dwarf hold in the humans' hills), not only the cell's chief place"
type: task
status: todo
parent: PW-856
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-60
blocked_by: []
relates: [PW-1011, PW-929, PW-910]
refs: [planet/lineages/settlements.py, "run 6553f1", "world 4360a3"]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The settlement ledger (PW-1011 v0) keeps one place per cell, the cell's chief place, and gives it to the people with the most heads there. A smaller people living in the same cells, such as dwarves in hills that humans farm, then never holds a place of its own, even where it is a fifth of the people.

On world 4360a3, run 6553f1, the dwarves lead only 4 cells by heads at the present (1.2 Mkm² of range, 1.4 million people). They founded 40 sites over the last 12 kyr and hold 4 now. The other runs on that world: 57 founded / 11 alive, and 23 / 7. Two causes are fixed in lane 60:
- 'villages' was too slow a tech (rate 0.12 now);
- miners counted as nobody settled (HOLD_SHARE now).

What remains is that the dwarves seldom lead a cell (also PW-929: dwarves are remnants on some worlds).

What to try: let a cell hold a second site for its second people (mix_second, at least ~15% of the heads) when that people can build. It would be a hamlet, hold or quarter town at its own spot (dwarves' on the highest ground of the cell). The globe would then show the dwarf holds and the kobold warrens inside the humans' country. Check against the PW-910 mixing preset (realistic vs fantasy-neat).
- [ ] second-people sites; dwarves hold 20+ live sites on 4360a3 where they live mixed with humans

## Updates
- 2026-10-30: Created from inbox draft draft-settlements-minority-holds.md (found by fun-lane-60).
