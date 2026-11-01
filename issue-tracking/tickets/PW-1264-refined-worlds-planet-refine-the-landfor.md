---
id: PW-1264
title: "Refined worlds (planet refine): the landform classes' own terrain is not drawn, only the zoom's noise and means"
type: task
status: needs-decision
parent: PW-1198
milestone: v2
subsystem: zoom
effort: l
impact: med
found_by: lane104-refine-l8
blocked_by: []
relates: [PW-490, PW-1008]
refs: [planet/refine.py, planet/zoom/landforms.py, planet/zoom/stage_terrain.py, docs/review/refine-l8/design.md, docs/review/refine-l8/shots/]
created: 2026-11-01
updated: 2026-11-01
---

## Description
**In plain words.** `planet refine` makes a finer whole world (L8 or L9) from a finished L7 one. Its terrain uses the
regional zoom's coastline, relief noise and "keep each big cell's average height" steps, but not the zoom's landform
shapes (fold ridges, rift blocks, escarpments, mesas, karst, dunes). At 28 km cells (L8) most of those shapes are
smaller than a cell, so little is lost there. At 14 km (L9) and finer the loss starts to show.

Why it was not done: `zoom/landforms.py` is built on the zoom's pixel raster (D8 receivers, bench maps along pixel
rows, a planar projection per region). Running its hooks on the icosphere needs a refactor: the hooks (target,
shape, strata) would take 3D cell positions and a neighbour graph instead of pixel arrays.

Options:
- A: leave it out at L8, where the classes' forms are smaller than a cell. Do it with the GPU detail mesh (PW-1008) instead.
- B: refactor the hooks that depend only on position (target, shape: folds, rift blocks, domes) to take points,
  and call them from refine at L9. Leave strata and benches, which are tied to the raster, to the zooms.
- C: full port (all hooks on a graph). Large.

Lean: A for L8; B when L9 becomes a product (after PW-1209 makes L9 openable).

## Updates
- 2026-11-01: Created from inbox draft draft-refine-landform-synthesis-on-the-sphere.md (found by lane104-refine-l8).
