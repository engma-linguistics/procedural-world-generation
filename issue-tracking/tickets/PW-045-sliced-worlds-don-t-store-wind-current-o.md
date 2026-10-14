---
id: PW-045
title: Sliced worlds don't store wind, current or jet layers
type: task
status: todo
parent: null
subsystem: store
effort: s
impact: med
found_by: overview
blocked_by: []
relates: []
refs: [planet/world.py, planet/store.py, "world 7c5adf"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Only runs and the Earth world store `wind_e/n`, `current_e/n` and `jet_e/n`, so those overlays never
appear on generated (sliced) worlds, e.g. 7c5adf. Add them to the world layers in `world.py`/`store.py`.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world (found by the overview agent; confirmed: 7c5adf has no wind layers).
