---
id: PW-290
title: The same seed is ~10 points more arid at L7 than at L6 (Koppen B 38-42% of land against 28-30%), with less tree cover
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: health-sweep
blocked_by: []
relates: [PW-243, PW-013]
refs: [docs/review/health/2026-10-15/report.md, tools/health.py, "run a1d3b9", "run 550a5a", "run 9068cb"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-246 health sweep (2026-10-15, main 6926583, default params, 1 Gyr, medians over 50-1000 Myr of the
run keyframes). For the three seeds run at both levels:
| seed | arid (B) % of land, L6 / L7 | tree cover % of ice-free land, L6 / L7 | land % L6 / L7 |
|---|---|---|---|
| 3199 | 27.9 / 37.6 | 33.6 / 25.0 | 31.0 / 32.2 |
| 21 | 29.6 / 41.5 | 29.2 / 22.5 | 31.5 / 32.3 |
| 11 | 29.7 / 39.7 | 28.6 / 21.2 | 31.1 / 32.3 |
All 8 L6 seeds sit at 28-34% arid (Earth ~30%, the model on Earth's terrain 31%). Land, crust and
temperature medians barely differ between levels, so the climate itself (rain over land: moisture
transport per cell, rain-shadow sharpness on the finer relief, or the vegetation's rain recycling
feeding back) dries with resolution. Like PW-243's closed basins, a level-dependent result means
L6 checks don't carry over to the L7 showcases. NPP after flowering trees is ~5% lower at L7 (333-361
against 352-378 g C/m2/yr).
- [ ] compare land rain and its latitude profile for one keyframe of seed 3199 at L6 and L7
- [ ] find the term that depends on cell size; arid share within a few points between L6 and L7

## Updates
- 2026-10-15: Created from inbox draft draft-health-l7-drier-than-l6.md (found by health-sweep).
