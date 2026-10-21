---
id: PW-259
title: "climate._stommel: serial Gauss-Seidel/SOR is 5% of an L7 run and 8.5% of an L7 time zoom; try a faster solver"
type: task
status: todo
parent: PW-247
milestone: v2
subsystem: climate
effort: m
impact: low
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249]
refs: [planet/climate.py, docs/review/gpu/profile.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`climate._stommel` (wind-driven ocean streamfunction) relaxes r lap(psi) + beta dpsi/dx = F with
SOR sweeps in a fixed east-to-west order (one sweep carries the Sverdrup balance across a basin).
It is single-threaded by design and grows faster than the cell count: 47 ms per call at L6, 330 ms
at L7 (2.6% of an L6 run, 5.3% of an L7 run, 8.5% of an L7 time zoom). It can't go to a GPU as is
(the order is the algorithm). Options: a sparse direct solve of the same linear system (would need
scipy, not a dependency), a multigrid V-cycle using the existing coarse grids as levels, or
warm-starting psi from the last climate update (fewer sweeps). Any of these changes the output
slightly (converged vs iteration-limited psi), so this needs a check that currents/SST stay put
(`tools/earth_check.py`) and new goldens.

## Updates
- 2026-10-15: Created from inbox draft draft-stommel-solver-sequential.md (found by gpu-explore (PW-249)).
