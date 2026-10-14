---
id: PW-115
title: "Time zoom: the ablation zone is one cell wide (sub-cell melt at margins)"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: low
found_by: climfix
blocked_by: []
relates: [PW-036]
refs: [planet/timezoom.py, planet/timezoom_kernels.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Split from PW-036 (its other half, the accumulation jumps at climate refreshes, is fixed on climfix).
In the Earth time zoom (L6, 100 kyr from today) 94% of ice cells with negative mass balance are margin
cells: north of 40N 87 of 93 ablating cells sit on the sheet's edge, in Antarctica 64 of 65. Real
ablation zones are tens to ~150 km wide and slope up into the sheet; here a margin is one ~110 km cell
that drops from the dome's height to bare ground, so the melt is all-or-nothing at the edge.
Ideas: a sub-cell hypsometry for margin cells (melt computed over a spread of surface heights between
the cell's and its ice-free neighbours'), or a partial ice cover per cell. Measure with the share of
ablating cells away from the margin and the ablation area ratio (Greenland today ~0.15-0.2 of its area).
- [ ] ablating ice not confined to margin cells; ablation area ratio reported in the run's stats

## Updates
- 2026-10-14: Created from inbox draft draft-timezoom-one-cell-ablation-zone.md (found by climfix).
