---
id: PW-327
title: "Zoom: no shoreface; the sea floor is at the coarse cell's depth a pixel off the shore (no shallows for seagrass, reefs, beaches)"
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: med
found_by: coastal-life
blocked_by: []
relates: [PW-188, PW-097]
refs: [planet/zoom.py, planet/zoom_coastal.py, "run:a1d3b9@900Myr(22.13,-25.66)"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
In a zoom of run a1d3b9 @ 900 Myr (`planet finish a1d3b9 --at 900`, then a 1000 km @ 2 km zoom at 22.13, -25.66; a warm inland sea whose cells average ~40 m deep) the shallowest 1% of the sea pixels are ~19 m deep and only 2% are under 20 m: the sea floor next to the coastline sits at about the interpolated coarse depth instead of shoaling to 0 at the shore. Real coasts have a shoreface: depth grows with distance offshore roughly as h = A x^(2/3) (Dean's equilibrium profile; A ~0.1 m^(1/3) for fine sand: ~10 m at 1 km, ~20 m at 3 km), flatter still on muddy tidal coasts and reef flats. Without it the zoom has few pixels shallow enough for seagrass (Duarte's limit ~15-25 m) or reef growth (~20-40 m in clear water) and no beach or tidal-flat shallows to colour, though the world's cells give the region ~30% seagrass and ~15% reef (PW-188's zoom places them on each pixel's own depth, so this limits them honestly).

Fix in the zoom's coastline/sea-floor pass: blend the sea pixels near the shore toward a Dean profile from the coastline distance (inside_distance on the sea), keeping each coarse cell's mean depth (deepen the outer part slightly). Coordinate with the zoom.py owners (PW-125 creep/landscape pass), and with PW-097 (beaches vs cliffs: a steep rocky shore keeps deep water close in).
- [ ] sea pixels within ~5 km of a sandy or muddy shore shoal to < 10 m; cell means kept
- [ ] re-check that region: seagrass and reef pixels close to the world's shares

## Updates
- 2026-10-15: Created from inbox draft draft-zoom-shoreface-shallows.md (found by coastal-life).
