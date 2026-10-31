---
title: The weathering sink's plants never starve at low CO2, so nothing stops a source dip short of tens of ppm
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane94
blocked_by: []
relates: [PW-1224, PW-1158, PW-1163, PW-880, PW-1156]
refs: [planet/tectonics/earth.py, planet/vegetation.py, docs/review/v1-cut/co2-crash-diagnosis.md]
---

## Description
In plain words. When CO2 gets very low, real plants starve, and the extra rock weathering they cause stops. That puts a
floor under CO2: Pagani et al. 2009 give this as the reason CO2 stayed above about 180 ppm for 24 Myr. In the model the
weathering plants keep most of their effect down to any CO2, so a world whose volcanoes quieten can fall to 36 ppm
(PW-1224's draw 639472).

Evidence (lane 94, docs/review/v1-cut/co2-crash-diagnosis.md):
- The weathering plants are grown at the balance's CO2 (`npp_w`, PW-880). Their CO2 dependence is GEOCARB's FERT
  `(2X/(1+X))^0.4`, which is still 0.44 at 36 ppm. The vegetation's own CO2 responses are held within 124-990 ppm
  (`vegetation.CO2_RANGE`).
- The model's own C3 quantum yield (`vegetation._q3`: Farquhar 1980, Bernacchi 2001 G*) at the sink-weighted cells is 3%
  of the balance's at 35 ppm and 13% at 50.
- Offline, in draw 639472 over 930-1000 Myr: scaling the planted enhancement (PLANT_WEATHER - 1) by
  `_q3(T, 0.7 Ca) / _q3(T, 0.7 x 124 ppm)` below 124 ppm only (FERT kept above) changes the end from 38 ppm, -10.3 C to
  73 ppm, -7.7 C (65 ppm, -8.2 C if 30% of the enhancement is C4/CAM and does not starve).
- Lane 92's tally: 6 of 36 L6 draws had minima under 124 ppm (88-119 ppm), so the change acts only in those dips.

Fix sketch: below the vegetation's floor, the planted part of the sink takes the C3 starvation ratio on its enhancement.
Better: lift the floor for the vegetation too, so biomes and the sink agree (C4 grass and CAM keep theirs). No new
constant. Watch for a double count with FERT above the floor.
- [ ] The law as a unit test against the doc's offline table
- [ ] Screen: 639472 l6fix r0.001 plus the 5 draws with minima < 124 ppm, arm against main. Minima rise; median end T
      moves under 0.3 C
