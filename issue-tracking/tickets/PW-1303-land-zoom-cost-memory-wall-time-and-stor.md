---
id: PW-1303
title: "Land zoom cost: memory, wall time and storage per 4000 km section, and whether the GPU should take the heavy pass"
type: task
status: in-progress
parent: PW-1299
milestone: v2
subsystem: zoom
effort: m
impact: med
found_by: owner
blocked_by: [PW-1300]
relates: []
refs: [docs/review/gpu/profile.md, docs/review/speed/pw252.md, planet/parallel.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** Measure a section's peak memory and time at ~1 km/px, how many run side by side on this machine (183 GB RAM, 48 cores, RTX PRO 6000 96 GB), the storage of a whole planet's land, and whether the zoom's heaviest kernels belong on the GPU (lane 114 found GPU pays from L8-sized arrays; a 4000 km section is ~16 M px).

## Updates
- 2026-11-02: Status todo -> in-progress. 11-02: lane 122 (cost profile + fixes; tiling design and section lister).
- 2026-11-02: 11-02 from PW-1300: a 4000 km section at 1 km took 2 h 48 m and peaked at 110 GB (107 GB in the first 8 min, then ~48 GB through a long single-core stage); at 2 km 20-60 min and 22-40 GB. A planet at 1 km is ~50 h one at a time and can't run in parallel at 110 GB, so cost comes before the sweep: find the memory peak and the single-core stage first.
- 2026-11-02: Created.
