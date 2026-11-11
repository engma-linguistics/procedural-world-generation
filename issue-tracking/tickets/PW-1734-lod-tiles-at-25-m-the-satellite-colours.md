---
id: PW-1734
title: "LOD tiles: at 25 m the satellite colours (snow, scrub) change on a cell edge though the ground matches"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane306
blocked_by: []
relates: [PW-1705, PW-1708, PW-1713]
refs: ["planet/zoom/lod_build.py::line_surface", planet/zoom/fine.py, planet/zoom/satellite.py, docs/review/zoom/lod-judge-306.md, docs/review/zoom/lod-judge-306/after_15_25m_straight_down.png, "world dba204", "tiles py.0.1/4/283/110 and py.1.1/4/9-10/110"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Where two big squares meet, the ground of their tiles now agrees (level 4: median 0.13 m, the
floor), but the colours do not: straight down at 25 m over dba204's py.0.1 / py.1.1 line, alpine-scrub and snow patches
of one side end exactly on the line and the other side is plain snow (`after_15_25m_straight_down.png`). Sibling
tiles inside one cell show no such line (colour steps across their edges as inside, lane 306).

The fade to the line (`line_surface`) carries the owner's ground and river courses, not its categorical layers: each
cell's tile classifies snow, vegetation and land cover from its own parent and climate, so the classes jump at the line.

**Done when.** Within the line's fade, a tile's categorical layers that colour the satellite view (vegetation, ice /
snow, land cover) are the owner's on both sides (as the courses are, PW-1713); the colour step across the line is within
10% of the steps beside it (`tools/lod_judge_seams.py`-style, on a dba204 border dive); a rebuild bit-identical.

## Updates
- 2026-11-11: Created from inbox draft draft-lod-satellite-colours-differ-at-cell-edges.md (found by lane306).
