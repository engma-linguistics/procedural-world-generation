---
id: PW-1704
title: "LOD tiles: a level-1 tile job checks RAM for a 3.2 GB tile, and an API section build can shadow a matched one"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: s
impact: med
found_by: lane295
blocked_by: []
relates: [PW-1699, PW-1690]
refs: ["planet/api.py::tile_job", "planet/api.py::TILE_PEAK_GB", "planet/api.py::_section_zoom_job", "planet/zoom/lod_build.py::_section_dir", planet/tiles.py]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Since lane 295 the tile service builds a square's first detail level through the same job as
the finer tiles, so that it fits its built neighbours. Two loose ends in planet/api.py (lane 295 was asked not to
edit it): the job's own memory check still assumes a finer tile (3.2 GB) where the first level needs ~8.4 GB, and a
section built the old way (POST /api/zoom with a section, unmatched) after a matched one becomes the one the globe
uses (the newest wins). If never done: a level-1 build can start with too little memory free when the tile service's
own guard is bypassed (a direct job), and a hand-built section can bring back the step at a square's border.

Measured (lane 295, dba204, 4 threads, two builds at once): level 1 unmatched 227-229 s, peak 8.53-8.54 GB; matched
182-188 s, peak 8.32-8.37 GB (the load fell between the pairs; CPU 570-591 s matched against 664-684 s alone).
- [ ] `api.tile_job` checks 8.3 GB (tiles.PEAK_GB[1]) for a level-1 key; a 4 km section from POST /api/zoom of a cell
      with built neighbours is built matched (`lod_build.build_level1`), or the globe prefers the matched one

## Updates
- 2026-11-11: Created from inbox draft draft-lod-level1-job-ram-and-api-sections.md (found by lane295).
