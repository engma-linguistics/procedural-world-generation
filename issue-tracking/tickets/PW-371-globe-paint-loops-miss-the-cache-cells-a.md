---
id: PW-371
title: Globe paint loops miss the cache - cells are numbered coarse-level first
type: task
status: todo
parent: PW-649
milestone: later
subsystem: viewer
effort: m
impact: low
found_by: viewer-3d
blocked_by: []
relates: [PW-316]
refs: [viewer/index.html, viewer/relief.js, planet/grid.py]
created: 2026-10-16
updated: 2026-10-23
---

## Description
A grid's cells are numbered coarser level first (cell 1000 and 1001 at L7 are thousands of km
apart), while a cell's corners are numbered locally. Every per-vertex loop in `paint` (positions,
colours, the 3D relief's smooth normals in `relief.sphereNormals`) and the corner loops gather
across the whole grid. Measured at L7 in Node: the smooth-normal kernel takes ~20 ms on the real
grid against ~5 ms on the same amount of work with local access; it is why the relief shades smooth
only while still and flat during a replay.

Try: renumber the mesh's cells for locality once per grid (e.g. sort cells by their first corner,
or a Hilbert/Morton order of their positions) and build the vertex buffers, `vSrc`, `cList` and
the fan lists in that order (picking maps back through `triCell`). Could take the replay above
the ~25 keyframes/s it reaches now, and allow smooth relief shading during replay. Measure with
`planetViewer.bench()`.
- [ ] keyframe ms before/after on run a1d3b9 (L7), relief on and off

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-16: Created from inbox draft draft-globe-cell-order-locality.md (found by viewer-3d).
