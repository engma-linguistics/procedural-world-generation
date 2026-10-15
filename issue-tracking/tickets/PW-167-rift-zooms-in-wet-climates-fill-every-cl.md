---
id: PW-167
title: Rift zooms in wet climates fill every closed half-graben with a lake (100+ small lakes)
type: task
status: done
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
- 2026-10-14: Status todo -> done. zoomland3: basin lakes by water balance (zoom_landforms.basin_lakes): runoff in vs open-water evaporation, upstream basins first so full ones spill into the next; closed lakes below the spill, dry flats where streams end; full ones under 5 km2 silt up; rift lakes only on the half-graben floors. f9b027 rebuilt: 155 -> 57 lakes (48 full, 3 closed, 7 silted), lake area 6620 -> 4350 km2; falls 42/28 unchanged.
- 2026-10-14: Created from inbox draft draft-rift-lake-count.md (found by zoomland2).
