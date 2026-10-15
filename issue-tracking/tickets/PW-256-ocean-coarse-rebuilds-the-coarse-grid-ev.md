---
id: PW-256
title: ocean._coarse rebuilds the coarse grid every climate update and evicts climate._geom's cache (~4-8% of runs and time zooms)
type: task
status: todo
parent: PW-247
subsystem: ocean
effort: s
impact: med
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249]
refs: [planet/ocean.py, planet/climate.py, planet/grid.py, docs/review/gpu/profile.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`ocean._coarse(grid, sea, level)` is cached on `(id(grid), n, level, hash(sea))`; the sea mask
changes every climate update, so every update calls `build_grid(level)` again (126 builds in an L6
500 Myr run) and gets a new Grid object. Its `id` then lands in `climate._GEOM` (cleared whenever it
holds more than 4 grids), so the main grid's `_geom` (least-squares gradient weights, blur weights,
einsum + inverse of n 3x3 matrices) and `ocean.cell_area_km2` are recomputed again and again.
Measured exclusive time at 16 threads: `climate._geom` 3.2% + `ocean.cell_area_km2` 1.6% +
`grid.build_grid` (under ocean) ~1.2% of an L6 run; 7-8% of a time zoom (L6 and L7).

Fix: cache `build_grid(level)` per level (the coarse grid doesn't depend on the sea), keep the
per-sea-mask part of `_coarse` separately, and key `_GEOM` so that a handful of coarse grids can't
evict the main grid (or cache per level rather than per id). Outputs should be bit-identical.
- [ ] build_grid per level cached; `_geom` / `cell_area_km2` computed once per grid per process
- [ ] goldens unchanged; before/after timing of an L6 run and a time zoom

## Updates
- 2026-10-15: Created from inbox draft draft-ocean-coarse-grid-cache-thrash.md (found by gpu-explore (PW-249)).
