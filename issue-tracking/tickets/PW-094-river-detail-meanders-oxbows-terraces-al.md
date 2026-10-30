---
id: PW-094
title: "River detail: meanders, oxbows, terraces, alluvial fans, floodplains, wetlands"
type: story
status: todo
parent: PW-090
milestone: null
subsystem: zoom
effort: l
impact: med
found_by: daniel
blocked_by: []
relates: [PW-061]
refs: [planet/zoom/regional.py, planet/zoom/kernels.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
In the zoom: meandering channels and oxbow lakes on low gradients, river terraces (from base-level and
uplift history), alluvial fans at mountain fronts, floodplains and wetlands.

## Updates
- 2026-10-14: zoomland3 (PW-012): coastal plains want proper meanders too; for now CoastalPlain only adds a few metres of micro-relief to the target so its rivers wander.
- 2026-10-14: Created from the owner's world-finishing epic (2026-10-14).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
