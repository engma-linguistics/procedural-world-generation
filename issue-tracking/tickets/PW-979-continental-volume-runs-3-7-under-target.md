---
id: PW-979
title: Continental volume runs 3-7% under target all run although the arc thermostat's gain climbs to 2-3
type: task
status: todo
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: low
found_by: lane23
blocked_by: []
relates: [PW-970, PW-749, PW-046, PW-052]
refs: [planet/tectonics/crust.py, docs/review/tectonics/crust/crust.md, docs/review/tectonics/crust/areadiag.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Lane 23's area budget (docs/review/tectonics/crust/areadiag.py) showed two halves to PW-970's thin crust. The area
half (coherence welds ratcheting continental area) is fixed. The volume half remains, and it was there before
the rift fixes too:
- L5 400 Myr: continental volume / target 0.91-0.93 on main and on the pre-rift code (seeds 1-2), with
  crust.thermostats' arc gain at x2.3-3.0 and its integral 0.14-0.17 of the 0.4 cap, still climbing.
- After the weld fix: 0.94-0.95 at L5 400 Myr, and 0.965-0.975 at L6 1 Gyr (gain x2.3-2.4).
- L5 seed 2 budget over 400 Myr (km x L5 cells): arcs +15k, subduction erosion -33.5k, resolve -33.6k against
  collision +29.3k, erosion -5.8k. The area thermostat's lever (subduction erosion, x shrink) also removes volume
  (~21 km per cell of area it takes), so whenever area runs over target, volume is pulled under it, and the
  volume thermostat answers only through continental arcs, by a slow integral (THERMO_MYR 100 Myr, x e^(4 err)).

Thickness = volume / area, so a 3-5% volume shortfall costs ~1-1.5 km of mean continental crust at L6.
Options:
- A. Find which volume sink is out of scale (subduction erosion's 120 km forearc rate; resolve's crust lost at
  overlaps that the collision stacking doesn't put back: -33.6k vs +29.3k) and size it from the literature
  (Scholl & von Huene 2007/2009 give the global subduction-erosion and sediment-subduction fluxes).
- B. Leave it: thickness is now 33-34 km at L6 (Earth ~35-40), within the owner's 33-35 km target.
Lean: B for v1, A in v2 with PW-749.
- [ ] per-process volume budget in km3 at L6 and L7 over two seeds; the sink whose rate per km of trench or
  boundary is off, sized from a source

## Updates
- 2026-10-28: Created from inbox draft draft-crust-volume-thermostat-shortfall.md (found by lane23).
