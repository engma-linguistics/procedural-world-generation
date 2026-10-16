---
title: Zoom stores no lake kind: 3D and 2D guess fresh / salt / pan from the climate
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: pw342
blocked_by: []
relates: [PW-342, PW-072]
refs: [viewer/zoom3d.js, planet/satellite.py, planet/zoom.py, "zoom 193d10"]
---

## Description
The zoom has no `lake_kind` layer and `stats.largest_lakes` carries no kind, so the 3D view
(`Tile.lakeKinds`) and `planet/satellite.py` each guess: the 3D view calls a lake salt when it is
closed (no river leaving it; the five biggest lakes' outlets from the stats) under 500 mm/yr, a pan
when under 1 m deep; the satellite view calls it salt under P/PET 0.3 whether closed or not. They
can disagree (193d10: the 3D view makes the open 26656 km2 lake fresh and the closed 19840 km2 one
salt). Store a per-pixel `lake_kind` (1 fresh, 2 salt, 3 pan, from the coarse world's `lake_kind`
and the zoom's own lake balance) in the zoom, and have the 3D view and satellite read it. No zoom
in the store has pans, so the white pan path is untested on real data.
- [ ] zoom writes `lake_kind`; 3D view and satellite use it instead of guessing
