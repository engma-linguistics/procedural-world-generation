---
id: PW-129
title: Nested fine zoom (~100-250 m/px) of a small area of a zoom, for close-up and 3D viewing
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-072]
refs: [planet/zoom.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
Owner: an even more granular pass of the area around a point of interest (a waterfall, a valley), tied into the 3D view (PW-072). A zoom of a zoom: 25-50 km across at 100-250 m/px, conditioned on the parent zoom's heights, rivers, falls, lakes and rock the way zooms are conditioned on worlds; falls, plunge pools and gorges resolved properly at that scale.

## Updates
- 2026-10-16: Owner decisions: finest view ~25 km (500 px = 50 m/px default, try 1000 px = 25 m/px), plus 50 km at 100 m; progressive nesting world -> zoom -> fine -> finer (not from a world; fine of fine allowed); fall heights and volcanoes keep the parent's values exactly. Tree sprites not yet; warn at 25 m/px. River flights nice to have. See proposal 'Owner decisions'.
- 2026-10-16: Status todo -> needs-decision. Design ready: docs/proposals/nested_fine_zoom.md (zoom_fine.py from a parent zoom, falls as lip/face/gorge/plunge pool, ~8-10 s per fine zoom; shown as a second 3D tile). Three owner questions at its end.
- 2026-10-16: Design written (viewer-3d branch): docs/proposals/nested_fine_zoom.md. A separate pass, planet/zoom_fine.py, takes a finished parent zoom as its coarse input (not zoom.build on the parent's pixels: that would fake world fields and redesign the parent's falls): bicubic parent heights plus 3D-position noise with each parent pixel's mean kept; the parent's rivers, lakes and falls imposed (each fall laid out as lip, full-drop face, retreat gorge with walls at lip level, plunge pool); the zoom's stream-power loop with a channel head (threshold hillslopes ~30-35 deg below ~0.1-0.5 km2) and talus; glaciers, climate, vegetation and satellite redrawn. Writes an ordinary zoom dir plus a parent_zoom block; POST /api/zoom {zoom, lat, lon, size_km, res_km}; ~8-10 s, ~18 MB. 3D: a second Tile placed by exact reprojection, a hole cut in the parent's mesh and sea, per-tile textures; groundY already asks the finest tile, so river flights pass through it. Three owner questions at the end (size, from-world, fall heights).
- 2026-10-14: Created.
