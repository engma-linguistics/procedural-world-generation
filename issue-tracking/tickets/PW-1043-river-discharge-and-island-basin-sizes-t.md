---
id: PW-1043
title: River discharge and island/basin sizes treat every grid cell as the same size; real cells span 0.67-1.21 of the mean
type: task
status: done
parent: null
milestone: null
subsystem: hydrology
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-444, PW-820, PW-243]
refs: [planet/grid.py::Grid.cell_area_km2, tests/test_cell_area.py, tools/fork_screen.py, planet/hydrology.py, planet/vegetation.py, planet/coast.py, planet/climate.py, planet/ocean.py, docs/review/code-audit-2026-10/index.html]
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
- 2026-11-10: Done (lane 263). `Grid.cell_area_km2` / `area_weight` (moved from ocean.py, cached); hydrology weights runoff, lake loss and the dry-hollow rain/PET by cell area, so flow keeps its units (mean cell x m/yr) and the one `hydrology.discharge` is true m3/s; every discharge caller uses it. is_land's small-sea rule, coast's basin/sea sizes and river_sediment, climate's island sizes, coastform's island mask, coastal plume/habitats, export/highlights/health areas, ocean river_input, both ice sea-level formulas and the ice diag add true areas. `tests/test_cell_area.py` pins discharge (L5 pentagon dome: old cells-as-mean answer 7% high). Goldens regenerated; full suite passes. Fork screen (tools/fork_screen.py, L6 seeds 1/2/77/3199, 4 draws vs main a866c5ad's 7 + fp-null): pooled inland 10.07 -> 10.09%, lakes 0.734 -> 0.733%, giant-lake frames 6.6 -> 8.4% (s.e. ~2.1), sea discharge 2862 -> 2864 k m3/s: inside main's spread. earth_check vs main a866c5ad: unchanged to the last digit but a few (Amazon 371,819 -> 371,812 m3/s; it already scaled by true areas). Scorecard line b7773291 vs c0f88f98: Earth climate identical; seeds 1/2 on new trajectories, all plausible. Left over: the tectonics/volcanism/lineage areas still on the mean cell, and test_coast's tide-delta mouth count flipping 4 -> 3 at +4% river (drafts).
