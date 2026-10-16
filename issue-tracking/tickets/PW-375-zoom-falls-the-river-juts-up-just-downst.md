---
id: PW-375
title: "Zoom falls: the river juts up just downstream of many waterfalls (seen in the 3D view)"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: med
found_by: owner
blocked_by: []
relates: [PW-341, PW-072]
refs: ["zoom:226c95", planet/zoom.py, viewer/zoom3d.js]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Owner 2026-10-16 (screenshot): in the zoom 3D view many waterfalls have the river rising in a step just below the fall
(zoom 226c95, 338 m drop at 38.659, 73.255). Agent started: find whether terrain or rendering, fix soundly.

## Updates
- 2026-10-16: Status in-progress -> done. Done (54e174a): rendering, not terrain (0 of 240 falls' stored water rises). Quads took the smaller-height-difference diagonal, drawing a ridge across the river below falls; new viewer/zoom3d_mesh.js splits quads along the river and pulls smoothed river lines to the valley floor. Climbing falls 17/17 -> 0 on 226c95; worst climb 400-1100 m -> 3 m.
- 2026-10-16: Created from inbox draft draft-fall-downstream-jut.md (found by owner).
