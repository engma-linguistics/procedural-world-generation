---
id: PW-843
title: "Zoom 3D: one mouse-wheel step zooms wildly in or out"
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Seen on zoom 91bf86 in 3D mode.

## Updates
- 2026-10-25: Diagnosis (untested): OrbitControls zoomToCursor steps by a fraction of the distance to a far orbit target (maxDistance 3x size), and the tick loop forces camera.y above ground while the target stays put (zoom3d.js:435-438, 726, 971). Fix: re-target to the picked ground point, or scale the step by height above ground.
- 2026-10-25: Created.
