---
id: PW-1626
title: "Language river list: RIVER_MIN_CELLS still counts cells, so an L8 refine names more, shorter rivers"
type: task
status: todo
parent: null
milestone: v5
subsystem: culture
effort: xs
impact: low
found_by: lane266-pw1584
blocked_by: []
relates: [PW-1584, PW-820]
refs: ["planet/language/inputs.py::RIVER_MIN_CELLS", "planet/language/inputs.py::RIVER_FLOW", "planet/hydrology.py::discharge", "planet/lineages/seafood.py::rings_for"]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
The language pass picks the rivers a people names. Its flow floor is already in m3/s (RIVER_FLOW = 4,900, commit e4661a71),
but a river still has to be at least 3 grid cells long (RIVER_MIN_CELLS = 3). At L7 that is about 180 km of river; on a
world refined to L8 it is about 90 km, so the same planet's languages name more, shorter rivers.

## Description
Lane 266 (PW-1584) moved the peoples' cell and ring counts to km and km2 but left planet/language/ alone (the language lane
owns it). What is left there:
- `RIVER_MIN_CELLS = 3` (inputs.py ~line 34, used ~line 954 as a count of river cells per basin). Restate as a river length
  in km at its L7 value (3 x 60.16 km, about 180 km), turned into cells with `seafood.rings_for(g, km)` style rounding
  (`max(1, round(km / (g.spacing * R_KM)))`), so L7 keeps exactly 3 and L8 gets 6.
- `RIVER_FLOW` itself needs no change for the level: it goes through `hydrology.discharge`, which turns flow units
  (cells x m/yr) into m3/s with the grid's mean cell area. Lane 263 is switching `discharge` to each cell's true area;
  after that merges, check the river count on one L7 world against today's (same world, current code) before
  re-stating the floor.
- [ ] RIVER_MIN_CELLS in km, L7 count unchanged (a test like tests/test_people_units.py)

If never done: on the December L8 refine, each people's river vocabulary counts streams 90-180 km long that the same planet
at L7 leaves out.

## Updates
- 2026-11-10: Created from inbox draft draft-language-river-min-cells-in-km.md (found by lane266-pw1584).
