---
id: PW-019
title: Rain is patchy cell to cell on flat ground, with diagonal streaks
type: task
status: todo
parent: PW-013
subsystem: climate
effort: m
impact: med
found_by: zoomwater
blocked_by: []
relates: []
refs: [planet/climate.py, docs/review/rivers_lakes_deltas.md, "world 7c5adf"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Neighbouring cells on flat ground differ by a median 1.5× in rain (vs 1.16× globally), seen near the
hothouse lake in the rivers/lakes investigation. Diagonal streaks in rain maps predate the gyre work.
Owner: the same moisture-transport problem is probably behind it. Fix with the transport work or
smooth the source terms; check rain maps on a showcase world (e.g. 7c5adf) and on Earth.

## Updates
- 2026-10-14: clouds: the cloud layer's deep cloud sees the rain smoothed over 300 km, which hides most of this lattice there; it still shows faintly in the humidity, cloud and sunshine layers over wet tropical land at L7 (world 2085dc), inherited from the rain and vapour.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Climate ('Rain is patchy cell to cell').
