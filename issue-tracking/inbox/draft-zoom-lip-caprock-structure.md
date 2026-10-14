---
title: Zoom lips should read the caprock's thickness and the soft rock under it
type: task
status: todo
parent: PW-010
subsystem: zoom
effort: s
impact: med
found_by: stratarock
blocked_by: []
relates: [PW-136, PW-010]
refs: [planet/zoom.py, planet/landform.py, planet/surface.py]
---

## Description
Since PW-136 (option B), `surface_rock` is the exposed stratum, so the
zoom's `lip_resistance` already sees a sandstone or limestone caprock over
shale (world f59dd6 @ 408 Myr: lips on sandstone-over-shale went from 0.20
to 0.70; mean lip resistance of a caprock-area zoom at 41.0, -156.5 from
0.57 to 0.67). But `lip_resistance` still falls back to the basement when
the *whole cover* is under 0.5 km, and otherwise ignores the structure.

The zoom has what it needs per cell (`strata_top_km`, `strata_next`,
`sediment_cover`): a hard top thinner than the fall over soft rock is the
classic waterfall (Niagara: ~25 m of dolomite over shale; the soft rock is
undercut, the fall keeps its step and retreats as a gorge). Suggested:
- lip held by the top stratum while the fall is about as high as the
  caprock is thick or more, with the gorge length / retreat set by how soft
  `strata_next` is;
- the basement fallback keyed to the cover under the caprock, not the
  whole cover.
Not done in the stratarock branch because zoomland1 owns zoom.py (escarpment,
caprock and lava plateau synthesis); best folded into that work or right
after it.
