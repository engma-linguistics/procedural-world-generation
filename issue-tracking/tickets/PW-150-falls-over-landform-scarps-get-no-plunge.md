---
id: PW-150
title: Falls over landform scarps get no plunge pool or gorge, and most go unlisted
type: task
status: done
parent: PW-005
subsystem: zoom
effort: s
impact: med
found_by: zoomland1
blocked_by: []
relates: [PW-010]
refs: [planet/zoom.py, planet/zoom_landforms.py, "zoom:b2165d", "zoom:9e2ba9"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Since PW-010 the zoom's landform classes make many falls where rivers cross
a scarp or bench cliff (world 800c99, 11 fixed zooms: 44 -> 154 falls >= 30 m,
16 -> 77 >= 100 m). Only designed reaches (knickpoints) get a lip, gorge and
plunge pool; the emergent ones are listed as kind "drop", with no plunge pool,
and `stats.waterfalls` keeps only the top 5 by power, so the preview and the
viewer mark at most 5 of the ~30 falls along an escarpment (zoom 9e2ba9).
Try: give landform falls (a drop at a class cliff, weight > 0.5) their own
kind ("scarp" / "bench") with a plunge pool at the foot, and list more of
them (e.g. top 5 overall plus the top few per class), or a separate
`stats.landform_falls` count/height summary.

## Updates
- 2026-10-14: Status todo -> done. stats.falls lists every fall >= 30 m (kind lip/scarp/bench/lake outlet/drop), falls_count; waterfalls keeps top 5; scarp/bench falls get plunge pools; scarp_gorges() retreats class-cliff falls into gorges; preview marks all falls.
- 2026-10-14: Created from inbox draft draft-zoom-landform-falls-listing.md (found by zoomland1).
