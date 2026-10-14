---
id: PW-082
title: "Lake display: hover only with elevation loaded, confusable colours, ~0 m depths"
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: lakes
blocked_by: []
relates: [PW-020]
refs: [viewer/index.html, planet/store.py, "run 8dc2f2"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Run hover shows lake info only when the elevation layer is loaded. Salt-lake teal is close to some biome
greens, and fresh blue is close to shallow sea. `lake_depth` is stored in whole metres, so shallow lakes
read "~0 m" (store decimetres or a log scale). Which layers draw lakes is settled in PW-020 (elevation and biome only).

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world (the layer question is decision D1, closed).
