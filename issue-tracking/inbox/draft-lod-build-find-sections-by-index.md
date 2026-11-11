---
title: "lod_build finds a cell's level-1 section by scanning the whole tile store (it should look it up)"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: xs
impact: low
found_by: lane298
blocked_by: []
relates: [PW-1702, PW-1704, PW-1690]
refs: ["planet/zoom/lod_build.py::_section_dir", "planet/zoom/lod_build.py::find", "planet/zoom/lod_build.py::built_neighbours", "planet/zoom/lod_build.py::build_level1", "planet/store.py::tile_store", "planet/tiles.py", "docs/review/zoom/lod-plan-v2.md (State, lane 298)", "/data/personal/scratch/lane298/measure.py (deleted at the end of lane 298; 50 ordinary zooms, 20 tiles)"]
---

## Description
**In plain words.** Since lane 298 the globe's tiles live in their own store (`<data root>/.tiles/<world>/zooms/`), so
saving a tile no longer rereads any zoom and the viewer's zoom lists hold none. What is left is one scan:
`lod_build._section_dir` (used by `find`, `built_neighbours`, `build_level1`, i.e. by every tile build that reads
level 1 and by every level-1 build, once per neighbour) globs and parses every `zoom.json` in the tile store to find
the cell's section. Measured on 50 ordinary zooms + 20 tiles: 0.1 ms with 1 tile, 1.1 ms with 20, about 0.05 ms a
tile, so a world with a few thousand tiles pays ~100-200 ms a lookup, in each tile job. If never done, that cost grows
with the cache (small next to a 12-200 s build, but it is the one scan left, and the ticket PW-1702 asked for a
lookup).

Lane 298 could not edit `planet/zoom/`. What I'd do: keep the cell -> section-dir map in the tile store as a small file
(`<tile store>/sections.json`, `{"<cell>/<seed>": "<zoom id>"}`), written by `build_level1` after it saves the section
(inside its existing per-world lock), read by `_section_dir` before the scan (fall back to the scan only when the file
lacks the cell, then add it). Level 2-4 tiles are already found by their deterministic id (`find`).
- [ ] `_section_dir` of a built cell reads no `zoom.json` of other tiles (count file reads in a test)
- [ ] `tests/test_zoom_lod_level1.py` and `tests/test_tiles.py` still pass
