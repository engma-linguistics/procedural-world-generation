---
id: PW-1412
title: The winter air over the open sea sits almost at the water's temperature; over the N Atlantic the real air sits ~2.4 C below it
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane142
blocked_by: []
relates: [PW-1381]
refs: ["planet/climate.py::_winter_air", "planet/climate.py::TUNE", docs/review/base-climate/n-atlantic/round1.md, docs/review/base-climate/n-atlantic/seabox.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: in winter, cold air from the continents flows out over the warm Atlantic. The real air stays a few
degrees colder than the water for a long way. In the model it takes on the water's temperature almost at once.

Earth L6, coldest month, the air's temperature minus the sea's (model against NCEP's 2 m air minus OISST v2's sea):

| box | model | NCEP minus OISST |
|---|---|---|
| N Atlantic storm track | -0.5 | -2.4 |
| NW 50-60 N | -2.1 | -4.7 |
| SW 40-50 N | -0.1 | -2.8 |
| NE 50-60 N | -0.2 | -1.6 |

That is ~1.9 C of the box's 5.7 C winter air excess (PW-1381).

`_winter_air` relaxes the air over open water to the water's winter over `air_km_sea` (300 km, from 500 m of
boundary layer over C_H). Raising it to 600 / 1000 km cools the box's winter air by 0.7 / 2.0 C. But it overshoots
the Nordic seas (5.2 -> 3.0 / 0.3 against NCEP 2.1), so the fetch alone isn't the mechanism.

Probably missing: a sea losing heat in winter keeps its air below it by the sensible flux over rho c_p C_H U (bulk
formula), everywhere, not only downwind of land. Needs a source for C_H and the observed fluxes before screening
(the helper found none it could open for the N Atlantic gap itself).

- [ ] the coldest month's air minus sea within ~1 C of NCEP minus OISST in the four boxes above, with the Nordic
  seas' winter air no worse

## Updates
- 2026-11-03: Created from inbox draft draft-winter-air-over-heat-losing-sea.md (found by lane142).
