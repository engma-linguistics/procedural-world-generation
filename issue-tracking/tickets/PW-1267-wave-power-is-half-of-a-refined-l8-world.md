---
id: PW-1267
title: "Wave power is half of a refined L8 world's finish (129 of 252 s) and grows as cells^1.5: most of L9's 38 min"
type: task
status: todo
parent: PW-1198
milestone: later
subsystem: coast
effort: s
impact: med
found_by: lane104-refine-l8
blocked_by: []
relates: [PW-1211, PW-490]
refs: [planet/coast.py, planet/world.py, docs/review/refine-l8/design.md]
created: 2026-11-01
updated: 2026-11-03
---

## Description
**In plain words.** Making a finished world at L8 spends half its time on one step, the waves arriving at each coast.
At L9 that step is several times worse, because its cost grows faster than the number of cells.

Measured (lane 104, cProfile of `planet refine 783674 --level 8`, 16 threads, load ~35): the whole refine 266 s,
`world.finish` 233 s, of which `coast.wave_power` 129 s and `coast.tide_range` 39 s. The climate (run at L7) is 22 s.
`wave_power_winds` casts N_DIR rays from every ocean cell, each `D_MAX / (0.45 x cell spacing)` steps long, so
its cost goes as cells x 1/spacing, about x8 per level. The L9 refine took 38 min in all, its finish 35 min.
The direct L8 slice (a16f5a) had the same cost inside its 13.8 min.

Try: rays with a fixed step in km (the L7 step) on L8/L9 grids, or the open sea's wave power on the coarse grid
(it is smooth there) with only the coast cells' sheltering done on the fine grid. Check: L7 wave_power unchanged
(goldens), L8 coast-cell values within a few % of today's.
- [ ] L8 wave_power < 30 s; L7 outputs unchanged

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: L8/L9 whole-world work, post-v2 (see PW-1198 space-to-ground globe)
- 2026-11-01: Created from inbox draft draft-wave-power-cost-at-l8-l9.md (found by lane104-refine-l8).
