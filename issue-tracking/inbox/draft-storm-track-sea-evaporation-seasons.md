---
title: The storm-track seas evaporate a third to a half of NCEP's in winter and 1.4-2.8x in summer
type: task
status: todo
parent: PW-015
milestone: v2
subsystem: climate
effort: l
impact: med
found_by: lane58
blocked_by: []
relates: [PW-1093, PW-1096]
refs: [planet/climate.py, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
---

## Description
In plain words. Over the North Atlantic and North Pacific at 40-60 N the model's sea evaporates most in summer and
little in winter. The reanalysis has it the other way round. Its sea evaporates most in winter, when cold, dry air
off the continents crosses warm water. In the model those seas don't make their own winter vapour. They get it from
the south (the storms' drift brings +143 mm/yr into the Atlantic box), and they rain it at 0.7-0.8 of the observed
rate per mm.

Earth L6, 347b4374 (`tools/moisture_regions.py`; mm/yr as a half-year rate, model / NCEP E):

| box | Apr-Sep E | Oct-Mar E | Oct-Mar P / GPCP | Oct-Mar q/qs |
|---|---|---|---|---|
| N Atlantic 40-60 N, 60-10 W | 846 / 610 | 448 / 1339 | 1197 / 1651 | 0.92 |
| N Pacific 40-60 N, 145 E-130 W | 759 / 268 | 430 / 882 | 1214 / 1465 | 0.93 |

Likely cause (unverified): the bulk exchange drives the air toward 0.98 of saturation at the SST. The kernel's
one-layer air has no temperature of its own, so cold-air outbreaks over warm water get no extra deficit. Warm-advected
air from the subtropics arrives near saturation for the colder sea.

NCEP's E is a reanalysis (high by ~10% globally), but the seasonal sign is the issue, not the size. This is PW-015's
boundary-layer option (A). Not a v1 blocker.
- [ ] storm-track seas' Oct-Mar E within 2x of NCEP and peaking in winter
