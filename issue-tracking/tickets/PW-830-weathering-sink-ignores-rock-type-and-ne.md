---
id: PW-830
title: "Weathering sink ignores rock type and never saturates: weight by silicate share, together with PCO2_BALANCE"
type: task
status: todo
parent: null
milestone: later
subsystem: tectonics
effort: m
impact: med
found_by: assumptions-audit
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-11-03
---

## Description
From the pre-v1 assumptions audit (docs/review/assumptions-audit/README.md, findings.json): Weathering sink ignores rock type and never saturates: weight by silicate share, together with PCO2_BALANCE.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: second-order tectonics refinement; the planet is stable without it
- 2026-10-25: v1-finish-11: the sink now has GEOCARB III's saturating CO2 law under plants ((2X/(1+X))^0.4, bare X^0.5) and a runoff factor; the lithology weighting is still open. docs/review/base-climate/v1-finish-11/README.md
- 2026-10-24: Created.
