---
id: PW-1338
title: Land zoom sections need an orientation in zoom(), save() and zoom.json before any tiling sweep
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: zoom
effort: s
impact: high
found_by: lane122
blocked_by: []
relates: [PW-1319]
refs: ["planet/zoom/tiling.py::sections", "planet/zoom/tiling.py::section", "planet/zoom/regional.py::frame_of", "planet/zoom/regional.py::up_of", "planet/zoom/terrain.py::en_to_grid", "planet/zoom/glacial.py", viewer/zoom3d_place.js, viewer/zoom.html, viewer/globe/tabs.js, docs/review/land-zoom/seams-round1.md, "planet/zoom/regional.py::Frame", "planet/zoom/regional.py::zoom", "planet/zoom/regional.py::build", "planet/zoom/regional.py::save", "planet/zoom/regional.py::zoom_id", docs/review/land-zoom/tiling.md, docs/review/land-zoom/seams.py, tests/test_zoom_tiling.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** The tiling (`tiling.py`) says each section is a square turned so its up is the cube face's up. `Frame`
now takes `up=`, but `zoom()` / `build()` / `save()` / `zoom_id()` do not: there is no way yet to ask for a rotated square, and
`zoom.json` records only the centre, so `seams.py` and the viewer would rebuild a north-up frame. Add an optional `up` (unit
vector or bearing in degrees) to the build arguments, the zoom id (so a rotated and an unrotated zoom of one centre differ),
`zoom.json` (`projection.up`), the viewer's 3D placement and `seams.py::Z` (frame from the recorded orientation). Pole centres
(`pz.1.1`, `mz.1.1`) must work.
- [ ] `planet zoom --section px.1.1` (or `--up`) builds the tiling's section for a world; ids differ by orientation
- [ ] corners in `zoom.json` follow the rotation; `seams.py` accepts rotated zooms
- [ ] two neighbouring sections' overlap band checked against `tiling.sections()[..]['overlap_km']`

## Updates
- 2026-11-02: Created from inbox draft draft-land-zoom-section-orientation.md (found by lane122).
