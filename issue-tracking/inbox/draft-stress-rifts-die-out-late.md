---
title: Stress rifts die out after ~600 Myr (10-16 per 200 Myr -> 1-5), so ridges shorten and the floor ages to 75-120 Myr
type: task
status: todo
parent: null
milestone: null
subsystem: tectonics
effort: l
impact: med
found_by: pw549
blocked_by: []
relates: [PW-549, PW-051, PW-024, PW-191]
refs: [planet/tectonics/events.py, planet/tectonics/motion.py, docs/review/audit/pw549-sea-level.md]
---

## Description
PW-549's diagnosis (10 L6 seeds x 1 Gyr, 5 of them to 2 Gyr, scratch diagnostics in docs/review/audit/pw549-sea-level.md):
the ocean floor ages from ~48 Myr to 66-92 Myr by 1 Gyr on the deep-sea seeds and sits at 60-120 Myr through 1-2 Gyr.
It isn't the plates slowing: mean cell speed is ~3.5-4.2 cm/yr from ~300 Myr to the end on every seed. What falls
is the plate-boundary length (ridge and trench edge sums -40% on seeds 2 5 7 13 99; plates 12-13 -> 6-9), because
**stress rifts** (events.maybe_rift's stress hazard) fall from 10-16 per 200 Myr in the first 400 Myr to 1-5 per
200 Myr after ~600 Myr on those seeds, and stay there to 2 Gyr; new plates then come mostly from margin subduction.
Seeds whose ocean stays young (3199, 11, 1) keep 8-10 rifts per 200 Myr. The floor's half-space heat flux falls
from ~100 mW/m2 (Earth's ocean) to 75-85 at a constant mantle heat.

Not the cause, checked: craton share of continental crust only rises 53 -> 60% (stored v1 runs 9b685e, 0ecb0d),
orogen belts fall 47 -> 24%, so mean continental strength rises ~6%, too little alone for a 3-5x rate drop.
Candidates to look at: the starting supercontinent's insulated warm mantle (warm_rift) fading after the breakup,
so later continents never sit still long enough to re-weaken; the opening-stress threshold `rift_stress` being
met mostly by the breakup's forces; whether a supercontinent re-assembles at all (largest landmass 20-33%).

Tried in PW-549 and not kept: a mantle heat budget (Tozer thermostat: plate mobility x e^(integrated heat
imbalance / 340 Myr), derived constants). Over 1 Gyr it moved vigor only 0.9-1.2x and didn't change the floor's
age, because slab-driven plates run at their slab's terminal speed (slab_pull / slab_drag), which mobility doesn't
set, and the deficit is in ridge length, not speed.
- [ ] find why stress rifting stops after the first breakup; measure rifts per 200 Myr over 2 Gyr
- [ ] the floor's mean age over 300-2000 Myr stays within ~50-80 Myr on ~70% of seeds
