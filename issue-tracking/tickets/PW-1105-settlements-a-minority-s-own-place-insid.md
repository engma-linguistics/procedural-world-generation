---
id: PW-1105
title: "Settlements: a minority's own place inside another people's land (a dwarf hold in the humans' hills), not only the cell's chief place"
type: task
status: done
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
- 2026-10-30: Status todo -> done. Fun lane 61: a cell may hold a second place, its second people's own (kind 'minority' in settlements.json), friends or foes of the lead alike (owner 10-30). Founded where that people is SECOND_MIN (5%) of the heads or more and the place reaches FOUND (300) people: MINORITY_SHARE (10%) of its settled heads, or for a mining people its halls, HOLD_SHARE (0.5) of its heads, up to a town (a hold) if it knows 'towns'; a mining people's place leans to the cell's highest neighbour. It stays its founders' and merges into the chief place (no ruin) once they have led the cell for HAND_KYR. Also mines (kind 'mine', owner 10-30): on an ore district or rock-salt bed, worked by the lead (else the second) people once it knows 'mines' (and 'copper' for ore), 0.4% of the cell's people. Chief places unchanged: with the new kinds off, the ledgers equal main's exactly. World 4360a3, D&D seeds 7/8/9/10 (runs 488d7e, 6128a3, 114231, 570701), living now main -> branch: dwarves 32->91, 11->57, 7->19, 3->9 (20+ in 2 of 4 runs; on 6553f1 4->60); kobolds 1464->2271, 1380->2324, 1660->2625, 1614->2480; all places 7,291-8,182 -> 14,912-16,061 (of them second peoples' own 4,851-5,620, mines 2,193-2,277, ~95% human). Ruins 616-889 -> 3,146-4,561: churn, see the draft. Viewer: holds drawn like any place; mines as diamonds; hover 'town (their own place, as a second people here) of the dwarves'. Screenshots docs/review/settlements/12-14. Drafts: churn and the 9,999 hold cap; the mine count.
- 2026-10-30: Created from inbox draft draft-settlements-minority-holds.md (found by fun-lane-60).
