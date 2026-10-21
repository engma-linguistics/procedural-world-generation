---
id: PW-477
title: "Static 2D maps: choose a centre point and a projection (equirectangular, Equal Earth, Mollweide, Lambert azimuthal equal-area, azimuthal equidistant, orthographic, stereographic) in export and the viewer"
type: task
status: done
parent: PW-244
milestone: v1
subsystem: store
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-100, PW-472]
refs: [planet/export.py]
created: 2026-10-20
updated: 2026-10-21
---

## Description
Owner 2026-10-20: a static 2D map should be centrable on any point of the globe, with a few projections, so any region can be shown centrally with little distortion.
- Export: --projection {equirect, equal-earth, mollweide, laea, aeqd, ortho, stereo} and --center lat,lon (oblique aspect for the whole-world projections, so any latitude can be centred). Optional --extent (deg or km) for regional maps. Applies to every raster layer (heights, class maps, splats) and reprojects features.geojson coordinates or adds projected x,y. Manifest records projection, centre and extent (a proj string where possible). Nearest-cell lookup for class maps, smooth interpolation for heights.
- Viewer (after PW-472/473 land): a 2D map mode with the same choices and a click-to-centre.
- No new heavy dependency without need; pure numpy forward/inverse formulas are fine (pyproj only if it already exists in the env).

## Updates
- 2026-10-21: Status todo -> done. Viewer part done on branch worktree-agent-a0fc90d9213631395: a Map projection section (viewer/projmap.js, a JS port of planet/projection.py checked against it by tests/test_projection_js.py) draws the current layer in any of the seven projections, click to centre, extent, graticule, PNG download; client-side, no endpoint. Remaining polish in an inbox draft (overlays, smoothing).
- 2026-10-20: Export part done on branch worktree-agent-a007f54365b6fcec5: `planet export --projection/--center/--extent` (worlds and zooms; planet/projection.py pure numpy; layouts.map, coverage layer + nodata, features_map.geojson; README). Viewer part still open (2D map mode with the same choices, click-to-centre; planet/projection.py has the forward/inverse formulas, JS would need a port or a /api endpoint).
- 2026-10-20: Created.
