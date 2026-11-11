---
title: "LOD globe near the ground: the globe's river ribbons run cell centre to cell centre, away from the tiles' own rivers"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: viewer
effort: m
impact: med
found_by: lane299
blocked_by: []
relates: [PW-1696, PW-1688]
refs: [viewer/globe/drape.js, viewer/globe/overlays.js, "viewer/globe/geometry.js::cellPositions", docs/review/zoom/lod-dive-299/, docs/review/zoom/lod-plan-v2.md, tools/viewer_lod_dive.py, "world dba204", "tile py.1.1/2/3/4"]
---

## Description
**In plain words.** Low over the ground the river lines now lie on the ground (PW-1696), but they are the globe's
rivers: straight lines from one 55-km cell's centre to the next. The detail tiles under them show the real river
somewhere else (its own valley, 1 km pixels), so at 20 km and 1 km up a blue line crosses fields and hills while the
river in the picture runs beside it. If never done, the low view shows two rivers that disagree, and the line one is
the one people will trust.

Seen: `docs/review/zoom/lod-dive-299/05_low_20km.png` (world dba204, -4.08, 88.52; the dark ribbon runs through the
centre, the tile's own river is the pale band to the right), `06_ground_1km.png`.

What to try (plan section 4, "Layers follow you down"): below the drape height (`drape.js::DRAPE_KM`, 300 km), where
a level-2 or finer tile is drawn, hide the globe's river ribbons there and draw the tile's own rivers (the tile's
`layer/rivers` or flow layer, as lines or as a tinted texture in the tile shader); keep the globe ribbons where only
cells are drawn. The draped copies already know which tile is under each point (`lodtiles.js::groundRadius`).
- [ ] at 20 km and 1 km over dba204 the river drawn is the tile's river; no globe ribbon over a drawn level-2 tile
- [ ] where tiles are still building, the globe ribbon shows as now
