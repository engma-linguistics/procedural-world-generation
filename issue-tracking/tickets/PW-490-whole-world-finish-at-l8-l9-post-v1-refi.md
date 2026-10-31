---
id: PW-490
title: "Whole-world finish at L8/L9 (post-v1): refine the finished moment onto a finer global grid, with a level-of-detail globe viewer"
type: epic
status: todo
parent: null
milestone: v3
subsystem: zoom
effort: xl
impact: med
found_by: daniel
blocked_by: []
relates: [PW-316, PW-290, PW-100, PW-101]
refs: []
created: 2026-10-20
updated: 2026-10-31
---

## Description
Owner 2026-10-20: saved for after v1, since the viewer can handle it with level of detail.
Idea: keep the L7 tectonic history and refine only the finished moment onto L8 (655k cells, ~28 km) or L9 (2.6M, ~14 km). The icosphere nests, so every L7 vertex is also an L8/L9 vertex.
- Terrain: the regional zooms' landform synthesis, keeping each L7 parent's mean.
- Rivers, lakes and coasts recomputed on the new terrain.
- Climate downscaled from L7 first (lapse rate, rain shadow, as in PW-101). Rerunning it at L9 risks the resolution dependence of PW-290.
- Soils, vegetation and biomes rerun per cell.
Cost: roughly 4x (L8) or 16x (L9) the finishing time; measure first. Memory ~1 GB per L9 frame.
Viewer: chunked level of detail, like Cesium or Google Earth. The coarse L7 globe is always drawn, and finer patches load only where the camera is close and only for visible tiles, building on PW-316's data textures.
Gain: a sharper globe, and honest detail in large exports (today a 4096 px export is ~10 km/px over 56 km cells).

## Updates
- 2026-10-31: 2026-10-31: first cut (refine a finished L7 world to L8) moves into the v2 epic PW-1198 (space-to-ground globe); the rest (L9, GPU synthesis) stays v3.
- 2026-10-23: Milestone -> v3 (board triage 2026-10-24): deliberately far off, a system of its own after v2; see docs/review/board/triage-2026-10-24.md.
- 2026-10-20: Created.
