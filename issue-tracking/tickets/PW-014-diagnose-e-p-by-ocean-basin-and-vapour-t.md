---
id: PW-014
title: Diagnose E-P by ocean basin and vapour transport across land bridges
type: story
status: todo
parent: PW-013
subsystem: climate
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [tools/earth_check.py, planet/climate.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Add diagnostics (in `tools/earth_check.py`) on Earth's terrain: evaporation minus precipitation per
ocean basin (Atlantic, Pacific, Indian, Arctic, Southern), and net water-vapour transport across land
bridges and isthmuses. The key check: Atlantic → Pacific across Central America ≈ 0.25 Sv observed.
Compare with observed basin E−P and salinity (Atlantic saltier than Pacific). Find where the rain
model loses the contrast (e.g. rain falls too close to its source, too little inland/long-range
transport by the trades and westerlies).

## Updates
- 2026-10-14: Created from the rain/overturning epic (owner discussion 2026-10-14).
