---
title: "Zoom doesn't keep coarse cell means: valley carving lowers land ~60-90 m, trenches lose ~3 km"
type: task
status: todo
parent: PW-245
subsystem: zoom
effort: s
impact: med
found_by: audit-coast-zoom
blocked_by: []
relates: []
refs: [planet/zoom.py, docs/overview.md, docs/review/audit/coast-zoom.md, "world 592f2a"]
---

## Description
The overview (§2.13) and zoom docstring say every coarse cell's mean height is kept. Staged measurement on
an L7 zoom of 592f2a (-9.35/-161.39, 2000 km at 4 km): land cells away from the coast have bias/RMS
-0/93 m after the detail's mean correction, then **-58/185 after the coarse valleys are carved**
(zoom.py:1455 `smin(h, T)`, no correction after it), -66/226 after the landscape pass (C is fitted to
box means of the carved target, `tmean` at 2094, not to the coarse means) and -86/234 at the end. Cells
above 1500 m: -96/269.

Sea cells away from the coast: +415/912 m. One-cell-wide trenches at -7,700 m come out at -3,700 to
-5,600 m, because `e_sea` is a σ = 0.5 cell Gaussian and the two Gaussian-smoothed mean-correction passes
(1118-1123) can't restore a narrow feature. This dominates `stats.cell_mean_rms_error_m` (516 m here), which
no test or doc checks.

Fix (simplest sound): compute `tmean` from the surface before carving (or re-run `keep_means` on land
outside the valley bottoms after carving); for the sea, more correction iterations or a narrower kernel
where coarse relief is steep. Add a test or golden stat on land-interior cell-mean bias.
- [ ] land-interior cell-mean bias within ±20 m, RMS < ~120 m on this zoom
- [ ] trench cells within ~500 m of their coarse depth
