---
title: "Sustained rifting (PW-565) spreads continents thinner: L5 envelope test_land_and_crust[2] at 27.7 km < 28"
type: task
status: needs-decision
parent: null
milestone: v1
subsystem: tectonics
effort: m
impact: med
found_by: lane22
blocked_by: []
relates: [PW-565, PW-952, PW-749, PW-046, PW-052]
refs: [planet/tectonics/crust.py, planet/tectonics/events.py, tests/test_envelopes.py, docs/review/tectonics/rifts/rifts.md]
---

## Description
Lane 22's rift fixes (settle clock only for the new plate, stress ~ sqrt(area), plume triple junctions) keep
stress rifting at ~12-17 per 200 Myr all run instead of dying to ~5 after 600 Myr. Every continental rift lays thin
margin crust (12-18 km) in the opening rift, and subduction erosion (the area thermostat, crust.thermostats) does
not remove it as fast, so the continents' area runs higher and, at a held volume, they are thinner:
- L6 1 Gyr mean continental crust: seed 1 33.5 -> 31.6 km, seed 2 32.6 -> 31.5 km; continent 42% -> 42-45%.
- L5 400 Myr (test_envelopes' fixture, seeds 1-4): main 29.6 / 31.6 / 30.5 / 30.9 km, branch 27.7 / 29.4 / 29.0 / 28.8.
  At L5 seed 2 the area thermostat's factor is x2.6 and its integral 0.17 of the 0.4 cap at 400 Myr, still climbing.
- So the slow envelope test_land_and_crust[2] fails (27.7 < 28 km). The bound was not loosened.
With triple junctions off, L5 seeds 1-2 are close to main (30.1, 31.2 km), but seed 2's thinning on the branch comes
from ordinary continental stress rifts at 250-400 Myr (area 40 -> 46%), not a triple split: it is the rifting rate.

Options:
- A. Make the area thermostat answer the margin crust: e.g. a shorter THERMO_MYR or count rifted-margin crust
  (< ~20 km) at its volume share rather than as full continental area. Belongs with PW-749 (the thermostats run
  differently by level). Lean: A, with the rift fixes merged first (a correct mechanism over a fitted downstream
  bound).
- B. Lay less margin crust per rift (thinner or narrower belts): changes margins and shelves (PW-950).
- C. Re-baseline the L5 thickness band once the owner accepts thinner L5 continents (the band's own comment says
  L5 has sat at 29.5-34.8 km across versions; L6/L7 are 34-36 km on main).
- [ ] test_envelopes passes with the rift fixes in
- [ ] L6 continental crust back to ~33-35 km at 1 Gyr without bringing back the late giant plates
