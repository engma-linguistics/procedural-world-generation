---
id: PW-225
title: "Zoom viewer: 'Relief' layer replaced by 'Satellite'; decide if a hypsometric relief layer is still wanted"
type: task
status: todo
parent: null
subsystem: viewer
effort: xs
impact: low
found_by: satview
blocked_by: []
relates: [PW-083]
refs: [viewer/zoom.html, planet/zoom.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-083 made the zoom's `preview.png` the satellite view (summer, hill-shaded, with rivers), so the zoom
viewer's old "Relief" layer (which drew preview.png: a height x rain tint, lakes, marshes, rivers) became a
duplicate and was replaced by "Satellite" (the default layer; season picker, clouds). The hypsometric
"map-style" relief look is gone from zoom.html (the Height and Hillshade layers remain, and coarse.png
still uses `zoom.tint`).
Options: A) leave it (lean: the satellite view, Height and Hillshade cover it); B) bring back a "Map"
layer drawn in JS from height and rain (`zoom.tint`'s ramps), ~30 lines.

## Updates
- 2026-10-15: Status needs-decision -> todo. Coordinator decision (north star, cheap and loses nothing): bring the hypsometric relief back as a non-default layer next to Satellite.
- 2026-10-15: Created from inbox draft draft-satellite-zoom-relief-layer.md (found by satview).
