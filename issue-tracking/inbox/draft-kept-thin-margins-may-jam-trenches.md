---
title: With the 15 km shred bound, the spin-up's arcs and ridges are weaker; check whether kept thin margins jam trenches
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: med
found_by: lane-115
blocked_by: []
relates: [PW-1295, PW-1314, PW-558]
refs: [planet/tectonics/crust.py::coherence, planet/tectonics/crust.py::arc_growth, planet/tectonics/crust.py::thermostats, planet/tectonics/earth.py::global_temperature, docs/review/tectonics/margin/pw1295-note.md, docs/review/tectonics/margin/envdraw.py, tests/test_envelopes.py]
---

## Description
In plain words: keeping 15-20 km margin cells as continent (PW-1295's 15 km shred bound) makes the young planet's
volcanoes at trenches and its mid-ocean ridges about 7% weaker in the first 300 Myr. The CO2 thermostat learns that
weaker outgassing as normal, and when it recovers the world warms; on the test_envelopes world's seed 2 that ran to a
28.8 C hothouse, so the bound was reverted.

Numbers (pw1295-note.md section 4, L5, 400 Myr, 20 seeds): spin-up source lower with 15 km on 17 of 20 (median -7%);
on 7 traced seeds ridges and arcs lower on 6/7, plates slower on 4/6, subduction erosion's area gain higher on 7/7,
continental area at 100 Myr higher on 7/7.

Likeliest reason (not shown): the kept thin margin on a plate's leading edge meets a trench as continental crust, so
it jams instead of subducting, which shortens the subducting trench and slows the plates.

What to try:
- [ ] count, per step, trench edges whose sinking-side cell is continental and 15-20 km, both bounds, seeds 1-8
  (envdraw.py plus `bd.at_trenches`), and the subducting trench length
- [ ] if that is the difference: let continental crust thinner than BECOMES_CONT_KM subduct like ocean floor; screen
  on the 20 envelope seeds (band count and spin-up source) before any judge
