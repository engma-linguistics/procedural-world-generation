---
id: PW-1733
title: "LOD tiles: settled at 300 m over a four-cell corner, the ground at the screen's centre is the 1 km level"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: viewer
effort: s
impact: med
found_by: lane306
blocked_by: []
relates: [PW-1708, PW-1710]
refs: [viewer/globe/lodtiles.js, viewer/lodmath.js, docs/review/zoom/lod-judge-306.md, docs/review/zoom/lod-judge-306/corner_19_ground_300m.png, docs/review/zoom/lod-judge-306/corner_report.json, "world dba204, -16.3, 72.95 (py.0.0 / py.0.1 / py.1.0 / py.1.1)"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Lane 306's corner dive (dba204, -16.3, 72.95, where four big squares meet) came down to 300 m and
waited until nothing was queued or building; the view still looks 1 km blurry and the hover at the screen's centre read
"Detail 1 km/px ... tile py.0.0/2/7/1" (`corner_19_ground_300m.png`; the report: 34 level-4 tiles drawn elsewhere in the
view). On the border dive the same wait gave 25 m ground. Not traced: either the corner's level-3/4 tiles of that cell
are never wanted (the walk in `updateLod`, `lodmath.exists` near a corner), or they are built and not drawn, or the
hover's `tileUnder` (nearest cell centre, not the cell holding the point) picks the wrong cell.

**Done when.** The cause is found; settled at 300 m over that corner, the ground at the centre is level 4 and the hover
says so; a test pins it (`tests/test_viewer_lod.py`).

## Updates
- 2026-11-11: Created from inbox draft draft-lod-corner-ground-stays-at-1km.md (found by lane306).
