---
id: PW-054
title: Generated worlds lose their closed basins over time
type: task
status: todo
parent: null
subsystem: tectonics
effort: l
impact: high
found_by: water
blocked_by: []
relates: [PW-056]
refs: [planet/tectonics/, planet/surface.py, docs/review/rivers_lakes_deltas.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Generated worlds have almost no closed (endorheic) basins after ~150 Myr: 0–4% of land drains inland,
against ~20% on Earth's terrain (the model gets 21% on Earth). Sediment and erosion fill every hollow,
and the tectonics makes no new interior basins: foreland basins, intermontane basins (Tarim, Altiplano),
rift-flank highs. Needs tectonic sources of basins, possibly less filling.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Rivers, lakes, sediment and morning_report biggest problem 2.
