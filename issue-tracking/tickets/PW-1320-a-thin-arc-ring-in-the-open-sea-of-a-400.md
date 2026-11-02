---
id: PW-1320
title: A thin arc ring in the open sea of a 4000 km zoom, absent in its neighbour
type: task
status: todo
parent: PW-1299
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: lane116
blocked_by: []
relates: [PW-1301]
refs: ["zoom 2a4463", "zoom fde691", docs/review/land-zoom/seam-coast.png, docs/review/land-zoom/practice.md, "world dba204", "planet/zoom/regional.py::zoom"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In `seam-coast.png` (zoom 2a4463 at (40,130), 4000 km @ 2 km, and its neighbour fde691), strip 1 shows a thin circular arc in A's deep sea (a few pixels wide, ~1000 km of arc) that B lacks at the same place; strip 3 shows it as a bright red line (a height step). It looks like a radius-based clamp or blending boundary in the sea floor. Find which stage draws it (open the zoom's heightmap near the arc; check the coast, shoreface and halo code) and whether other large zooms have it.

## Updates
- 2026-11-02: Created from inbox draft draft-zoom-sea-arc-artifact.md (found by lane116).
