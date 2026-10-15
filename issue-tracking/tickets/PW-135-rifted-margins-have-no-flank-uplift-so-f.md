---
id: PW-135
title: Rifted margins have no flank uplift, so few great escarpments stand high
type: task
status: todo
parent: PW-005
subsystem: tectonics
effort: m
impact: med
found_by: landform
blocked_by: []
relates: [PW-010]
refs: [planet/tectonics/crust.py, planet/landform.py, planet/tectonics/isostasy.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
The escarpment class needs a rifted, passive coast and a plateau to step up
to (>= 300 m at the scarp's retreat distance, `landform.ESCARPMENT_M`). On
the L7 seed-21 run it covers 0.4% of land (rift ages 50-340 Myr, median
126). Many rifted margins don't qualify because stretching only thins the
crust (lowering it), while on Earth rift flanks are lifted by flexural
unloading and heating (1-2 km shoulders: the Drakensberg, the Western
Ghats, Eastern Australia's divide), and that high edge is what retreats as
the great escarpment. Try a flexural flank uplift alongside
`crust.rift_stretching` (a broad, decaying `lift`-like term on the cells
next to the stretched belt), then recheck escarpment share and heights.

## Updates
- 2026-10-15: Merged inbox draft draft-rift-flank-flexure.md ("Rift flanks need flexural unloading uplift (negative-load flexure)", found by tect2).
  PW-054 added `isostasy.subsidence`: flexural moats beside thickened crust
  (positive loads only) and a McKenzie thermal term that lifts the stretched
  cells themselves (~0.8 km at beta 1.5) and lets them sag over 63 Myr. The
  flanks of a rift still get nothing: on Earth a rift's thinned crust is a
  negative load that the stiff plate spreads, lifting the shoulders 1-2 km
  (Drakensberg, Western Ghats, Eastern Australia), which is what PW-135 needs
  for great escarpments.
  
  The same formula extends naturally: root R = ROOT x (thick - CONT_KM) for
  recently rifted continent (negative), weighted by its age (exp(-age / ~200
  Myr), so old, relaxed margins don't keep a permanent bulge), and apply the
  positive part of flexure x (R - smooth(R)) on the cells that aren't
  themselves thinned. Careful: rifted-margin crust (12-18 km) is a huge
  negative load; restrict to stretched crust with a rift record, and check the
  coastal land share and the escarpment class (landform) at L6 and L7.
  - [ ] escarpment class share and heights re-measured (PW-135)
- 2026-10-14: Created from inbox draft draft-rift-shoulder-uplift.md (found by landform).
