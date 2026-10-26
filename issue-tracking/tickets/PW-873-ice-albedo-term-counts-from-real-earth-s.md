---
id: PW-873
title: Ice-albedo term counts from real Earth's ice share (3.1%), not the model's own ice at dT = 0
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: xs
impact: low
found_by: coupling-audit
blocked_by: []
relates: []
refs: [planet/tectonics/earth.py, tools/ice_probe.py, docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-26
---

## Description
Coupling audit finding C8 (severity low for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**Physics lane:** take fourth.

**One side:** planet/tectonics/earth.py EARTH_ICE = 0.031 (branch L25) and global_temperature: -(albedo(ice_frac) - albedo(EARTH_ICE)), ice_frac a cell count.

**Other side:** The model's own Earth at dT = 0 holds 2.53% of the surface in ice (tools/ice_probe.py, docs/overview.md section 2.8, L6).

**Why they disagree:** The intent is "Earth's ice is neutral"; with the model's own Earth ice the term is +0.23 C, not 0. ice_frac is also a cell share (cells differ by up to ~9% in area).

**Measured:** albedo(f) = 3 tanh(f/0.06): albedo(0.031) - albedo(0.0253) = 0.23 C.

**What to try:** Set EARTH_ICE from the model's own Earth probe (area-weighted) and weight ice_frac by cell area. Fold into the next calibration pass.

## Updates
- 2026-10-26: Milestone null -> v1. (PW-900 backlog reorg).
- 2026-10-25: v1-finish-13 (1b52cdf): ice-albedo zero is the model's own Earth ice at dT 0, area-weighted (earth.MODEL_EARTH_ICE: L6 2.77%, L7 3.05%, tools/ice_probe.py now prints the area share); the run's ice share is area-weighted.
- 2026-10-25: Created from inbox draft draft-ice-albedo-reference-is-real-earths-ice.md (found by coupling-audit).
