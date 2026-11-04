---
id: PW-1226
title: The weathering sink's net climate gain is 0.044 per C of dT in a cold episode, against the design's 0.070
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: s
impact: low
found_by: lane94
blocked_by: []
relates: [PW-1224, PW-235, PW-881]
refs: [planet/tectonics/earth.py, planet/climate.py, docs/review/v1-cut/co2-crash-diagnosis.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
In plain words. As a world cools, weathering should slow and let CO2 build back up. In PW-1224's crash draw it slowed
less than the model's own design figure, because nearly all the weathering happens in the tropics. The tropics cool least,
and fresh mountain rock keeps arriving there.

Evidence (lane 94, draw 639472 l6fix r0.001, 930 to 990/1000 Myr, per-cell snapshots):
- 84-93% of the sink lies within 15 degrees of the equator. The global climate factor `w_temp` fell ln -0.47 for -10.5 C
  of dT (0.044 per C), against `climate_coef()` = 0.09 x 0.6 + 0.016 = 0.070.
- On cells weathering at both times, the factor fell 0.91 e-folds for -8 C (local T -3.9 C, ln runoff -0.85), which is
  strong. But 59% of the 990 sink was on newly eroding cells (supply-weighted |lat| 20 to 13 degrees), which cancels about
  two thirds of the response. Much of this is real geography: a colliding belt in the tropics.
- The tropical land cooled about 2.7 C for 8 C of dT on fixed cells, against `temp_response`'s 0.5 per C. That is
  confounded by 60 Myr of plate drift.
- At the design gain the draw would end at 58 ppm instead of 38 (offline). So this is a minor part of the crash.

Cheapest check: on one terrain, `climate.compute` at dT 0 and -8 (seconds). Compare the land's cooling by latitude band
with `temp_response` (and the runoff's with RUNOFF_PER_C). Act only if the climate model's tropical land cools much less
than 0.5 per C.
- [ ] The fixed-terrain comparison, with a yes/no on whether the climate model or the geography explains the gap

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-10-31: Created from inbox draft draft-weathering-land-temperature-response.md (found by lane94).
