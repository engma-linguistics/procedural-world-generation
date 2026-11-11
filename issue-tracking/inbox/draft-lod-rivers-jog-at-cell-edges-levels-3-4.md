---
title: "LOD tiles: big rivers cross a cell edge 1-4 km apart on the two sides at levels 3-4"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane300
blocked_by: []
relates: [PW-1708, PW-1705, PW-1355, PW-1302]
refs: ["planet/zoom/lod_build.py::line_rivers", "planet/zoom/lod_build.py::line_surface", "planet/zoom/fine.py::_courses", "planet/zoom/fine.py::build", "planet/zoom/lod.py::parent_mosaic", tests/test_zoom_lod_cells.py, docs/review/zoom/lod-plan-v2.md, "world dba204", "cells py.1.1, py.0.1", "tiles py.1.1/3/0/15-16, py.0.1/3/28/15-16"]
---

## Description
**In plain words.** Where two big squares (cells) meet, the ground now matches at every zoom level (PW-1705, PW-1708),
but a large river crossing that border at the 250 m and 25 m levels can end on one side and restart 1-4 km along the
border on the other: each side lays its course from its own parent tiles, and at 250 m a few kilometres is 4-16
pixels, a visible jog. If never done, zooming in on a border river shows it broken where the squares meet.

Measured on dba204 (scratch roots of lane 300, gone; rebuild: level 1 of py.1.1 and py.0.1 in either order, then the
level-2 tiles 2/0/3-4 and 2/7/3-4 (and py.0.1/2/6/3-4), then the level-3 tiles listed in refs). `line_rivers` looks
for the other side's river within 2 px of where a river enters; at level 3 that is 500 m:
- py.1.1 first: a 2,874 m3/s river leaving py.1.1/3/0/16 finds 140 m3/s within 2-8 px on py.0.1's side and its
  2,927 m3/s within 16 px (4 km). The same on main's code (the edge fade changes heights, not courses).
- py.0.1 first: a 3,576-6,101 m3/s river runs along the line, crossing it 3-5 times; each crossing finds 0 m3/s within
  2 px on the other side and the river within 4-16 px. Main's code: 5 such crossings, this branch 3.
- At level 2 the same rivers pass `line_rivers` (2 px is 2 km there), so the offset was already there, under 2 km.
What to try: lay a parent river's course near the line once, by place, on the owner's lattice (as the ground's
`line_blocks`), and have both cells' tiles impose that course and its discharge there (the later cell's discharge
into the earlier stays the earlier's own estimate, PW-1355).
- [ ] dba204 py.1.1 | py.0.1 at level 3, both orders: every river >= 100 m3/s crossing the line finds the other
      side's within 2 px, within 20% of its discharge (or the later->earlier estimate, PW-1355)
