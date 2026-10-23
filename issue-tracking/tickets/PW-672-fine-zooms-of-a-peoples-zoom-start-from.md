---
id: PW-672
title: Fine zooms of a peoples zoom start from the wild plants again
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: zoom
effort: m
impact: low
found_by: zoompeoples
blocked_by: []
relates: [PW-667, PW-662]
refs: [planet/zoom_peoples.py, planet/zoom_fine.py, "zoom 859e74"]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-667's `planet zoom WORLD ... --peoples RUN` (planet/zoom_peoples.py) puts a peoples run's cleared land into a regional zoom (`land_use` layer, `meta.peoples`, satellite colours). A fine zoom of such a zoom (zoom_fine.py, 25-100 m/px) rebuilds its own plants and satellite from the world and knows nothing of `meta.peoples`, so a fine zoom of the demo zoom 859e74 shows wild forest where the parent has fields.

What to try: when the parent has `meta.peoples`, load the same run and call `ZP.apply` at the fine zoom's pixels (the cell fractions interpolate at any resolution; at 100 m the fields should become parcels of a few pixels and a village a cluster, so `VILLAGE_PEOPLE` and the parcel size (satellite.parcel_tone, 3 km) need a resolution rule: village ground and parcels in metres, not pixels). Carry `land_use` and `meta.peoples` into the fine zoom and give it its own id suffix as zoom_id does.
- [ ] a fine zoom of 859e74 shows fields, pasture and villages matching its parent
- [ ] a fine zoom of a zoom without peoples is unchanged

## Updates
- 2026-10-23: Created from inbox draft draft-zoom-peoples-fine-zooms.md (found by zoompeoples).
