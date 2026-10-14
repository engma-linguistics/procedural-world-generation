---
id: PW-057
title: Run lakes and sliced-world lakes disagree
type: task
status: todo
parent: null
subsystem: hydrology
effort: m
impact: low
found_by: lakes
blocked_by: []
relates: []
refs: [planet/world.py, planet/timeline.py, "run 8dc2f2", "world 1c98e7"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Closed lakes on flat basins disagree a lot between a run frame and the world sliced at the same time
(t=180 in demo run 8dc2f2: 1 shared wet cell of 88 vs 18), because the world adds ±180 m texture, its own
erosion and a fresh climate. Open lakes agree roughly; the world's are smaller and about half as deep.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world.
