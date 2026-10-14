---
id: PW-148
title: Landform bench levels are chosen per zoom, so overlapping zooms disagree
type: task
status: todo
parent: PW-005
subsystem: zoom
effort: s
impact: med
found_by: zoomland1
blocked_by: []
relates: [PW-010, PW-011]
refs: [planet/zoom_landforms.py, "zoom:366f51", "zoom:3bdcbb"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The zoom's bench levels (zoom_landforms: caprock and lava plateau anchors,
the escarpment's level e*, the caprock period) are one value per zoom, taken
from the zoom's own pixels (`Ctx.zone_level`: a percentile of the reshaped
surface; `Escarpment._level`: the median e* over the zoom's escarpment
cells; `Caprock._cap`: the median cap thickness). They must be horizontal
(a level varying across the land faster than its rivers fall meets them
with cliffs from below: thousands of up-steps that had to be breached), but
a different window over the same place picks different levels, so two
overlapping zooms (e.g. 500 km @ 1 km vs 250 km @ 0.5 km at -33.31,-12.41)
put the mesas' rims at different heights. The rest of the zoom is
deterministic in planet coordinates.

Try: levels from the coarse world rather than the zoom, e.g. quantised per
connected landform zone on the coarse grid (one level per zone, computed
from all of the zone's cells), or a level field smooth enough (gradient well
under the rivers' ~1 m/km) built from the coarse cells alone.
- [ ] two overlapping zooms of one caprock area share their bench levels
- [ ] breach cuts (zoom_landforms.breach) don't grow

## Updates
- 2026-10-14: Created from inbox draft draft-zoom-bench-levels-per-zoom.md (found by zoomland1).
