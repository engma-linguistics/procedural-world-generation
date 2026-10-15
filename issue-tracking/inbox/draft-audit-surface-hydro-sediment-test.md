---
title: Add an invariant test that surface.erode conserves sediment (deposited = removed)
type: task
status: todo
parent: PW-245
subsystem: infra
effort: xs
impact: low
found_by: audit-surface-hydro
blocked_by: []
relates: []
refs: [planet/surface.py, tests/test_invariants.py]
---

## Description
Today `surface.erode`'s budget closes exactly: sum(deposited) == sum(removed) per step to 4e-16 (L5, 150 steps).
No test asserts it, so a future change to `_route`, `_offshore`, `_spread` or the lake spreads could leak or
create sediment unnoticed. Add a test to test_invariants on sim4: wrap surface.erode for a few steps, assert
equal sums (rtol 1e-9) and dep >= 0.
