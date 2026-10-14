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
refs: [planet/tectonics/crust.py, planet/landform.py]
created: 2026-10-14
updated: 2026-10-14
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
- 2026-10-14: Created from inbox draft draft-rift-shoulder-uplift.md (found by landform).
