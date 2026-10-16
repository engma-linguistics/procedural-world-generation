---
title: Fine zoom streams below the imposed-river threshold are still D8 paths on the landscape pass
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: pw405
blocked_by: []
relates: [PW-405, PW-390]
refs: [planet/zoom_fine.py, viewer/zoom3d_mesh.js]
---

## Description
PW-405 smooths the imposed courses: the parent's rivers draining at least max(25 parent px, 1 km^2). Streams below that threshold appear only in the fine landscape pass's priority-flood D8 routing. Their receivers zigzag at the fine pixel scale, by +-1 px. That is not the 100 m switchbacks PW-405 fixed. The viewer's Chaikin smoothing hides most of it. It does show in plan view and in zoom_fine.planform at q >= 1 m^3/s: the planform metric counts a few switchbacks per 100 km there.

What to try (only if the owner sees it): route the finished surface with a D-infinity or multiple-flow-direction method for the river line only. Or lower the imposed threshold for fine parents, so that more of the network is drawn as smoothed courses.
