---
id: PW-174
title: Plate cells no world cell samples miss each step's physics
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: tectchurn
blocked_by: []
relates: [PW-108, PW-134]
refs: [planet/tectonics/simulation.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Nearest-neighbour sampling of a rotated grid skips ~7% of each plate's owned
cells per step (L6 seed 21: ~3000 of 41k world cells sample a plate cell
another world cell also samples). `_scatter` writes the step's results only to
sampled cells, so skipped ones miss that step's erosion, deposition, stacking,
arc growth, thinning (ageing is already done on all cells, see `_age`).
Tried on branch tectchurn (not kept): an inverse-map kernel (each skipped
plate cell -> the world cell it lies in, same plate) and applying that world
cell's change (deltas of thickness/cover/mix; type, rock, strata, history
copied where they changed). Alone it cut type churn ~20% (L6 s21 500-600 Myr:
crust flips 3.37 -> 2.71%); with crust.coherence in place no measurable gain
(L6 s21/s22 100-600 Myr, within noise), so it was dropped for simplicity.
Worth revisiting for PW-134's record speckle (strata/cover differ cell to
cell partly because of this). Cost: one numba pass like cleanup_ghosts.

## Updates
- 2026-10-14: Created from inbox draft draft-unsampled-plate-cells.md (found by tectchurn).
