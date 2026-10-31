---
id: PW-1244
title: The diagnostics' sink CO2 slope (w_a) ignores the plants' starvation below 124 ppm
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: xs
impact: low
found_by: lane95
blocked_by: []
relates: [PW-1227]
refs: [planet/tectonics/diag.py, planet/tectonics/earth.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
In plain words. A diagnostic number reads slightly wrong at very low CO2; the model itself is right.

`diag.py` writes `w_a = earth.co2_slope(X, w_bare)` without the planted cells' starvation (`starve`, lane 95), so below
124 ppm it reports the old, shallower slope. Read-only diagnostics, opt-in; no run output changes. Fix: build the same
`starve` tuple as `global_temperature` does and pass it (or have `weathering` return it).
- [ ] w_a matches `co2_slope(X, bare, starve)` below the floor

## Updates
- 2026-10-31: Created from inbox draft draft-diag-co2-slope-ignores-starvation.md (found by lane95).
