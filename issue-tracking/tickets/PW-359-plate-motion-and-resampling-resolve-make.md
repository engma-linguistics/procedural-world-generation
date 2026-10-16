---
id: PW-359
title: Plate motion and resampling (resolve) make most of the run's closed-hollow volume each step
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: basins-lakes
blocked_by: []
relates: [PW-054, PW-300, PW-243]
refs: [planet/tectonics/plate_kernels.py, planet/tectonics/simulation.py, docs/review/audit/basins-lakes.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
A per-substage budget of closed-hollow volume (hollows the lakes keep: `hydrology._bed` with MIN_DEPTH and
MIN_SLOPE, then priority-flood spill - bed over land), L6, 300 Myr, mean per 2-Myr step after 50 Myr:

| substage | seed 1, km3 (gross + / -) | seed 77 |
|---|---|---|
| resolve (move, resample, collide; dyn recomputed) | +66,000 (+73,000 / -6,600) | +34,000 (+51,000 / -16,000) |
| _age (plume swells decay) | +9,700 | +800 |
| arcs and plumes | +5,800 | +5,800 |
| crust flow and orogeny | -13,000 | -19,000 |
| erosion and deposition | -78,000 (+4,500 / -82,000) | -47,000 (+16,000 / -63,000) |
| write-back (dyn recomputed) | -9,400 | -10,000 |
| events, world view, climate's sea shift | +25,000 | +44,000 |

So the run's closed hollows are mostly made by `resolve` each step and filled by erosion: rigid plates
moving over the grid and resampled to it (nearest cell; ~10-20% of cells momentarily unsampled, per
`_age`'s docstring) shift and duplicate cells, which on flat continental interiors dams a low cell or an
outlet valley. In plate interiors with no boundary that is numerical, not tectonic. It matters for PW-054
(the closed basins it makes are noise, refilled within a step or two, rather than basins that sink) and
PW-300 (giant hollows on flat plains appear and vanish in one frame), and possibly PW-243 (the noise's
relief depends on the cell size). Worth measuring the per-step elevation change of plate-interior cells far
from boundaries under resolve alone (should be ~0 for a rigid plate), and trying a conservative resample
(area-weighted from the plate's frame) for elevation-carrying columns. Script:
docs/review/audit/basins-lakes/hollow_budget.py (`python hollow_budget.py <repo> 6 <seed> 300`).

## Updates
- 2026-10-16: Created from inbox draft draft-resolve-makes-hollows.md (found by basins-lakes).
