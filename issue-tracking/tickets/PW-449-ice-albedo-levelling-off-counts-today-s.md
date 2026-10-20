---
id: PW-449
title: "Ice-albedo levelling-off counts today's ice in Earth's LGM change: 2.8 -> 8% iced gives 1.3 C, not ~2.6"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: high
found_by: pw448
blocked_by: []
relates: [PW-448, PW-435, PW-447, PW-030, PW-438]
refs: [planet/tectonics/earth.py, planet/timezoom/forcing.py, planet/timezoom/params.py, docs/review/audit/PW-448-diagnosis.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
The run's ice-albedo rule (`earth.py`: `ice_albedo_max * tanh(ice_albedo * f / 0.03 / ice_albedo_max)`,
1.5 C per 3% of the planet, max 3 C), which the time zoom has copied since PW-030, is annotated "Earth's
LGM ice sheets: ~2.5-3". That literature figure (Köhler et al. 2010: land ice -3.2 W/m2, ~-2.6 C at
0.8 C per W/m2) is the LGM's change from today. The tanh, though, already spends 1.4 C of its 3 C on
today's 2.8%, so going from 2.8% to Earth's LGM ~8% gives only 1.3 C. Physically, new ice spreading
equatorward gets more sun per km2, not less, so the levelling-off should start beyond LGM size.

Measured (PW-448, Earth L6, 600 kyr): `ice_albedo_max=30` (about linear) takes the time zoom's deepest
glacial from -42.8 to -70.8 m (dTg -1.86 -> -4.10 C; ice albedo -1.21 -> -2.75 C). Interglacial ice is
unchanged (29.0 vs 28.1 Mkm3), and it gives 5 endings (18-74 kyr) with no backstop instead of 2 and 1.
The Earth zoom sits near a loop gain of 1, so the slope matters this much.

Options:
- A. Fix the shared rule in `earth.py` and the time zoom together: the cap such that 2.8 -> 8% gives
  ~2.5 C (`ice_albedo_max` >= ~10-15), or an insolation-weighted area (annual sun at each iced cell's
  latitude x albedo contrast). Run lane (after PW-438). Every planet's icy-era climate changes, so it
  needs a run health sweep. Lean.
- B. Time zoom only (`TZParams.ice_albedo_max`). Quick, but it undoes PW-030's run/zoom consistency, and
  a run's moment would no longer sit at the zoom's balance in the same way (PW-436).
- C. Leave it. The glacial stays ~-43 m.
- [ ] decide; then re-measure Earth (depth, interglacial 8-9% of land, endings) and one cold run moment

## Updates
- 2026-10-20: pw449 (4 attempts, not merged): physical rules are insolation-weighted (A1) and add the bare ground's snow-free season (A2-A4). A1: Earth zoom -47.6 m, dTg -2.8 C, 0 backstops, but the run's cold eras pass on only 4/10 seeds (main 8/10). A2: run 9/10, Earth -32.6 m with 2 backstops. A3/A4: run 5/10, Earth -35 m. A rule calibrated on the LGM's real ice-albedo forcing can't reach ~-70 m with the model's high-Arctic ice: that depth is PW-435/PW-033/PW-450. Tables and options in inbox draft draft-ice-albedo-physical-rule-run-vs-zoom.md; patch docs/review/audit/PW-449-snow-season.patch.
- 2026-10-20: Status needs-decision -> todo. Coordinator decision 2026-10-20 (owner delegates physics): option A. Re-anchor the levelling-off in the shared rule, run and time zoom together, in the run lane right after PW-438 lands. Condition: the run's 4-seed L6 cold-era table (PW-438) must not get worse; a stronger ice-albedo slope could deepen the run's cold eras, so measure it.
- 2026-10-20: Created from inbox draft draft-ice-albedo-levelling-off-misanchored.md (found by pw448).
