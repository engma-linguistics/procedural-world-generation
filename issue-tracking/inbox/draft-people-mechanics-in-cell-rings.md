---
title: "People mechanics still count cells and rings (raids, barter, reach, deme sizes), so L8/L9 refined worlds will play differently"
type: task
status: todo
parent: null
milestone: v5
subsystem: peoples
effort: m
impact: med
found_by: scout-242
blocked_by: []
relates: [PW-820]
refs: [planet/lineages/ladder.py::RAID_REACH, planet/lineages/ladder.py::BARTER_REACH, planet/lineages/compose.py::REACH_CELLS, planet/lineages/demes.py::MIN_CELLS, planet/lineages/demes.py::ADAPT_MIN_CELLS, planet/lineages/animals.py::OVERLAP_MIN, planet/lineages/history/params.py::CHAIN_CELLS, planet/language/inputs.py::RIVER_FLOW, planet/lineages/seafood.py::rings_for, docs/review/pw820-water-units/README.md]
---

## In plain words
PW-820 moved the food-water rules to km, km2 and m3/s. Several people rules still count grid cells: how far a den people
raids (2 rings), how far foragers barter (1 ring), how far a people's presence reaches (10 cells, ~560 km at L7), how
big a cut-off piece must be to become its own deme (40 cells, 125,000 km2 at L7). On an L8/L9 refined world those
distances shrink by 2-4x and the areas by 4-16x, so the same world's peoples raid, trade and split differently.

## Description
- Convert each to km or km2 at its L7 value, using seafood.rings_for (whole rings, at least one) and
  seafood.cell_km2, as PW-820 did; keep L7 identical.
- planet/language/inputs.py RIVER_FLOW = 50 is commented "m^3/s as stored", but the world `flow` layer is cells x m/yr
  (hydrology.discharge): 50 units is ~4,900 m3/s at L7 and ~1,230 m3/s at L8. Use discharge() and restate the floor.
- [ ] each constant in km/km2 with its L7 equivalent; a test that rings_for gives the old ring count at L7
- [ ] a peoples run on an L8 refine reads raids/barter/deme splits on the same physical scale as L7

If never done: the December refine (v5) gives peoples on L8/L9 worlds shorter raids, smaller trade circles and more
deme splits than the same planet at L7, and the language river list changes with level.
