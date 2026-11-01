---
title: The arc CO2 source follows the continental volume thermostat, so sediment processes steer the climate
type: task
status: needs-decision
parent: null
subsystem: tectonics
effort: l
impact: med
found_by: lane-100d
blocked_by: []
relates: [PW-950, PW-1158, PW-576]
refs: [planet/tectonics/earth.py, planet/tectonics/crust.py, docs/review/tectonics/margin/diagnosis-land.md]
---

## Description
In plain words: the model keeps the continents' total volume steady by growing volcanic arcs when the volume runs
low, and it counts the arcs' growth as volcanic CO2. So anything that moves crust in or out of the continents also
changes the CO2 the volcanoes give off: erosion, sediment carried out to sea, sediment piles that become new
continent. With the new sea-floor creep (PW-950) the arcs grew 20% faster early in the run and 14% slower late. The
CO2 source's reference is learnt in the first 300 Myr, so the late source sat below it and the world came out ~3 C
colder (L6 seeds 1 and 3, slope_k=1000). Real arc CO2 comes from the sinking slab and the mantle above it, not from
how much crust the continents need.

Where: `earth.global_temperature`, source = new floor + `20 x growth` (the arcs' growth at the volume thermostat's
rate, `crust.thermostats`) + plumes. Lane 100d's trace (docs/review/tectonics/margin/diagnosis-land.md, part 2):
seed 1 arc growth 10 935 / 19 889 / 28 787 (main) against 13 096 / 25 745 / 24 821 (creep) km x L5 cells over 0-300
/ 300-600 / 600-1000 Myr; raw source 2551 / 2729 / 3001 against 2882 / 2774 / 2719. Late source / reference 1.12 /
1.24 against 0.97 / 0.92 (seeds 1 / 3), pCO2 1290 / 1120 against 789 / 750 ppm.

Options:
- A. Arc outgassing from the slab: convergence rate x trench length (both in the model), at the same mean. The arc
  crust's growth stays on the thermostat. This cuts the link outright, but re-sets the source's calibration and
  needs a full judge.
- B. Count the continent-derived sediment on oceanic crust in the volume thermostat's volume, so that moving sediment
  to the continent's foot doesn't call for arcs. Narrower, and main moves slightly (0.42 km of cover on the ocean
  floor, ~1.7% of the continental volume).
- C. Keep sediment-born rises out of the area thermostat (they are drowned rises on oceanic crust, not continent).
  This removes the late-run swap of arcs for born rises. It's the narrowest, but it treats a symptom of A.
Lean: A, because that's the physics. Try C first as a cheap screen with the creep on. Related: PW-1158 (the source
running low late in some runs).
- [ ] decision A / B / C
- [ ] the chosen change judged paired (18 x 2) against main, then with slope_k on
