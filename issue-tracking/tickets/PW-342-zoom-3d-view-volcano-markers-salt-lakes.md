---
id: PW-342
title: "Zoom 3D view: volcano markers, salt lakes and glaciers' own look"
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: zoom3d
blocked_by: []
relates: [PW-072]
refs: [viewer/zoom3d.js, viewer/zoom.html]
created: 2026-10-16
updated: 2026-10-16
---

## Description
The zoom 3D view (PW-072) draws terrain, sea, lakes, rivers and the falls, but leaves out
things the 2D map shows:
- volcanoes: the 2D Volcanoes overlay (active, extinct, below the sea) has no 3D pins; the
  checkbox does nothing in 3D. They could use the falls' pin-and-label code
  (`Zoom3D.buildPins`) with the 2D card.
- salt lakes and salt pans: every lake is one blue; the 2D map's fresh / salt split
  (cyan / pink, white pans) would carry over by lake kind (`stats.largest_lakes`).
- lakes keep their pixels' staircase in the colour texture (the 2D colours paint lake
  pixels blue, bilinearly scaled), visible at 1-4 km/px next to the smooth 3D shore; the
  texture could paint lake pixels in the land's colour and leave the water to the lake mesh.
- [ ] volcano pins with cards in 3D
- [ ] salt lakes and pans coloured as in 2D

## Updates
- 2026-10-16: Created from inbox draft draft-zoom3d-volcanoes-salt-lakes.md (found by zoom3d).
