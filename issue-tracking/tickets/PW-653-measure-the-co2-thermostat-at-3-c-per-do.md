---
id: PW-653
title: "Measure the CO2 thermostat at 3 C per doubling (PW-646 C): fb should go 0.35 -> ~0.5 C/C, and sink-side forcings (PW-636's NPP weathering) reach dT ~30% more"
type: task
status: todo
parent: PW-649
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: base-climate-laneA23
blocked_by: []
relates: [PW-646, PW-611, PW-576, PW-636, PW-644]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, tools/ice_diag.py, docs/review/base-climate/thermostat.md, docs/review/base-climate/laneA23/htable.txt]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane A23 (PW-646 option C) made `co2_sensitivity` 3 C per *doubling* of the stock's pCO2, where it was 3 C per
e-fold (2.1 per doubling). An e-fold of the stock now warms 4.33 C. Nothing else in the carbon cycle changed.

Expected from thermostat.md's numbers (the sink's g ~0.047 per C, WEATHER_CO2 0.4):
- the stock's answer fb = sensitivity per e-fold x g / WEATHER_CO2 goes from 0.35 to ~0.51 C/C;
- a non-CO2 cooling (the plants' albedo, PW-644) is damped by 1 / (1 + fb), ~11% less;
- a sink-side change (NPP-driven weathering, PW-636; mountain building) moves dT by sensitivity / WEATHER_CO2 /
  (1 + fb) per unit of ln sink, ~29% more.

Health quick on A22 + C, 16 seeds:
- deep-ice frames (< -150 m) back to main's level: mean 5.9% of keyframes, against A22's 13.4% and main's 3.8%;
- old ice bar fails 0, new 6 of 16 (as on main);
- median icehouse 23% and 34% on the two draws, against main's 18% and 27%.

Not measured:
- `tools/ice_diag.py --summary` on the 10 thermostat seeds (1 Gyr L6): the CO2 answer on the drift, N1-N4, and the
  icehouse share split of PW-611;
- whether PW-636's earlier flora now draws CO2 down further in dT.

What to run: ice_diag's 10-seed summary on this code. Compare it with thermostat.md's Stage 4 (+0.32 C/C, 5/10 in
band, icehouse median 54%).
- [ ] ice_diag --summary on the 10 seeds at 3 C per doubling, recorded in thermostat.md, with the CO2 answer and the icehouse share

## Updates
- 2026-10-23: Created from inbox draft draft-thermostat-gain-at-3c-per-doubling.md (found by base-climate-laneA23).
