---
title: "LOD tiles: cell edges at levels 3-4, and where three or four cells meet"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane297
blocked_by: []
relates: [PW-1705, PW-1699, PW-1694]
refs: ["planet/zoom/lod_build.py::line_surface", "planet/zoom/lod_build.py::line_blocks", "planet/zoom/lod_build.py::line_owner", "planet/zoom/lod_build.py::near_lines", "planet/zoom/lod_build.py::LINE_LEVEL", "planet/zoom/fine.py::build", tests/test_zoom_lod_cells.py, docs/review/zoom/lod-plan-v2.md, "world dba204", "cells py.1.1, py.0.1"]
---

## Description
**In plain words.** Lane 297 (PW-1705) made the 1 km tiles of two big squares meet where the squares meet: on dba204 the
two sides now differ by 3 m (median) where they differed by 29-38 m, which is as close as two pixel grids can draw the
same ground. Only level 2 does this. The 250 m and 25 m tiles (levels 3-4) near a square's edge still each carve
their own ground from their own parent, so a smaller step (not measured: no level-3 tiles were built at the line) can
come back when zooming in further along a square's border. Separately, within ~10 km of a corner where three or four
squares meet, each side blends the two edges' ground in its own way, so the corner can show a small mismatch there.
If never done, the border of a big square may show a faint seam in close-up views and at its corners.

What to try:
- Levels 3-4: the same construction one level down: `line_surface` for level L carves on the owner cell's level-L
  lattice from the owner's level L-1 tiles along the line. Unlike level 1, those parent tiles need not be built when the
  other cell's tile is wanted: the tile service (planet/tiles.py) would have to queue the owner's parent tiles along the
  line too, or the line be carved from the owner's level 1 through two passes. Measure first: build a level-3 tile pair
  at the dba204 line (py.1.1 / py.0.1) and compare with lane 295's `line_seam` against the two-lattice floor
  (`resampled`); if within ~10% already, close as not needed.
- Corners: at a pixel near two cell edges, both cells should blend the same two surfaces with the same weights; today
  each cell's weights are computed in its own plane from its own edges (the diagonal neighbour's edges are not seen).
- [ ] level-3 seam at the dba204 line measured, both build orders; fixed if over 10% of the floor
- [ ] a tile at a 3- or 4-cell corner of dba204: |A - B| along each edge within 10 km of the corner against the floor
