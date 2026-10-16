---
id: PW-255
title: "Lakes and river routing: three settle passes and ~9 priority floods per step (~15% of an L7 run)"
type: task
status: todo
parent: PW-247
subsystem: hydrology
effort: m
impact: med
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249]
refs: [planet/hydrology.py, planet/kernels.py, planet/surface.py, docs/review/gpu/profile.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`surface.erode` -> `hydrology.lakes` runs `_settle` 3 times per step; each calls `_bed`
(`priority_flood` + `fill_shallow`), `kernels.lakes` (~2.6x per settle) and `hydrology.route`
(`priority_flood_to` + `accumulate_lakes`, ~2.9x per settle; 8.7 routes per step in all). All of
these are inherently sequential (heap order, union-find, topological order), so they don't
parallelise and won't go to a GPU. Per 100 Myr at 16 threads: ~5 s of an L6 run, ~26 s of an L7 run
(lakes 7.3, priority_flood 4.7, fill_shallow 2.8, route's priority_flood_to ~11).

Ideas, cheapest first: skip the 2nd/3rd settle pass when the lake set didn't change (early exit);
reuse the previous route's order when only lake levels moved; a single priority flood that also
returns the filled surface for `route`. Some change outputs slightly (check goldens / lake KPIs).
Expected 30-50% of this bucket.

## Updates
- 2026-10-15: Created from inbox draft draft-lakes-settle-passes.md (found by gpu-explore (PW-249)).
