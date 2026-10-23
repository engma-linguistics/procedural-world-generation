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
- 2026-10-23: Thermostat lane 1024 (in progress): ice_diag on the 10 seeds, main (PW-627): CO2 answer +0.24 C/C trends out, 2/10 in band, sink's own fb +0.43, source +0.17; c13b567 (before PW-627): +0.42, 5/10, sink fb +0.59 (A23's expected ~0.5). The climate's static sink sensitivity is the same on both trees (Earth and 3 L5 moments, to 1%), so the drop is the runs' or chaos. docs/review/base-climate/thermostat-1024/handoff.md.
- 2026-10-23: Merge lane 1024, step 4 (main + A23 real pCO2 + A20 shelf air + PW-627): health --quick pooled keyframes with ice sea level below -150 m, main 4.2 / 3.4%, step 4 4.4 / 20.1% (defaults / 101-108); 5 of 8 seeds of 101-108 deep, median icehouse 57%, old ice bar fails 3 of 16 (main 0). The thermostat's gain is the next lever. docs/review/base-climate/merge-1024/.
- 2026-10-23: Created from inbox draft draft-thermostat-gain-at-3c-per-doubling.md (found by base-climate-laneA23).
