---
id: PW-049
title: Sediment compaction isn't remembered after uplift
type: task
status: todo
parent: PW-649
milestone: later
subsystem: surface
effort: m
impact: low
found_by: mantle
blocked_by: []
relates: []
refs: [planet/tectonics/isostasy.py]
created: 2026-10-14
updated: 2026-10-23
---

## Description
Sediment density compacts with burial depth (`isostasy.sediment_density`, 2.1 → 2.6 g/cm³), but
compaction isn't remembered: uplifted and eroded sediment decompacts again. Track max burial per cell if
it matters for elevation of exhumed basins.

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Crust and continents.
