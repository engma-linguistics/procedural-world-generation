---
id: PW-359
title: Plate motion and resampling (resolve) make most of the run's closed-hollow volume each step
type: task
status: todo
parent: null
milestone: null
subsystem: tectonics
effort: m
impact: med
found_by: basins-lakes
blocked_by: [PW-358]
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
- 2026-10-16: Status blocked -> todo. pw300: PW-358 is done and PW-300 landed outlet memory (valley column carried with the rock), which removes the basins that closed only because they lost their outlet; the closed-hollow volume resolve makes each step is untouched by it. What's left for this ticket: giant lakes in hollows that never spilled, appearing in a step or two on flat plate interiors (after PW-300 they're most of the ~4% of L6 frames with a lake over 1 Mkm2; e.g. seed 77 @ 68 Myr 2.4 Mkm2 closed under 2009 mm, seed 42 @ 436/452 3.7 Mkm2 closed, seed 11 @ 192 4.3 Mkm2; see inbox draft-fresh-hollow-closed-lakes.md). The new valley column is resampled nearest-cell like the others, so it also suffers the duplicate/hidden-cell artefact (an outlet cell hidden for a step loses its gap; _fill averages it from neighbours). Re-measure with docs/review/audit/basins-lakes/hollow_budget.py before designing the interpolating world view.
- 2026-10-16: Status todo -> blocked. Blocked by PW-358 (lake evaporation) per the v1 reassessment: re-measure the closed-hollow volume after it lands.
- 2026-10-16: Status needs-decision -> todo. Owner 2026-10-16: coordinator's call. Coordinator: park until PW-358/PW-015 land (giant lakes now trace to open-water evaporation); then re-measure whether resampling hollows still matter before designing an interpolating world view.
- 2026-10-16: Status in-progress -> needs-decision. Confirmed a resampling artifact (~75k km3 of lake-kept hollow re-cut per L6 step on rigid interiors). A one-to-one sampling map didn't remove it; a real fix needs an interpolating world view (design decision).
- 2026-10-16: Tectonics night lane (2026-10-16): confirmed a resampling artifact. L6 seed 1 0-300 Myr, land cells >= 3 cells from any boundary (rigid interiors): resolve adds +75k km3 of lake-kept closed hollow per step there (hydrology._bed filter; erosion fills ~82k), while the raw hollow volume there doesn't change (-9k): the same relief, re-cut. Nearest-cell sampling of a rotated grid shows 14.8% of world cells on a duplicated plate cell and hides 7.4% of plate cells; each step a world cell sees a different arrangement, so floors filled to 5 m below spill (PW-299) come back as >= 20 m hollows. Write-back loses 4.3% of each step's gross land change (last write wins). Tried a one-to-one map (unique_samples: a duplicate takes the hidden neighbour): duplicates 14.8 -> 10.6%, lost write-back 4.3 -> 2.7% (82 -> 28 km-cells/step), but interior hollow creation unchanged (+90k): not landed (docs/review/audit/tectonics-night/pw359-unique-samples.patch). Sound fix is a design change: an interpolating (area-weighted) world view of thickness/cover with changes interpolated back (categorical columns nearest), effort m-l; needs a decision (it blurs plate fields unless only the increments are remapped). Scripts: docs/review/audit/tectonics-night/resample.py, writeback.py.
- 2026-10-16: Status todo -> in-progress. Tectonics run-lane agent started.
- 2026-10-16: Created from inbox draft draft-resolve-makes-hollows.md (found by basins-lakes).
