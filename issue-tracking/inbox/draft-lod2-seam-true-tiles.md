---
title: "LOD globe step 1: build level-of-detail tiles on one shared grid per level, so tiles built at different times meet without a seam"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: l
impact: high
found_by: lane289
blocked_by: []
relates: [PW-1198, PW-1299, PW-1341, PW-541, PW-391]
refs: [docs/review/zoom/lod-plan-v2.md, planet/zoom/lod.py, "planet/zoom/fine.py::build", "planet/zoom/fine.py::_courses", "planet/zoom/fine.py::_river_phase", tests/test_zoom_lod.py, "zoom 683193", "world dba204"]
---

## Description
**In plain words.** Daniel's v1.0 globe zooms like Google Earth: detail tiles are built on demand for what is on screen and
kept. Tiles next to each other are built minutes or days apart, so they must meet at their edges by construction. Today a fine
zoom is centred on its own spot with its own map, and near its edge it fades to the parent's bare, smooth surface: two
neighbours would show a grid of smooth stripes (8-10 px wide each side) and rivers whose bends jump at the edge. If this is
not done, the on-demand globe shows its tile grid everywhere you look closely. Plan: `docs/review/zoom/lod-plan-v2.md`
sections 1-2 (step 1).

`planet/zoom/lod.py` (lane 289) already names the tiles: levels 4 km (the 4,000 km section) / 1 km / 250 m / 25 m, 500 px tiles
on each cell's plane, one pixel lattice per level, parents, children, which tiles exist, which parent tiles a build reads.
What is left (2.2 of the plan):
- `lod.parent_mosaic`: the parent window cut from `lod.parent_sources` into one raster with the meta `fine._Parent` reads.
- A tile mode in `fine.build`: pixels from `lod.lattice` in `lod.frame(cell)`, not a centred Frame; save with `lod.tile_id`
  and a `tile` block in `zoom.json`.
- The edge fade goes to the place-keyed detailed surface (parent bicubic plus the place-keyed noise and ridges), not the bare
  parent surface; ramp ~6-8 px.
- A `river_phase` layer saved and read from the parent, so meanders continue across tiles; imposed-river threshold lowered for
  tiles; discharge on imposed courses anchored to the parent's.
- [ ] two sibling level-2 tiles of one section, built in either order, meet at the shared edge with a height-step distribution
      within 10% of their interior neighbour steps; rivers over the imposed threshold cross at the same place with discharge
      within 5%; a rebuilt tile is bit-identical
- [ ] time and peak per level re-measured (today's fine pass: 13-17 s, 3.4-3.5 GB per 500 px tile, plan 1.3)
