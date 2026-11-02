---
id: PW-1296
title: "Whole-planet land zoom: tile every land region at regional-zoom resolution, seamless, rivers continuous across tiles"
type: story
status: todo
parent: null
milestone: v2
subsystem: zoom
effort: l
impact: high
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-11-01
updated: 2026-11-01
---

## Description
**In plain words.** Daniel 11-01: rather than an L7 -> L9 refine, cover all of a world's land (not the ocean) with the regional zoom we already have (1-4 km/px). Compute is cheap: an L7 zoom of 1000 km at 2 km took 6.9 s per process (docs/coordination.md speed pass), and an Earth-like has ~170 Mkm2 of land, so ~200-250 overlapping 1000 km tiles is ~30 min one at a time, a few minutes in parallel at 2 km (roughly 4x that at 1 km); to be measured. The real work: (1) seams: neighbouring tiles must agree at their edges (heights, coasts, landforms; cf. PW-541's box-shaped cuts); (2) rivers and lakes routed across tiles so a river is one river (a planet-wide drainage pass at zoom resolution, or tiles conditioned on the world's routing); (3) storage and streaming: a tile pyramid the viewer loads by view, not one file; (4) cost and memory at 1 km. Order: after the v2 priority list (PW-252, PW-1295, PW-015/026, PW-1279, D34 B). First step: a written design and a timing of 10 adjacent tiles, with the seam problems measured.

## Updates
- 2026-11-01: Created.
