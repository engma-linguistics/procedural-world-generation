---
id: PW-125
title: "Zoom: remaining undesigned drops on mid-size streams, coarse-zoom hanging joins, edge steps"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomsmalls
blocked_by: []
relates: [PW-070, PW-069]
refs: [planet/zoom.py, "zoom:031ecf", "zoom:f2b532", "zoom:afdaf5"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
After zoomsmalls (creep no longer lifts stream beds, contrast filter in `waterfalls()`), 20 test zooms
still list 32 undesigned drops (14 >= 100 m), mostly on 50-300 m3/s streams that drop 100-490 m over
3-5 km in one concentrated step. Worst: zoom:031ecf px (457, 470), 490 m at 96 m3/s. Without the
contrast filter there are ~300 such steps (149 >= 100 m), so the terrain still has them.
- On the 4 km zoom f2b532, 5 tributaries still join a reach with falls in a hanging step (PW-069's
  "hanging joins mid-falls"); on finer zooms none were left.
- Steps into the region's edge (edge pixels are fixed at the target surface) are no longer listed
  (`WF_EDGE_PX` = 8), but are still in the terrain (e.g. afdaf5 cols 4-10, 270-320 m).
- In the synthetic `_escarpment_world(1.2, 400)` a few cascades still realise ~0.1 m (4 of ~13).
Measure with a per-zoom count of `waterfalls(..., top=100000)` kinds; find which floor/cap or
re-routing leaves each step (the zoomsmalls report has the diagnostic approach).

## Updates
- 2026-10-14: Created from inbox draft draft-zoom-remaining-undesigned-drops.md (found by zoomsmalls).
