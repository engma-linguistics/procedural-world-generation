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
updated: 2026-10-21
---

## Description
PW-187 changes the run (vegetation's ground cover in erosion, NPP in weathering; goldens updated), so every existing run replays differently (`slice` refuses), and their keyframes lack the `tree_cover`/`vegetation`/`npp` layers that `timeline.world_from_frame` (the viewer's Zoom button) now reads: building a world from an old run fails with "too old". Remake the showcases (docs/coordination.md recipes) and delete the old ones; remake the Earth world (the veg branch made fe2af4 with vegetation layers; dc3732 has none) and point docs at it.

## Updates
- 2026-10-21: Owner 2026-10-21: when v1 work is done, make 4 random-seed L6 and 4 random-seed L7 planets (full chain: run, time zoom, finished world, a few zooms) to view, as one batch.
- 2026-10-15: Created from inbox draft draft-remake-outputs-after-vegetation.md (found by veg).
