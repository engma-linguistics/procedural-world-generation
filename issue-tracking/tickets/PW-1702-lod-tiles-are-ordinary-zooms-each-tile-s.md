---
id: PW-1702
title: "LOD tiles are ordinary zooms: each tile save rereads every zoom, and the tiles flood the viewer's zoom lists"
type: task
status: done
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane294
blocked_by: []
relates: [PW-1690, PW-1689]
refs: [planet/tiles.py, "planet/zoom/lod_build.py::_section_dir", "planet/zoom/lod_build.py::save", "planet/zoom/fine.py::save", "planet/zoom/regional.py::update_index", "planet/store.py::update_index", "planet/store.py::items", planet/family.py, docs/review/zoom/lod-plan-v2.md, "world dba204"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Every detail tile the globe builds is saved as an ordinary zoom. Each save rewrites the zoom list by
reading every zoom on disk, each tile build looks for its 4,000 km section by reading every zoom too, and every tile
shows up in the viewer's lists of zooms (the planets page, a world's zooms). After Daniel explores a few dozen places
(~30 tiles a dive at levels 2-4, plan 1.3) there are hundreds to thousands of tiles. If this is never done, tile builds
slow down as the cache grows (each one reading every zoom.json, ~73 layer specs each), and the zoom lists Daniel uses
fill with "tile py.1.1/3/18/19" entries.

Where:
- `fine.save` ends with `regional.update_index()` -> `store.update_index("zoom")`, which globs and parses
  `zooms/*/zoom.json` (store.items) on every save.
- `lod_build._section_dir` (via `find` and `load_sources`) globs and parses every `zooms/*/zoom.json` on every tile
  build, to find the level-1 section. The tile service (planet/tiles.py) avoids it on its side (it finds a section by
  `api.section_zoom_id` and keeps its own index under `<data root>/.tiles/`), but the build in the worker still does it.
- `store._zoom_item` lists tiles like any zoom, so `/api/planets` (family.py) and a world's zoom list carry them.

What I'd try (planet/zoom is lane 293's file this round, so not done here): save tiles without `update_index` (the
tile service has its own index) and mark them in `_zoom_item` so the listings skip them; find the section in
`lod_build` by its deterministic id (`api.section_zoom_id` logic) before falling back to the scan.
- [ ] building the 100th tile of a world takes no longer than the first (same tile, timed) and no tile appears in
      `/api/planets` or the world's zoom list

## Updates
- 2026-11-11: Status todo -> done. Merged lane 298: tiles in .tiles/<world>/zooms, out of zoom lists; section find still a scan (PW-1707).
- 2026-11-11: Created from inbox draft draft-lod-tiles-flood-the-zoom-index.md (found by lane294).
