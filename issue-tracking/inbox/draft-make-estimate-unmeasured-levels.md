---
title: planet make's time estimates for L4, L5 and L8 are still scaled, not measured
type: task
status: todo
parent: PW-244
milestone: null
subsystem: infra
effort: s
impact: low
found_by: worktree-agent-a7b485e309b6e3a74 (PW-478 calibration)
blocked_by: []
relates: [PW-478]
refs: [planet/make.py, docs/coordination.md]
---

## Description
PW-478 fitted the `make` stage costs (`RUN_S_PER_GYR`, `TZ_S_PER_KYR`, `FINISH_S`,
`HIGHLIGHTS_S`, `ZOOM_S`) from the store's timings for L6 and L7. Three levels still have no
store measurement, so their numbers are scaled:
- L4: one 100 Myr run (23.2 s, one short run, fixed start-up cost included), so 230 s/Gyr is one data point.
- L5: no data; interpolated between L4 and L6 (400 s/Gyr).
- L8: no data; scaled from L7 by the cell count (x4).

Measure L5 (one 1 Gyr run, or 300 Myr) and one L8 timing when the owner has a window, then
refit the L4/L5 rows and check the L8 row. A time zoom and a regional zoom at L4/L5/L8 would
also be worth one timing each.

- [ ] L5 run timed on the owner's machine; RUN_S_PER_GYR[5] refit.
- [ ] L4 run timed again warm (the first run may include numba start-up).
- [ ] L8 run timed or the row kept with its note.
