---
id: PW-408
title: "Globe/map rivers flicker: small rivers draw as shimmering dotted lines (new 2026-10-16)"
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [viewer/index.html, viewer/relief.js]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Owner screencast (~/Screencasts/Screencast From 2026-10-16 17-30-26.mp4, map view of a run/world): every small river renders as a dotted line whose dots shimmer frame to frame, while the large highlighted river (white) stays solid. New today: most likely depth fighting between the river lines and the 3D relief surface (viewer/relief.js, landed 2026-10-16), or the rivers sitting on the old flat-sphere radius under the displaced surface. Fix the cause (draw rivers on the relief's displaced height with a small offset or polygonOffset, or depth-test off for the overlay layer); check globe and map, relief on and off, at several zoom levels.

## Updates
- 2026-10-16: Created from inbox draft draft-river-flicker-relief.md (found by daniel).
