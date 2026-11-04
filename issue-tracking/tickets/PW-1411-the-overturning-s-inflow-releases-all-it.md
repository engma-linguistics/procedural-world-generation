---
id: PW-1411
title: The overturning's inflow releases all its heat by 65 N and sinks off East Greenland, so the Nordic seas get too little of it
type: task
status: todo
parent: null
milestone: later
subsystem: ocean
effort: m
impact: med
found_by: lane142
blocked_by: []
relates: [PW-1381, PW-582]
refs: ["planet/ocean.py::overturning", "planet/ocean.py::_along", "planet/ocean.py::_slope_current", docs/review/base-climate/n-atlantic/round1.md, docs/review/base-climate/n-atlantic/heatcross.py, docs/review/base-climate/n-atlantic/seabox.py, docs/review/base-climate/n-atlantic/ec.sh, docs/review/base-climate/n-atlantic/summ.py, docs/review/base-climate/n-atlantic/launch.sh]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: the warm Atlantic water should carry about a third of its heat past Iceland into the Norwegian Sea.
In the model it gives almost all of that up just south of Iceland and sinks off East Greenland.

Earth L6:
- The N Atlantic's one sinking site is at 68 N, 33 W (12.5 Sv), the Denmark Strait / East Greenland side.
- `heatcross.py`, the inflow's heat above its sinking water: 0.61 PW at 60 N, 0.09 PW at 65 N (main,
  moc_lambda 30); 0.40 at 60 N, 0.02 at 65 N (moc_lambda 60).
- Observed: OSNAP carries 0.45 PW (Lozier et al. 2019, Science 363, 516), most of it across OSNAP East into the
  Nordic seas (0.38 PW). The Nordic seas hold the deepest winter mixed layers with the Labrador Sea (Holte et al.
  2017, GRL 44, 5618).

On main the Nordic seas' SST happened to be right (7.4 against OISST 7.2), because the inflow came in too warm
(the subpolar box 3 C warm, PW-1381). With PW-1381's moc_lambda 60, the subpolar box is right and the Nordic seas
are 2.7 C cool (4.5), the 60-70 N sea band 2.2 C cool, and its rain 610 against GPCP 905.

What I'd look at:
- whether the route east of Iceland is open at L5 (the moc_level grid; `_straits` over the Iceland-Faroe-Scotland
  ridge, ~400-850 m);
- whether a second sinking site in the Greenland Sea can win;
- whether the inflow's heat in the Nordic seas should relax toward the latitude's sea when it is under the slope
  current (`_slope_current`).

- [ ] on Earth L6, the inflow's heat left at 65 N is >= ~0.2 PW, and the Nordic seas' annual SST is within ~1 C of
  OISST, with the 40-60 N box no warmer

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: ocean calibration against Earth sea temperatures; Earth is a plausibility anchor, not a target
- 2026-11-03: Lane 150 (merged, docs/review/base-climate/nordic-seas/round1.md): three strikes (A relax to sst0, B sea-warmed air, C Clausius-Clapeyron lambda), back of the line. Correction: the overturning does not sink off East Greenland; 67.3N 32W is the centroid of one 5.1 Mkm2 Labrador-to-Barents area (Labrador 3.84 Sv, Irminger/Iceland 2.92, north of the ridge 5.80 vs obs ~6). Volumes about right; the inflow crosses the ridge at 3.8 C, 118 TW vs Tsubouchi 2021's 305 TW. Next try needs structure (air pass inside ocean.solve; surface imprint, PW-1419).
- 2026-11-03: Created from inbox draft draft-inflow-misses-nordic-seas-interior.md (found by lane142).
