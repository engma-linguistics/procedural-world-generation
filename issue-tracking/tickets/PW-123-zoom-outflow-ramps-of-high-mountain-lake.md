---
id: PW-123
title: "Zoom: outflow ramps of high mountain lakes stand up to ~440 m above the land"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomsmalls
blocked_by: []
relates: [PW-066]
refs: [planet/zoom.py, "world:f724bd(72.22,1.87)", "world:f724bd(67.99,7.43)"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Since PW-066 the rapids floor below an open lake's outlet only covers the outflow river and its banks
(not 150 km around), capped at the coarse ground. But it still descends at RAPIDS_GRAD = 2 m/km, which
is far too gentle for a lake at 1,400-2,000 m in mountains: in zooms at world:f724bd(72.22,1.87) and
(67.99,7.43) the corridor stands up to ~440 m above the target surface (the carved valley), a raised
causeway down the valley. Options: let the rapids steepen with the local coarse relief (e.g. the
coarse drop from the lake cell to its exit cell over their distance), or end the ramp in a designed
fall/cascade where the floor would sit far above the target.

## Updates
- 2026-10-14: Created from inbox draft draft-zoom-mountain-lake-outlet-ramps.md (found by zoomsmalls).
