---
id: PW-1301
title: "Land zoom seams: neighbouring sections agree at their edges (heights, coasts, landforms, biomes)"
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: zoom
effort: l
impact: high
found_by: owner
blocked_by: [PW-1319]
relates: []
refs: [planet/zoom/stage_finish.py, planet/zoom/coastal.py, planet/zoom/fine_forms.py, planet/zoom/match.py, "planet/zoom/match.py::prepare", "planet/zoom/stage_landscape.py::landscape_loop", "planet/zoom/stage_terrain.py::mean_correction", "planet/zoom/stage_terrain.py::coastline", "planet/zoom/regional.py::zoom", planet/zoom/tiling.py, tests/test_zoom_match.py, docs/review/land-zoom/seams-round1.md, docs/review/land-zoom/practice.md, docs/review/land-zoom/seams.py, docs/review/land-zoom/table.py, "world dba204"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** Make adjacent sections agree where they meet: shared overlap bands with blending, noise and landform seeds keyed by place rather than by section, and coastlines from one source. Judged on the practice sections.

## Updates
- 2026-11-02: Created.
