---
id: PW-1263
title: Refined L8 world has 6x the source's lakes (211 vs 35); check which are real
type: task
status: todo
parent: PW-1198
milestone: v5
subsystem: hydrology
effort: s
impact: low
found_by: lane104-refine-l8
blocked_by: []
relates: [PW-490]
refs: [planet/refine.py, "world 783674", docs/review/refine-l8/design.md]
created: 2026-11-01
updated: 2026-11-03
---

## Description
**In plain words.** The refined L8 world has many more small lakes than its L7 source: 211 lakes on 1,597 cells,
against 35 lakes on 126 cells at L7. The directly simulated L8 world a16f5a has 124 lakes on 1,944 cells, but 1,439 of
those cells are one giant salt lake, so its other lakes cover about 500 cells. In the refined world 96 of the 211
lakes are single cells.

`refine.terrain` drains the noise's hollows (priority flood) everywhere except where the L7 world held water,
drained inland, or lay below sea level. The hollows there are kept on purpose and fill to lakes by their water
balance. So most of the new lakes are probably inside L7 closed basins. That would be a real gain from the finer
grid, but nobody has checked it.

Try: count the refined world's lakes inside and outside the L7 closed basins, and look at the one-cell ones. If most
are noise pits inside basins, drain the ones shallower than the noise's own amplitude.
- [ ] lake count per source basin, and a verdict (keep them, or drain the shallow ones)

## Updates
- 2026-11-03: Milestones 11-03: later -> v5: v5 must-have: check the refined world's extra lakes before the campaign world is refined
- 2026-11-03: Triage 11-03: v2 -> later: L8/L9 whole-world work, post-v2 (see PW-1198 space-to-ground globe)
- 2026-11-01: Created from inbox draft draft-refine-lakes-in-coarse-closed-basins.md (found by lane104-refine-l8).
