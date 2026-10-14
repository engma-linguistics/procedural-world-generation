---
id: PW-167
title: Rift zooms in wet climates fill every closed half-graben with a lake (100+ small lakes)
type: task
status: todo
parent: PW-005
subsystem: zoom
effort: s
impact: low
found_by: zoomland2
blocked_by: []
relates: [PW-011]
refs: [planet/zoom.py, planet/zoom_landforms.py, "zoom c34d7a"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-011's rift keeps its closed basins (Synth.basins: not breached, except
by rivers >= BASIN_THROUGH_Q) and, where precipitation is above ~600-1200
mm (Rift.lakes), every closed depression at least LF_LAKE_M deep and
LF_LAKE_KM2 big becomes a lake filled to its spill level (zoom.build, final
drainage). Zoom c34d7a (East-African-like rift at -14.8, -11.8, 767 mm)
gets 130 lakes: the long graben lakes look right, but many are small
depressions in the blocks' fluvial texture. Lakes ignore the water balance
(a closed basin in a semi-arid rift would be a salt lake well below its
spill level, or a playa).
Try: lakes only where the basin's catchment runoff exceeds its evaporation
(the coarse lake_evap / runoff fields), levels below spill for closed ones,
and fill (not lake) depressions under ~5 km2 outside the half-graben floors.

## Updates
- 2026-10-14: Created from inbox draft draft-rift-lake-count.md (found by zoomland2).
