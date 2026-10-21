---
id: PW-537
title: Zoom lakes on high ground draw tilted, lumpy water surfaces with ragged edges and floating slivers (60b7e1)
type: task
status: todo
parent: null
milestone: v1
subsystem: zoom
effort: s
impact: med
found_by: owner
blocked_by: []
relates: []
refs: [docs/review/screens/lakes-tilted-60b7e1.png]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Owner 2026-10-21, zoom 60b7e1 (world 28442c, 1 km/px), 3D view: small lakes up on a slope have water surfaces that are not level (they tilt with the ground and one bulges like a tent), the shore is ragged and spiky, and two small water slivers float beside the river below the upper lake. Also the river there zig-zags as a pixel staircase. Find out whether the lake level stored by the zoom is per-pixel rather than one level per lake, whether the viewer drapes the water mesh on the ground or interpolates water level across the shore into dry neighbours, and where the slivers come from. Fix so each lake is one flat surface at its spill level, clipped at the shore; no orphan water bits.

## Updates
- 2026-10-21: Created.
