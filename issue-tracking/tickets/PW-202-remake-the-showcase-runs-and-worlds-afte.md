---
id: PW-202
title: Remake the showcase runs and worlds after the vegetation merge
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: store
effort: s
impact: med
found_by: veg
blocked_by: []
relates: [PW-187]
refs: []
created: 2026-10-15
updated: 2026-10-23
---

## Description
PW-187 changes the run (vegetation's ground cover in erosion, NPP in weathering; goldens updated), so every existing run replays differently (`slice` refuses), and their keyframes lack the `tree_cover`/`vegetation`/`npp` layers that `timeline.world_from_frame` (the viewer's Zoom button) now reads: building a world from an old run fails with "too old". Remake the showcases (docs/coordination.md recipes) and delete the old ones; remake the Earth world (the veg branch made fe2af4 with vegetation layers; dc3732 has none) and point docs at it.

## Updates
- 2026-10-23: Owner 2026-10-24: old outputs deletable; deleted everything except tonight's L7 batch, the Earth world 577526 and the nine overturning reference worlds (119973 28442c 607540 81aced 7082f5 d14b89 a5a387 dad91b c00ebf).
- 2026-10-23: 2026-10-23 night L7 batch on main 59b83d7 (PW-576 mature start + CO2 stock, PW-596 winds, PW-594 island walls, PW-634 full-flora pick), planet make --level 7, random seeds, 1 Gyr: run a6643c @1000 tz fc82c2 world 1df1c3 (peoples run 9dc3d3); run 3a0480 @964 tz 141402 world afcee8 (peoples 6920a9); run 0d1889 @944 tz 7deb8a world 1f0505 (peoples f5958f); run 89bea8 @928 tz 6e96d2 world 3e9e7d (peoples 3433f0). Each world also has resources and coast layers; 4 zooms each. Older showcase worlds predate the flora fix (PW-634) and PW-576; candidates for cleanup once the owner has looked.
- 2026-10-23: Merged PW-498 (closed as duplicate; PW-597 triage). Time zooms made before glacial carving (PW-037) can't be finished by `planet finish` ("made before glacial carving; run it again"); as of 2026-10-20 that was every time zoom on the main data root: 6d0ed0 (PW-471's Earth showcase), 098d5d, 080df3, 86c513, 755514, 7d5027, 98ee98, be3362. The 2026-10-22 L6 batch above made fresh carved time zooms. Remaining from PW-498: delete the pre-carving time zooms (`planet delete`) unless one is worth re-running from its run.txt remake line (~6 min per Myr at L6, 30-40 at L7), and check the one-command flow (make.py, PW-479) doesn't pick an old zoom.
- 2026-10-22: 2026-10-22 v1 L6 batch on main 3798b6a (planet make --level 6, random seeds, 1 Gyr, 300 kyr time zoom, interglacial now, 4 zooms). #1 run 0ceebf @800 Myr, tz 1224c2, world 119973, zooms 4bd1cd 36ecb0 a28b44 9d7c44. #2 run 172922 @656, tz d6a5c5, world 81aced, zooms b615dd e0a4d6 eb379d 47d22c. #3 run 343058 @308, tz cd972b, world 7082f5, zooms ea83b7 a5d25d 8d4e8a 32051f. #4 run 2b0b65 @404, tz 24420d, world a5a387, zooms 24d30f 6e9dfd 91e9ee 321bae. Owner asked for L6 only this round; L7s from the 2026-10-21 batch stand.
- 2026-10-21: Owner 2026-10-21: when v1 work is done, make 4 random-seed L6 and 4 random-seed L7 planets (full chain: run, time zoom, finished world, a few zooms) to view, as one batch.
- 2026-10-15: Created from inbox draft draft-remake-outputs-after-vegetation.md (found by veg).
