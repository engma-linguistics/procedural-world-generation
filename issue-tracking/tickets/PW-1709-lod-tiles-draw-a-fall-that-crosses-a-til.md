---
id: PW-1709
title: "LOD tiles: draw a fall that crosses a tile edge from one gorge block keyed by its lip (design for PW-1698)"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: l
impact: med
found_by: lane297
blocked_by: []
relates: [PW-1698, PW-1695, PW-1694, PW-1705]
refs: ["planet/zoom/fine.py::build", "planet/zoom/fine.py::_fall_chain", "planet/zoom/fine.py::_gorge_path", "planet/zoom/fine.py::_parent_gorge", "planet/zoom/lod_build.py::carve_block", "planet/zoom/lod_build.py::edge_surface", "planet/zoom/lod.py::parent_mosaic", planet/zoom/falls.py, tests/test_zoom_lod_build.py, docs/review/zoom/lod-plan-v2.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** On the zoomable globe a waterfall whose gorge runs within ~8-10 pixels of a tile's edge is still
left out of both tiles (PW-1698): the river runs on with no drop and no gorge, at that level and every finer one. Lane
297 looked at doing it and stopped: it is not a local change to the gorge code but a new path through it, so this is
the design to build it from. If never done, some falls on the globe vanish depending on where the tile grid falls.

Why it is large. `fine.build` draws a fall from the parent's chain (`_fall_chain`) as pixel sequences of the tile's
own built area: `seq` (lip to foot along the tile's imposed course), the cut window `ib`, the plunge pools (`pool`,
`pool_d`), the walls (`g_wall`, `g_floor`, `g_out`, used again after the landscape pass to clip walls to their rims),
`course`/`c_rec` (the course pinned down the gorge) and the fall's stats (`px`, `foot_px`, `pool_px`, `gorge_path`).
All of it needs the lip, the foot and the whole cut inside the built area, which is why a chain within `ramp` of the
edge is skipped (`fine.build`, "the parent's falls in the region"). The fall's links also change how the course is laid
(`fall_links`, `lips` in the course and node-phase code), so a tile that doesn't draw the fall lays a different course
there than one that does.

Design (as the volcanoes, PW-1695, and the edge blocks, PW-1694):
1. **A gorge block keyed by the lip's place.** For each parent fall in a tile's mosaic whose chain comes within the
   ramp of the tile's built area and isn't wholly inside it: a square on the level's lattice centred on the lip's
   lattice pixel, as wide as the chain plus `margin` (the gorge code's own wall reach) plus `STRIP_PX` round it.
   Carve it with `fine.build(..., shape=, carve=True)` from `lod.parent_mosaic(key, sources, r)` (the same window
   whichever tile asks), the fall wholly inside it, so it is drawn there as today.
2. **Return the fall, not only the ground.** `carve=True` returns, besides `hw`, what the gorge drew, on the block's
   lattice pixels: the held pixels and their heights *before* the landscape pass (floor, walls, headwall), the walls'
   `g_floor`/`g_out`, the pools and depths, `seq` and its receivers, and the fall's stats entry.
3. **Paste it into every tile it touches**, before the landscape pass (where the gorge is drawn today): the held
   pixels set and fixed, the pools as pools, `seq`'s pixels as course with their receivers (joined to the tile's own
   course where `seq` leaves the built area), and the parent link marked in `fall_links` so the course is laid the
   same way as in the block. The edge strips and corner blocks paste the same fall, so the edge fade meets it.
4. **Stats and children.** List the fall in every drawing tile's stats with `owner` (the tile holding the lip, as
   volcanoes); `lod.parent_mosaic` de-duplicates falls by the lip's lat/lon (it does so for volcanoes, not for falls),
   so a level-3 tile reading two parents gets it once.
- [ ] a fall placed across the shared edge of two synthetic sibling tiles: drawn in both (its drop on the lip's side,
      the gorge on both), no step across the edge beyond the same line with no seam (PW-1697's rule), listed once
      per tile with one `owner`, once in a child's mosaic
- [ ] a rebuilt tile bit-identical; dba204 tiles with a fall near an edge counted before and after

## Updates
- 2026-11-11: Lane 303: not started (the lane went on PW-1713 and on the 11-11 out-of-memory crash, fixed in fine_meander._ease). Still the whole design, with lane 300's two findings folded in: (1) a gorge block carries its own rims: carve it as today's fine.build does, wall clipping included (the g_wall loop after the landscape pass, against the block's own finished ground), and return the clipped walls, floor, headwall, pools and seq; a pasting tile holds them and lets its pass shape only what lies beyond the rims (a step at the rim is the price; the block's rim ground could be faded into the tile over a few px). (2) a block's size is the fall's reach: hf + 2 (drop + 200 m) / tan(55 deg) + 2 px round the chain, so a big fall's block is several hundred px; carve it at most once per process (an lru cache keyed by the lip's place and level) and cap its side (skip or flatten a fall whose block would pass ~1,000 px, logged). PW-1713's path is the model for pasting: lod_build.line_surface maps a carved block's one-pixel courses onto a tile (_block_courses, _to_tile) and fine._paste_courses holds them and joins the tile's own; the fall's seq and its fall_links would go the same way. Effort stays l (a lane of its own).
- 2026-11-11: Created from inbox draft draft-lod-falls-on-blocks-keyed-by-lip.md (found by lane297).
