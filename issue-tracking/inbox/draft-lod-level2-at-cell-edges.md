---
title: "LOD tiles: level-2 tiles of two cells still differ by ~30 m at their shared cell edge"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane295
blocked_by: []
relates: [PW-1699, PW-1694, PW-1355]
refs: [planet/zoom/lod_build.py, "planet/zoom/lod_build.py::edge_blocks", "planet/zoom/lod_build.py::line_seam", docs/review/zoom/lod-plan-v2.md, "world dba204", "tiles py.1.1/2/0/3-4, py.0.1/2/7/3-4"]
---

## Description
**In plain words.** Where two of the big 4,000 km squares meet, their first detail level (4 km) now fits: the
later square takes the earlier one's ground (lane 295). One level finer (1 km), the two sides still miss each other
by about 30 m in the middle and 120-170 m at the worst tenth of the line (dba204, cells py.1.1 and py.0.1). If this
is never done, scrolling along a square's border at 1 km detail and finer shows a visible step all along it, in
mountains most.

Measured (lane 295, 1,068 land points along 1,000 km of the line, `lod_build.line_seam`): |A - B| median / p90
29 / 115 m (A built first), 38 / 174 m (B first), against 69 / 211 m for the same tiles on level-1 sections built
alone; their level-1 parents differ by only 12-14 / 56-59 m there (the floor of two 4 km lattices). The step between
neighbouring 1 km pixels along the line is 19-25 m (median): the seam is ~1.5x a pixel step. Cause: the cell edge is
not a tile edge, so neither side fades there; each side's fine pass carves its own ground from its own parent on its
own plane.

What to try: treat the cell line as a tile edge for tiles it crosses: both sides fade over a ramp to ground carved
once by place (as `edge_blocks`, PW-1694), here a strip along the line built on the earlier cell's lattice from the
earlier cell's parent, which the later cell's tiles resample (the later cell's level 1 already equals it there).
- [ ] level-2 tiles of py.1.1 and py.0.1 at their line: |A - B| median no more than the neighbouring-pixel step
      along the line, both build orders
