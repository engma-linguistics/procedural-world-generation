---
id: PW-1303
title: "Land zoom cost: memory, wall time and storage per 4000 km section, and whether the GPU should take the heavy pass"
type: task
status: todo
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
- 2026-11-02: Created.
