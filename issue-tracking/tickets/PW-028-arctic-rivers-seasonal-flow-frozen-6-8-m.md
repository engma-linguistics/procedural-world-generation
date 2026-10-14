---
id: PW-028
title: "Arctic rivers: seasonal flow (frozen 6-8 months, spring flood)"
type: task
status: todo
parent: null
subsystem: hydrology
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: [planet/hydrology.py, planet/climate.py, "zoom f81832", "world 0f7abd"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Rivers in cold climates should carry most of their water in a spring flood after 6–8 frozen months,
not a steady annual mean. That changes delta form (ice-dammed floods, river-dominated) and the zoom's
river look. Model it as a seasonal discharge profile from the monthly temperature (snow storage,
melt), at least as a stored "flood ratio" per cell for the zoom and deltas. Reference: zoom f81832 on
world 0f7abd (Lena-like: 2.2 Mkm², −12 °C mean, 16,800 m³/s).

## Updates
- 2026-10-14: Note from PW-027 (quickwins): the reference mouth of zoom f81832 (51.6 N, -13.3 on world 0f7abd) is on an ice-free sea (sea cells' cold month +2 to +3.5 C; wave power 26-67 kW/m), so sea-ice damping leaves its delta wave-dominated. Only the cold basin is Arctic; a spring-flood sediment pulse (this ticket) is what could push it toward river-dominated.
- 2026-10-14: Created from the owner discussion 2026-10-14.
