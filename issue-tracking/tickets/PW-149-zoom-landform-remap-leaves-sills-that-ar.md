---
id: PW-149
title: Zoom landform remap leaves sills that are cut as narrow gorges; lava steps look stippled
type: task
status: done
parent: PW-005
subsystem: zoom
effort: m
impact: low
found_by: zoomland1
blocked_by: []
relates: [PW-010]
refs: [planet/zoom_landforms.py, "zoom:6a4870", "zoom:b2165d", docs/review/landforms/zoom_lava_before_after.png]
created: 2026-10-14
updated: 2026-10-14
---

## Description
After the landform remap (zoom_landforms) about 0.5% of a zoom's pixels
stand above a donor along their flow path; `breach()` cuts them through
(inside the classes' reach), up to a few hundred metres in places (world
800c99, 250 km @ 0.5 km zooms: 500-1500 px cut by > 5 m, p99 100-400 m).
Sources: the class weight tapering across a band (a river leaving the zone
sideways regains height), the ramp next to designed falls' courses, and the
cell-mean correction. Most look like water gaps or slot gorges, but some are
1-px trenches. Also the lava plateau's benches alias into a stippled texture
at 0.5-1 km (zoom 6a4870, docs/review/landforms/zoom_lava_before_after.png),
and at 2 km/px benches of ~100 m are hardly visible at all.
Try: propagate a class's weight down the drainage on channels (a river
leaving the zone keeps the zone's offset until it rejoins the land around),
and widen lava cliff faces (`Strata.face`) with the pixel size.

## Updates
- 2026-10-14: Status todo -> done. cut(): breach cuts widened into gaps (walls at GAP_GRAD); fold structures keep big rivers graded (water gaps); bench cliffs anti-aliased (min face width, smoothed cliff line, sub-pixel bands fade; rivers keep sharp steps); lava step at least VISIBLE_PX wide. Weight propagation down channels not done.
- 2026-10-14: Created from inbox draft draft-zoom-landform-breach-gorges.md (found by zoomland1).
