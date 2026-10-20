---
id: PW-450
title: "Time zoom's climate has no vegetation feedback (veg=None): no forest-to-tundra snow albedo in glacials"
type: task
status: done
parent: null
subsystem: timezoom
effort: l
impact: med
found_by: pw448
blocked_by: []
relates: [PW-448, PW-033, PW-435]
refs: [planet/timezoom/fields.py, planet/climate.py, planet/tectonics/earth.py, docs/review/audit/PW-448-diagnosis.md]
created: 2026-10-20
updated: 2026-10-20
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

## Updates
- 2026-10-20: Status todo -> done. Merged ec36451 (coordinator 2026-10-20): the run's vegetation in the time zoom, with local and global terms. Earth -42.8 -> -45.1 m, no backstop. The term is ~0 at the deepest because the tropics green (new ticket).
- 2026-10-20: pw450: the time zoom grows the run's vegetation (planet/timezoom/plants.py: cheap model per full climate, in balance at the start; local feedback as the run's plus a global albedo term from the start, `veg` on/local/off). Earth zoom -42.8 -> -45.1 m, backstops 1 -> 0, interglacial ice 8.7-9.8% of land, Laurentide unchanged (1.6 Mkm2, 54.9 N); saved 098d5d. The term is ~0 at the zoom's deepest (-0.02 C; 45-90 N -0.07..-0.12 W/m2 cancelled by greener tropics) and -0.32 W/m2 at a prescribed -6 C (LGM -1.1): docs/review/audit/PW-450-vegetation.md. Tropics' wrong sign: inbox draft draft-glacial-tropics-green-not-dry.md. Runtime +11%.
- 2026-10-20: Created from inbox draft draft-timezoom-no-vegetation-feedback.md (found by pw448).
