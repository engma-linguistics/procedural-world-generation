---
id: PW-196
title: "Zoom terrain indices: slope-aspect radiation index and topographic wetness index layers"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: med
found_by: vegprop
blocked_by: []
relates: [PW-101, PW-139, PW-185, PW-187, PW-178]
refs: [planet/zoom.py, docs/proposals/vegetation.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Vegetation downscaling (proposal docs/proposals/vegetation.md §3.7) and soils (PW-185) both need, per zoom pixel: a radiation index from slope and aspect against the noon sun at the zoom's latitude (poleward slopes darker, cooler, moister), and the topographic wetness index TWI = ln(upslope area / tan slope) from the zoom's `drainage_area` and heightmap (wet hollows and valley floors), plus distance to the nearest river above a discharge threshold (riparian/gallery forest). PW-101 (microclimate) would use the same radiation index. Today the zoom computes slope internally for the landscape pass but stores no such layers.

Do: compute these once after the final heightmap in zoom.py, store `radiation_index` (u1), `twi` (u1, scaled) and `river_dist` (u1, px), and expose them to later passes. Small, deterministic, no change to existing layers.
- [ ] three layers stored and listed in the zoom legend specs
- [ ] noise-free: overlapping zooms agree where their heightmaps agree

## Updates
- 2026-10-14: Created from inbox draft draft-zoom-terrain-indices.md (found by vegprop).
