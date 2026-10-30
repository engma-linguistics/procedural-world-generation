---
id: PW-1043
title: River discharge and island/basin sizes treat every grid cell as the same size; real cells span 0.67-1.21 of the mean
type: task
status: todo
parent: null
milestone: null
subsystem: hydrology
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-444, PW-820, PW-243]
refs: [planet/hydrology.py, planet/vegetation.py, planet/coast.py, planet/climate.py, planet/ocean.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The globe's cells are not all the same size (the smallest are two-thirds of average, the largest a fifth bigger), but river flow and the size tests for islands and seas assume they are. So rivers near the grid's twelve corner points carry up to a third too little or a fifth too much water, and that feeds floodplains, deltas, navigable rivers and the culinary fish/salt thresholds.

Verified on main b36c9581: `ocean.cell_area_km2` on L6 gives min/mean 0.675 and max/mean 1.206 (the `_geom` comment says "~9%"). `hydrology.py:110 discharge()` uses `4*pi*6.371e6**2/grid.n`; the same uniform area is written out 23 times in 14+ files (vegetation.py:812, coast.py:534/541/688, climate.py:863 island walls, ...).

Fix: a cached `Grid.cell_area_km2` (moved from ocean.py), accumulate `runoff × area` instead of cell counts, one `hydrology.discharge` that every caller uses, and a test that pins discharge against true areas. Goldens and Earth checks move a little: re-run scorecard.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-true-cell-areas-in-river-flow.md (found by code-audit-2026-10).
