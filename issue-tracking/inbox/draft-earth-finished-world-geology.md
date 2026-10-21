---
title: Earth finished worlds carry a rough terrain-derived rock map and no landform classes
type: task
status: todo
parent: null
subsystem: timezoom
effort: s
impact: low
found_by: pw092
blocked_by: []
relates: [PW-494, PW-092]
refs: [planet/finish.py, tools/earth_world.py, "world 577526"]
---

## Description
A finished Earth world had no `rock` layers at all, so no regional zoom could be made of it (zoom needs them): PW-092 moves tools/earth_world.py's `earth_rock` (rugged ground = orogen, plains and shelf = sediment, rest craton) into `finish.earth_rock` and adds it to `finish._earth_world`. That is the same rough map the observed Earth world uses; it has no reef limestone (earth_world.build's second pass), no `landform` layer (so no shield, fold-belt, karst, dune classes in Earth zooms) and no `glaciated_myr`. PW-494 (GLiM erodibility) is the real fix for the rock; the landform classes need `landform.classify` on a rock record Earth lacks. Old finished Earth worlds (f6e955) have to be re-finished (f6e955 deleted and redone as 577526).
- [ ] Earth zooms get GLiM rock and landform classes (karst, dunes, fold belts)
