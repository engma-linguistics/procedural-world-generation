---
id: PW-1287
title: Drowned continental crust floats as if in air, so a shelf's sediment lifts it less than the same sediment lifts the ocean floor
type: task
status: needs-decision
parent: null
milestone: null
subsystem: tectonics
effort: m
impact: low
found_by: lane-100e
blocked_by: []
relates: [PW-950, PW-980]
refs: [planet/tectonics/isostasy.py, planet/tectonics/earth.py, tests/test_sea_level.py]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: the model works out how high the continents stand as if air sat on top of them, even where the
sea covers them (shelves, drowned margins). Under water a column floats higher per km of light rock, because the
water above weighs part of what it displaces. The ocean floor already uses the under-water rule. So 1 km of sediment
moved from a drowned shelf onto the ocean floor raises the floor more than it lowers the shelf. The sea then rises a
little even though no water was added. Lane 100e's sea-level test shows this: the net is the isostatic difference
(`tests/test_sea_level.py::test_sediment_moved_off_a_shelf_onto_the_ocean_floor_keeps_the_sea`).

Where: `isostasy.elevation` (continental: `250 + ISO_LAND x (thick - CONT_KM)`, `_k` K_LAND for cont) and
`sediment_lift` (K_LAND for continental cells, K_SEA for oceanic cells).

Options:
- A. Drowned continental cells use the under-water response below sea level (as `ISO_SEA` / `K_SEA` do), with a
  smooth join at the shore. It's correct, but it raises the drowned margins, so it moves the
  margin bands (PW-950) and the land. That means a paired judge.
- B. Leave it. It's a second-order bookkeeping gap, and the sea-level fix already conserves the ocean's water to
  within it.
Lean: B for v1, A when the margins are next revisited.
- [ ] decision A or B

## Updates
- 2026-11-01: Created from inbox draft draft-drowned-continental-crust-floats-as-in-air.md (found by lane-100e).
