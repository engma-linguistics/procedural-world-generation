---
title: "Time zoom's climate has no vegetation feedback (veg=None): no forest-to-tundra snow albedo in glacials"
type: task
status: todo
parent: null
subsystem: timezoom
effort: l
impact: med
found_by: pw448
blocked_by: []
relates: [PW-448, PW-033, PW-435]
refs: [planet/timezoom/fields.py, planet/climate.py, planet/tectonics/earth.py, docs/review/audit/PW-448-diagnosis.md]
---

## Description
`ClimateFields.refresh` calls `climate.compute(..., veg=None)`, so the time zoom's climate never
feels its vegetation: no Budyko w and no `albedo_warming` (snow masking by forest), unlike the run
(`earth.veg_feedback`). Earth's LGM budget has vegetation at ~-1.1 W/m2 (Köhler et al. 2010, ~-0.9 C),
and forest retreat is the classic amplifier of Laurentide inception. PW-448 measured that the
Canadian interior lacks 9-11 C of summer cooling at glacial orbits, and even at an Earth-like -5 C
global the ice goes to Siberia and Alaska instead (diagnosis section 2).
Doing it needs `vegetation.model` at each full-climate refresh (flow, lakes and clouds as inputs, the
cheap warm-started variant). Measure its regional effect on Keewatin, Labrador and Fennoscandia summers
before wiring it into the mass balance.
- [ ] vegetation feedback in the time zoom's full climate, its glacial effect measured
