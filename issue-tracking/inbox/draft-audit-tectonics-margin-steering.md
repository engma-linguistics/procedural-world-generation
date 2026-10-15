---
title: Rifted-margin thickness is steered by the global continental-area error
type: task
status: todo
parent: PW-245
subsystem: tectonics
effort: s
impact: med
found_by: audit-tectonics
blocked_by: []
relates: [PW-046]
refs: [planet/tectonics/crust.py, docs/review/audit/tectonics.md]
---

## Description
In `crust.rifted_margin`, the thinnest margin crust a rift may lay is
`MARGIN_MIN_KM + (rift_margin_km - MARGIN_MIN_KM) x clip(shrink - 1, 0, 1)`.
`shrink` is the area thermostat's factor (`crust.thermostats`), so how
thick a new rifted margin is depends on how far the whole planet's
continental area is above its 40% target. A local physical property is
driven by a global KPI error: a bandaid for PW-046 (area creeping up). The
area thermostat already acts through subduction erosion; this is a second
lever on the same number, and it acts through a process that has nothing
to do with the error.

Measured (audit probes): at L5 seed 1 (0-400 Myr) `shrink` is above 1 on
every step (mean 1.27, up to 1.8), so margins are laid at up to 16.8 km; at
L6 seed 21 (1 Gyr) on 30% of steps (shrink 0.66-1.56).

Fix (simplest sound version): lay margins at one fixed thickness, either
`rift_margin_km` or the stretched source crust's own thickness (that is,
keep beta), and let the subduction-erosion thermostat alone hold the area.
Expect a little more continental area from margins (thin margins make more
cells), which the area thermostat then has to remove. Check land and crust
share over 1 Gyr at L6 (scorecard), and PW-046's drift.
- [ ] margin thickness no longer reads `shrink`
- [ ] L6 seeds 1/2 over 1 Gyr: crust area within the envelope, land change reported
