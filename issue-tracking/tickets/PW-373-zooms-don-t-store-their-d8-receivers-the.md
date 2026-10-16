---
id: PW-373
title: Zooms don't store their D8 receivers - the 3D view guesses the rivers' directions
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: viewer-3d
blocked_by: []
relates: [PW-129, PW-072]
refs: [planet/zoom.py, viewer/zoom3d.js, viewer/zoom3d_fly.js]
created: 2026-10-16
updated: 2026-10-16
---

## Description
A zoom stores `discharge` and `drainage_area` but not the receivers its landscape pass routed
along. The 3D view rebuilds them (`Tile.flow` in zoom3d.js: the steepest drop in water surface
among neighbours carrying at least as much water), and everything after depends on that guess: the
river lines, the falls' reaches, the shimmer's flow directions and the "fly along a river" courses
(zoom3d_fly.js). Where the guess and the zoom disagree (flat lake shores, braided deltas) a course
can wander or stop early. The nested fine zoom (PW-129, docs/proposals/nested_fine_zoom.md) needs
the parent's rivers too.

Fix: save the final receivers as a uint8 layer (`receiver`: the D8 slot 0-7, 255 = none, as runs'
`nbr_slot` layers), and have zoom3d.js use it when present.
- [ ] `receiver` layer in new zooms; zoom3d.js and zoom3d_fly.js read it

## Updates
- 2026-10-16: Created from inbox draft draft-zoom-receiver-layer.md (found by viewer-3d).
