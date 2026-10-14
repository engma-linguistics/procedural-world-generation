---
id: PW-056
title: "Drainage memory: rivers switch outlet in one step when a rift opens"
type: task
status: todo
parent: null
subsystem: hydrology
effort: l
impact: low
found_by: water
blocked_by: []
relates: [PW-054]
refs: [planet/hydrology.py, planet/tectonics/events.py, docs/review/rivers_lakes_deltas.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
When a rift opens, a continent's drainage can switch to the new coast in a single 2 Myr step. Real
drainage keeps old channels; the physical damping is rift-flank uplift raising a divide next to the new
rift. A channel memory would have to move with the plates (per-cell arrays are world-frame), so the
likely fix is rift-flank uplift in the tectonics.

## Updates
- 2026-10-14: Migrated. Merged: 'Drainage switches outlet in one step' and 'Drainage memory is not implemented' (water).
