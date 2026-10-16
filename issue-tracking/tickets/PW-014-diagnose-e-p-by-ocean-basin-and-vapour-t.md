---
id: PW-014
title: Diagnose E-P by ocean basin and vapour transport across land bridges
type: story
status: in-progress
parent: PW-013
subsystem: climate
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [tools/earth_check.py, planet/climate.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
Add diagnostics (in `tools/earth_check.py`) on Earth's terrain: evaporation minus precipitation per
ocean basin (Atlantic, Pacific, Indian, Arctic, Southern), and net water-vapour transport across land
bridges and isthmuses. The key check: Atlantic → Pacific across Central America ≈ 0.25 Sv observed.
Compare with observed basin E−P and salinity (Atlantic saltier than Pacific). Find where the rain
model loses the contrast (e.g. rain falls too close to its source, too little inland/long-range
transport by the trades and westerlies).

## Updates
- 2026-10-16: Diagnosis done: tools/moisture_budget.py (+ tests), Earth L6/L7 reports in docs/review/moisture-budget-2026-10-16/, findings ranked in docs/proposals/moisture_transport.md §2 (interior rain 2-8x too efficient with vapour ~right; per-cell rates halve L7's rain-out length; storm eddies carry ~0 vapour; Atlantic E-P-R +0.06 Sv because its catchments return 0.84 Sv; Central America 0.24 Sv is right).
- 2026-10-16: Status todo -> in-progress. Agent started: diagnosis tool + moisture-transport proposal for owner review.
- 2026-10-14: Created from the rain/overturning epic (owner discussion 2026-10-14).
