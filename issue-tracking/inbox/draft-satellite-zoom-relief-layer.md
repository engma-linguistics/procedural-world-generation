---
title: "Zoom viewer: 'Relief' layer replaced by 'Satellite'; decide if a hypsometric relief layer is still wanted"
type: task
status: needs-decision
parent: null
subsystem: viewer
effort: xs
impact: low
found_by: satview
blocked_by: []
relates: [PW-083]
refs: [viewer/zoom.html, planet/zoom.py]
---

## Description
PW-083 made the zoom's `preview.png` the satellite view (summer, hill-shaded, with rivers), so the zoom
viewer's old "Relief" layer (which drew preview.png: a height x rain tint, lakes, marshes, rivers) became a
duplicate and was replaced by "Satellite" (the default layer; season picker, clouds). The hypsometric
"map-style" relief look is gone from zoom.html (the Height and Hillshade layers remain, and coarse.png
still uses `zoom.tint`).
Options: A) leave it (lean: the satellite view, Height and Hillshade cover it); B) bring back a "Map"
layer drawn in JS from height and rain (`zoom.tint`'s ramps), ~30 lines.
