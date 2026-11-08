---
id: PW-290
title: The same seed is ~10 points more arid at L7 than at L6 (Koppen B 38-42% of land against 28-30%), with less tree cover
type: task
status: done
parent: null
milestone: null
subsystem: climate
effort: m
impact: med
found_by: health-sweep
blocked_by: []
relates: [PW-243, PW-013]
refs: [docs/review/health/2026-10-15/report.md, tools/health.py, "run a1d3b9", "run 550a5a", "run 9068cb", docs/review/climate/levels/scout1.md, planet/nest.py::climate_coarse, tools/ice_diag.py, "commit 14165233", "run a19366", "run 10fd90", "run fe954c", "run c9f38c", "run 5aa5ff"]
created: 2026-10-15
updated: 2026-11-08
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
- 2026-11-08: Status todo -> done. Scout 221: fixed by PW-015 stage 1 (14165233, 10-16). Same ground L7 vs nested L6 on main: Koppen B +0.84 pt, land rain +0.9%; fresh 1 Gyr seeds 3199/21 now 1-5 pt LESS arid at L7. Residual is resolved relief. Guard test drafted.
- 2026-10-15: Created from inbox draft draft-health-l7-drier-than-l6.md (found by health-sweep).
- 2026-11-08: Scout 221 (pass 1, main c2e54f2b; docs/review/climate/levels/scout1.md): the gap is gone, fixed by PW-015 stage 1 (14165233, 10-16, which named this ticket but never updated it). Same L7 ground, climate on L7 against the nested L6 grid: today +0.84 points of Koppen B on average (+0.5 to +1.1 over 9 moments of 5 runs), land rain +0.9%; on the 10-15 code (6926583) +6 to +8 points with land rain -27%; just before PW-015 stage 1 (1b2f0800) land rain -17% at L7, just after (f0197064) +3%. Fresh 1 Gyr pairs of the ticket's seeds 3199 and 21: L7 is 1-5 points LESS arid than the same seed at L6, over the whole run and in the finish window alike. The last ~1 point on the same ground is resolved relief (rain shadows L6 averages away), not a grid constant. Recommend closing; a guard-test draft is filed.
