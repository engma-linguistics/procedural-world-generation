---
id: PW-342
title: "Zoom 3D view: volcano markers, salt lakes and glaciers' own look"
type: task
status: done
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
- [x] volcano pins with cards in 3D
- [x] salt lakes and pans coloured as in 2D
- [x] lake pixels painted in land colour in the texture

## Updates
- 2026-10-16: Status in-progress -> done. Done: 3D volcano pins with 2D cards; zoom stores lake_kind (fresh/salt/pan) used by the 3D view and satellite colours; lake pixels painted in land colour (no staircase).
- 2026-10-16: Status todo -> in-progress. Agent started.
- 2026-10-16: Created from inbox draft draft-zoom3d-volcanoes-salt-lakes.md (found by zoom3d).
- 2026-10-16: Done on the zoom3d branch (viewer/zoom3d.js, zoom.html): volcano pins and 2D card, lake kinds from a new zoom `lake_kind` layer (planet/zoom.py), lake pixels in land colour. Screenshot docs/review/viewer/zoom3d_volcano.png.
