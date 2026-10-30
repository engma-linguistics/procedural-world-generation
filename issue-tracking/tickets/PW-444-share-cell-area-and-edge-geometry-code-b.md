---
id: PW-444
title: Share cell-area and edge-geometry code between grid, climate, ocean and the time zoom
type: task
status: todo
parent: PW-649
milestone: later
subsystem: infra
effort: s
impact: low
found_by: pw442
blocked_by: []
relates: [PW-442]
refs: [planet/grid.py, planet/ocean.py, planet/climate.py, planet/timezoom/geometry.py, planet/landform.py]
created: 2026-10-20
updated: 2026-10-23
---

## Description
PW-442 added `Grid.nbr_src` (the cell each CSR edge leaves) and `Grid.edge_dir` (unit tangent per CSR edge) in `grid.py`, and used them in `ocean._csr_dir`, the time zoom's `geometry()`, and a few `np.repeat(np.arange(n), np.diff(nbr_off))` sites in `ocean.py`/`landform.py` (bit-identical). Left, because the versions differ numerically or sit in files another agent is editing:

- [ ] **Cell area**: `timezoom/geometry.py` sums a triangle fan from the centre over the corners and renormalises to 4 pi R^2; `ocean.cell_area_km2` sums solid angles (atan2 form) and does not renormalise. Same quantity, different last bits (and the fan version is rescaled). Pick one as `Grid.area` and check what each consumer's goldens say.
- [ ] **Edge geometry in `climate.py`** (`_geom` l.142 directed-edge distance and tangent; `_faces` l.201/209 corner side length and centre-edge length): the same quantities as `timezoom/geometry.py` dist/elen. Not touched (PW-438 edits climate). `Grid.edge_dir` is the same expression as `_geom`'s tangent.
- [ ] **Neighbour means**: `timezoom/ice.py shelf_cover` (weighted by sea, bincount over CSR neighbours), `ocean._coarse/_down` (sea share over coarse cells) and `landform.regional_dip` (neighbour mean via bincount) are near duplicates; a `nbr_mean(grid, values, weights)` in `grid.py` could serve all three. Different divisors, so not bit-identical by default.
- [ ] More `np.repeat(np.arange(n), np.diff(nbr_off))` sites to switch to `grid.nbr_src`: hydrology.py:352, store.py:375, climate.py:155/617, coast.py:479/539, zoom.py:1147/1152, soils.py:200.

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-20: Created from inbox draft draft-pw442-grid-geometry-dupes.md (found by pw442).
- 2026-10-30: Refactor 1 (lane 59) shared geo.arc/arc_km (about 50 inline great-circle distances), geo.cell_area_km2 (18 inline cell areas), geo.smoothstep/ramp, Grid.components (climate._label deleted), Grid.nbr_mean/nbr_mean_in/nbr_max_in, kernels.accumulate (zoom copy deleted), raster.box_mean; goldens unchanged. Left, with reasons: draft-refactor1-float-order-copies-left.md.
