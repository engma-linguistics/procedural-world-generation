---
title: "Ice sheets' own cold summer air: carry it along the winds (katabatic) instead of a local damping?"
type: task
status: needs-decision
parent: null
subsystem: climate
effort: m
impact: high
found_by: pw313
blocked_by: []
relates: [PW-313, PW-112, PW-039, PW-277, PW-190, PW-013]
refs: [planet/climate.py, planet/icemass.py, planet/timezoom.py, docs/review/audit/pw313-polar-summers.md]
---

## Description
A sheet's own cold, bright air mass is currently a local damping of each ice cell's summer (`icemass.sheet_cover`:
0.6 x the share of the surface within 1000 km under ice). The climate's air that reaches the ice, its margins and
the land beyond still comes off the bare ground's summer, +13 C over Antarctica's bed. Measured on Earth (L6,
dT 0), the Antarctic ice surface's warmest month is 5 C too warm at the median. Against stations: South Pole -9.9
(obs -28), Vostok -14.4 (-32), Byrd -7.8 (-14), Halley +5.2 (-4) (PW-039). Greenland's interior is about right
(Summit -13.3 vs -12).

Measured design (about 40 lines; not merged). `climate.compute` gives the air over land ice the ice's damped
summer (`SUMMER_DAMP` x the old sheet_cover formula, renamed `air_mass`), and the summer carry takes it on along
the winds (katabatic outflow onto margins, shelves and nearby land). `icemass.sheet_cover` becomes just the
surface's own share (`LOCAL`), so nothing is counted twice. The time zoom's full climate passes its ice
(`ice_air`). Warmest month:

| | base | A: carried, air-mass weighted | B: carried, full damping | obs |
|---|---|---|---|---|
| South Pole / Vostok | -9.9 / -14.4 | -18.7 / -22.8 | -20.6 / -24.6 | -28 / -32 |
| Byrd / Halley / Mawson | -7.8 / +5.2 / +1.7 | -10.3 / -2.8 / -0.1 | -13.7 / -5.8 / -3.2 | -14 / -4 / 0 |
| Summit / Swiss Camp (Greenland) | -13.3 / -4.2 | -16.6 / -6.5 | -23.2 / -8.4 | -12 / 0 |
| PW-313 probe, dT 0 after 8 updates | 0.10% | 1.18% (Greenland decays too) | 2.96%, steady | ~3% |

Options:
- A. Carried, air-mass weighted. Antarctica's coast and WAIS come within 0-4 C, the plateau error halves, and
  Greenland's interior is ~3 C colder. Holds Antarctica in the probe only with realistic snowfall (with Antarctic
  snow x2.5: 2.55%, -50 m).
- B. Full damping. Passes the probe now, but only with Greenland's summit 11 C too cold: a compensating error.
- C. Keep the local damping and fix the snowfall first (PW-013), then re-measure.
Lean: A, landed together with the snowfall fix (draft-antarctic-margin-snowfall) and the frozen-sea summer air
(draft-frozen-sea-summer-air). The remaining Antarctic plateau error (~9 C) is the high dry plateau's own surface
energy balance and inversion, which no bare-ground damping captures.
