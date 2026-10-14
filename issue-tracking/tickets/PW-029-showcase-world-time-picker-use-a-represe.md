---
id: PW-029
title: "Showcase world-time picker: use a representative moment, not the most dispersed"
type: task
status: todo
parent: null
subsystem: highlights
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: [planet/__main__.py, planet/highlights.py, docs/coordination.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The overnight post-processing picked each showcase world at the run's "most dispersed" moment, which
biased worlds toward the most fragmented snapshot. Use a neutral or representative time instead (e.g.
land fraction and landmass count near the run's median after 300 Myr). The tool was a temp script, so
make it a proper `planet` option (e.g. `planet slice <run> --at representative`, or in `planet
highlights`) or a documented rule in `docs/coordination.md`.

## Updates
- 2026-10-14: Created from the owner discussion 2026-10-14.
