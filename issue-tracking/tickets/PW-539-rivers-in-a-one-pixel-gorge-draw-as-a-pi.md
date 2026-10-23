---
id: PW-539
title: Rivers in a one-pixel gorge draw as a pixel staircase in the zoom 3D view
type: task
status: todo
parent: PW-516
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: pw537
blocked_by: []
relates: [PW-537, PW-649]
refs: [viewer/zoom3d.js, viewer/zoom3d_mesh.js, "zoom 60b7e1"]
created: 2026-10-21
updated: 2026-10-23
---

## Description
The river in zoom 60b7e1 zigzags a pixel either side of its line in 3D. It is not a smoothing bug: the river is painted on the texture from the D8 path (hugChaikin), and in a gorge one pixel wide the path IS the valley floor, so the smoothing holds the line to the zigzag.

Tried in PW-537: pre-smoothing the path with a [1 2 1]/4 filter before Chaikin cut the line's total turning from 25 to 6 rad, but then the line rides up to 111 m above the path's floor on the gorge sides. Holding it to the original path's floor (so the hug references the real floor) brings the zigzag back (25.3 rad, 1.8 m ride). So smoothing alone can't work here.

Options: (a) carve the zoom's terrain along a smoothed river course so the floor itself is smooth (zoom side; fits PW-488, the fine-zoom staircase); (b) draw the river as a ribbon mesh draped on the ground, with the gorge floor re-sampled on the smoothed line (viewer side, larger).
- [ ] the river in 60b7e1 below the upper pool turns less than ~1.5x the straight-line bearing change, without riding up the valley sides

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-21: Created from inbox draft draft-zoom3d-river-staircase.md (found by pw537).
