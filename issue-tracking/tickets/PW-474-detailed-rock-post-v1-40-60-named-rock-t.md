---
id: PW-474
title: "Detailed rock (post-v1): ~40-60 named rock types and a dig-down rock column per point, derived when a world is finished or zoomed"
type: task
status: todo
parent: PW-155
milestone: v2
subsystem: surface
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-155]
refs: [planet/surface.py]
created: 2026-10-20
updated: 2026-10-29
---

## Description
Owner 2026-10-20: Dwarf Fortress-style knowledge of a region's rocks, without going too nuts or slowing things down. Post-v1.
Approach: keep the run's 16 classes; refine at finish or zoom time from what the run records: protolith and burial depth (e.g. an orogen's shale becomes slate, phyllite or schist; limestone becomes marble), the cover column (km of each layer over basement, tectonics.EXTRA), arc and plutonic history, and age.
Output: a named surface rock per cell or zoom pixel, plus a rock column at any point (layer names and thicknesses down to basement), usable by PW-155's resources and by export (PW-100).
Cost: labels only, so ~0 run time; the stored column is a few bytes per layer.

## Updates
- 2026-10-29: 2026-10-29: owner wants the rock column in v2; World Orogen's per-cell rock column and lithology-controlled relief (PW-1005) are the reference design (docs/review/landscape/world-orogen.md).
- 2026-10-20: Created.
