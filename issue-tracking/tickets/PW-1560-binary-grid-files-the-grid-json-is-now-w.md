---
id: PW-1560
title: "Binary grid files: the grid JSON is now what makes an L8 world slow to open, and most of an L9 world's browser memory"
type: task
status: todo
parent: null
milestone: v5
subsystem: viewer
effort: m
impact: med
found_by: lane 229
blocked_by: []
relates: [PW-1209, PW-1198]
refs: [docs/review/viewer/binary-layers.md, "planet/store.py::write_grid", "viewer/globe/load.js::gridOf", "viewer/globe/geometry.js::prepareGrid"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: since PW-1209 a world's layers come to the viewer as binary files, and they now arrive while the
grid is still loading. So the grid file (`grids/L<level>.json`: cell centres, corners, corner lists, neighbour
lists, all as JSON text) is what the viewer waits for. At L8 it is about 1.0 s of a 2.2 s opening (87 MB of JSON);
at L9 it is 4.4-9 s of an 8-16 s opening (370 MB of JSON, 70% of Chrome's longest string), and its lists of lists
are most of the 2.7 GB JS heap an L9 world takes after loading (the layers are ~0.8 GB more, outside the heap).

What breaks if never done: L8 does not reach PW-1209's 1.5 s target, and L9 opens in 10-20 s and uses ~4 GB of the
browser's memory. It works, but slowly, and one level more (or a few more grid fields) would not fit.

Fix: write the grid as typed arrays like the world layers (lat/lon as float32 or scaled int32; cells and
neighbours as offset + flat index arrays, CSR), with a small JSON header. The viewer's users of `G.nbr[i]`,
`G.cells[i]`, `G.lat`, `G.lon` (geometry.js prepareGrid, pick.js, overlays.js, landsea.js, and others) move to
the flat arrays; runs and worlds share the grid file, so both change at once. Measure with
`tools/viewer_perf_globe.py` (load stages, heap, renderer RSS) at L8 and on the synthetic L9 world
(`tools/synth_l9_world.py`).

- [ ] an L8 world opens in < 1.5 s; an L9 world's JS heap after load under 1.5 GB

## Updates
- 2026-11-08: Created from inbox draft draft-binary-grid-file.md (found by lane 229).
