---
id: PW-1110
title: A few copied helpers give slightly different last digits, so they were not merged (cell area, neighbour mean)
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: s
impact: low
found_by: refactor-lane-59
blocked_by: []
relates: [PW-444, PW-1043, PW-1025]
refs: [planet/geo.py, planet/coast.py, planet/coastform.py, planet/lineages/brief.py, planet/highlights.py, planet/ocean.py, planet/timezoom/geometry.py, planet/timezoom/deposit.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Refactor 1 shares helpers only where the answer is bit-for-bit the same (goldens unchanged). Some copies compute the same thing in a different order, so the last digits differ; merging them would nudge outputs and needs a golden update, which this refactor may not do.

- Cell area: `geo.cell_area_km2(n)` replaced every `4*pi*R^2/n` that stood alone. Five sites multiply by it before dividing (`x * 4*pi*R**2 / n`), so their rounding differs: `coast.py` (two, the ocean-basin sizes), `coastform.py` (hazard_km2), `lineages/brief.py` (area_mkm2, land_mkm2). `ocean.cell_area_km2` (cached in `climate._geom`) and `timezoom/geometry.py` are exact variants and PW-1043 owns that difference.
- Neighbour mean: `highlights._nbr_mean` sums with `np.add.at` over the edge list, which adds in a different order from the reduceat in `Grid.nbr_mean_in`. Also `generators.smooth` (bincount over edges) and `lineages/gridops.nbr_reduce`.
- Box means with other edge rules: `zoom/resources._box` (clamped), `zoom/shoreforms._box` (zero-padded and renormalised) and `zoom/peoples._blur` (edge-padded) cannot share `raster.box_mean` without a choice per site.

- [ ] move these onto `geo.cell_area_km2`, `Grid.nbr_mean_in` and `raster.box_mean` with a golden update, one per commit, reading the golden diff each time

## Updates
- 2026-10-30: Created from inbox draft draft-refactor1-float-order-copies-left.md (found by refactor-lane-59).
