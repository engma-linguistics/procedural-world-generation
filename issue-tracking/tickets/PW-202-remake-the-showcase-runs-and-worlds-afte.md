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
updated: 2026-10-22
---

## Description
PW-187 changes the run (vegetation's ground cover in erosion, NPP in weathering; goldens updated), so every existing run replays differently (`slice` refuses), and their keyframes lack the `tree_cover`/`vegetation`/`npp` layers that `timeline.world_from_frame` (the viewer's Zoom button) now reads: building a world from an old run fails with "too old". Remake the showcases (docs/coordination.md recipes) and delete the old ones; remake the Earth world (the veg branch made fe2af4 with vegetation layers; dc3732 has none) and point docs at it.

## Updates
- 2026-10-22: 2026-10-22 v1 L6 batch on main 3798b6a (planet make --level 6, random seeds, 1 Gyr, 300 kyr time zoom, interglacial now, 4 zooms). #1 run 0ceebf @800 Myr, tz 1224c2, world 119973, zooms 4bd1cd 36ecb0 a28b44 9d7c44. #2 run 172922 @656, tz d6a5c5, world 81aced, zooms b615dd e0a4d6 eb379d 47d22c. #3 run 343058 @308, tz cd972b, world 7082f5, zooms ea83b7 a5d25d 8d4e8a 32051f. #4 run 2b0b65 @404, tz 24420d, world a5a387, zooms 24d30f 6e9dfd 91e9ee 321bae. Owner asked for L6 only this round; L7s from the 2026-10-21 batch stand.
- 2026-10-21: Owner 2026-10-21: when v1 work is done, make 4 random-seed L6 and 4 random-seed L7 planets (full chain: run, time zoom, finished world, a few zooms) to view, as one batch.
- 2026-10-15: Created from inbox draft draft-remake-outputs-after-vegetation.md (found by veg).
