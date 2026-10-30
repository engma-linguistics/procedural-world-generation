---
title: "The run's sheets still keep about 10 points of extra land ice at dT -4 on the way back up"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane71
blocked_by: []
relates: [PW-1142, PW-464]
refs: [tools/ice_probe.py, planet/tectonics/earth.py]
---

## Description
In plain words. When the Earth test planet is cooled step by step and then warmed again, its ice should come back
down the same way it went up. With lane 71's warm-phase changes it nearly does at today's temperature (10.3% of
land against 8.6% going down). But halfway back, at 4 C below today, it still holds 22.9% against 13.0% going down.
Real ice sheets also lag on the way out (the Laurentide was still large partway through the last deglaciation), so
some gap is real. But a gap of 10 points held for millions of years of run time is more than a lag.

Lane 71's Earth staircase (L6, 4 climate updates a step): the gap at 0 / -2 / -4 is 5.3 / 11.8 / 11.9 points on
main, and 1.8 / 3.7 / 9.9 with the warm-phase kitchen sink. The leftover sits in NW America (lat 47-69 N, beds
near sea level, 1.3-1.6 km thick). Its surface stays below freezing in every orbital state, so averaging the melt
over the states can't touch it. Candidates: isostatic lag, which the run settles at once (Abe-Ouchi et al. 2013
credit it for terminations; not read here); the sheets' carried air (lane 67: with it turned off the gap shrinks
20-50%).
- [ ] The staircase gap at -4 within ~3 points, with the down-leg still ~25% at -8
