---
id: PW-122
title: "Earth check: the Nile ends in a cell-scale pit in Nubia instead of reaching the sea"
type: task
status: todo
parent: null
subsystem: hydrology
effort: m
impact: low
found_by: lakesize
blocked_by: []
relates: [PW-055, PW-110]
refs: [planet/hydrology.py, tools/earth_check.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
After PW-110 the Earth check's Nile reaches Khartoum again (2.78 of observed
with GPCC rain), but downstream it still ends in a closed basin at about
23.3 N 30.4 E (Lake Nasser / Toshka area): a 62,000 km^2 hollow 97 m deep in
the L6 cell-mean terrain (0.39 m/km, so neither the 20 m nor the slope rule
drains it). The real Nile crosses it in a gorge far narrower than a cell, so
the cell means (desert plateau) make a pit that isn't there. The discharge
check is unaffected (it reads the flow where the river ends), but the river
never reaches the Mediterranean.

Generated worlds can have the same thing: a big river whose valley is
narrower than a cell ends in a pit. A possible nudge: a hollow whose inflow
is large (big river) and whose rim is low relative to it drains by incision
(an antecedent gorge), e.g. allow a deeper min_depth for hollows fed by a big
river. Relates to PW-055 (giant open lakes: outlets should cut down).

## Updates
- 2026-10-14: Created from inbox draft draft-nile-ends-in-nubian-pit.md (found by lakesize).
