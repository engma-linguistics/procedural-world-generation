---
id: PW-309
title: Run stats' land_pct counts oceanic crust with bed > 0 whose trench puts the frame's elevation below the sea
type: task
status: todo
parent: null
subsystem: tectonics
effort: xs
impact: low
found_by: pw305-prototype
blocked_by: []
relates: [PW-246]
refs: [planet/tectonics/output.py, tests/test_health.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`stats()` counts land as `sim.land()` = `(bed > 0) | (ice > 0)`. The snapshot's elevation is `bed + w_trench` on oceanic crust (output.py:71). So a few oceanic cells with a bed just above the sea come out as land in the run's stats and as sea in the frame. Example: L4 seed 1 at 300 Myr on the PW-305 branch, 2 cells with bed +10 / +148 m and frame elevation -257 / -311 m.

`tests/test_health.py::test_measure_frame` failed on this by 0.01 of its 0.1-point tolerance. The PW-305 branch now names the case in the test.

Decide whether `stats()` (and `land()`'s users) should use the frame's elevation for oceanic crust, so the run's land and every frame's land agree.

## Updates
- 2026-10-15: Created from inbox draft draft-land-pct-trench-cells.md (found by pw305-prototype).
