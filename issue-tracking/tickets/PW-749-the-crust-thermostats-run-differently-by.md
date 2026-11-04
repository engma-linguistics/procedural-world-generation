---
id: PW-749
title: The crust thermostats run differently by level (L6's volume gain climbs to ~2.5-4 and its area runs over target; L7's gain stays ~1.1-1.8 and its area under)
type: task
status: todo
parent: null
milestone: later
subsystem: tectonics
effort: m
impact: med
found_by: v1-finish-5
blocked_by: []
relates: [PW-741, PW-046, PW-052]
refs: [planet/tectonics/crust.py, docs/review/base-climate/v1-finish-5/]
created: 2026-10-24
updated: 2026-11-03
---

## Description
The same seeds at L6 and L7 (v1-finish-5's tracks, same code): the volume thermostat's gain on continental arcs
(crust.thermostats) climbs from ~1.4 at 300 Myr to ~2.2-4.4 at 900-1000 Myr at L6, and the area thermostat's
`shrink` (subduction erosion) climbs past 1-3 (the continents' area runs over its target, their thickness
~32 km); at L7 the gain peaks ~1.5-1.8 near 500 Myr and falls back, and shrink stays ~0.25-0.9 (area under target,
thickness ~34-35 km). Per 100 Myr the crust budget differs by process: L7 loses more to erosion (-4..-7 against
-3..-4 thousand km x L5 cells) and births more (+2 vs +1), L6 more to subduction erosion (shrink). So the crust's
area/volume balance still depends on the cell size (PW-052 fixed its first order).

Since PW-741 the climate no longer sees the gain (the arcs outgas at their nominal rate), so this is now a
tectonics-only resolution dependence: continental thickness (~1-3 km) and so hypsometry and land fraction by
level. Find which process's per-cell rule leaks (the area sources: margins, welds, born; erosion's loss) and put it
in km.

- [ ] split the per-process area and volume budgets (km2 and km3, not km x cells) L6 vs L7 on two seeds
- [ ] the process whose rate per km of coast/trench differs by level: make it level-consistent

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: second-order tectonics refinement; the planet is stable without it
- 2026-10-28: Lane 23 (PW-970): one level-dependent area source found and fixed. Coherence welds re-filled gaps that only the world grid's nearest-cell sampling showed at coastlines, and that wrote continental crust into the plate's ocean cell: a ratchet that runs with coastline length in cells. Welds now need the inlet on the plate's own grid (a607c614). The volume thermostat's shortfall remains (draft-crust-volume-thermostat-shortfall).
- 2026-10-24: Created from inbox draft draft-crust-thermostats-level-dependent.md (found by v1-finish-5).
