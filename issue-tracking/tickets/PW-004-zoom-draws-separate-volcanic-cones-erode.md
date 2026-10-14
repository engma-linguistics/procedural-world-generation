---
id: PW-004
title: Zoom draws separate volcanic cones, eroded old islands and atolls
type: story
status: todo
parent: PW-001
subsystem: zoom
effort: l
impact: high
found_by: daniel
blocked_by: [PW-003]
relates: []
refs: [planet/zoom.py, planet/zoom_kernels.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Given the world's volcano list, the zoom synthesises each volcano: a cone (stratovolcano for arcs,
shield for hotspots) sized by height and age, gullied and lowered as it ages, and once an ocean island
has subsided in warm water (SST > ~20 °C), a fringing reef → barrier reef → atoll sequence. Arc chains
should read as separate peaks, not a ridge.

## Updates
- 2026-10-14: Created from the discrete-volcanoes epic (owner discussion 2026-10-14).
