---
id: PW-1345
title: "Zoom vegetation classify calls is_land on pixels: raises when a land pixel is at or below sea level"
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: zoom
effort: xs
impact: low
found_by: lane127
blocked_by: []
relates: [PW-1301]
refs: ["planet/vegetation.py::classify", "planet/geo.py::is_land", "planet/geo.py::_grid_of", "planet/zoom/vegetation.py::compute", "planet/zoom/stage_landscape.py::landscape_loop"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** `vegetation.classify` tells sea from land with `geo.is_land(elev, ice)`, which needs a sphere grid
to flood the sea. A zoom calls it on its land pixels; it works only because the landscape pass keeps land at >= 0.5 m
(`landscape_loop`: "creep mustn't pull the coast below the sea"), so `wet` is empty and is_land returns early. Any land
pixel at or below 0 m without ice (lane 127 hit it while matching sections, before clamping the blend) raises
`is_land: 60995 cells is no sphere grid; pass grid=`. Inland pits below sea level (PW-1229 allows them on worlds) or a
future change could hit it in an ordinary zoom.

Fix: in a zoom, pass the land mask the zoom already has (classify is called on land pixels only) instead of is_land, or
give classify a `land=` argument and use is_land only on world cells.
- [ ] a zoom whose land includes a pixel at -5 m builds without error

## Updates
- 2026-11-02: Created from inbox draft draft-zoom-vegetation-is-land-on-pixels.md (found by lane127).
