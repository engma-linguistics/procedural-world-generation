---
id: PW-547
title: "Planet viewer: projection options belong under Flat map; picking a 2D map breaks Globe"
type: task
status: done
parent: null
milestone: v1
subsystem: viewer
effort: s
impact: med
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-21
updated: 2026-10-21
---

## Description
Owner (2026-10-21): the planet viewer has Globe, Flat map and North up views. Flat map doesn't match any of the Map Projection options in the left pane, and choosing a 2D map there means clicking Globe no longer works. Move the Map Projection options under the Flat map view so there's one control, and make Globe always work.

## Updates
- 2026-10-21: Created.
- 2026-10-21: Done. Cause: the 2D map was a separate full-screen canvas (#projView) switched by its own '2D map' checkbox, independent of the Globe / Flat map mode, so it kept covering the globe. Now the projection menu sits beside Flat map (View section; the Map projection section is gone), the canvas shows only in Flat map with a non-equirect projection, and Globe hides it. Default stays Equirectangular, which is what Flat map always was: the live three.js map, the only one with overlays, hill shading and 3D relief (Equal Earth as default would drop those and break every mode=map recipe). 3D relief forces the live map (menu disabled while on). URL: mode=map&proj=NAME (old map2d= still read). Screens: docs/review/screens/pw547-*.png.
