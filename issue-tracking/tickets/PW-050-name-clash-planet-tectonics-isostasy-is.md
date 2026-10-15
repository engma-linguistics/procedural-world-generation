---
id: PW-050
title: "Name clash: planet.tectonics.isostasy is the function, not the module"
type: task
status: done
parent: null
subsystem: tectonics
effort: xs
impact: low
found_by: mantle
blocked_by: []
relates: []
refs: [planet/tectonics/__init__.py, planet/tectonics/isostasy.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
`planet/tectonics/__init__.py` re-exports the function `isostasy`, so `planet.tectonics.isostasy` resolves
to the function and the module is shadowed. Rename the function or stop re-exporting it.

## Updates
- 2026-10-15: Status todo -> done. Merged (ice).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Crust and continents (still true at bdc967f).
