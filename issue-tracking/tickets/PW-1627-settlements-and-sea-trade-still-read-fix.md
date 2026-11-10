---
id: PW-1627
title: Settlements and sea trade still read fixed rings (town footprints, pits, mine exposure, coastal boat reach), so they shrink on L8
type: task
status: todo
parent: null
milestone: v5
subsystem: peoples
effort: m
impact: med
found_by: lane266-pw1584
blocked_by: []
relates: [PW-1584, PW-1265, PW-820]
refs: ["planet/lineages/settlements.py::_ring_index", "planet/lineages/settlements.py::PIT_RINGS", "planet/lineages/settlements.py::MINE_EXPOSE_STEPS", planet/lineages/trade_flow.py, "planet/lineages/seafood.py::_sea_to_coast", planet/lineages/history/tags.py, planet/lineages/history/dispersal.py]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
PW-1584 (lane 266) moved the main people rules from cell counts to km and km2 (raids, barter, presence reach, deme sizes,
tamers' overlap, island chains, hemmed-in seats, subject cultures, market pools). A second layer of fixed ring counts is
left, mostly in the settled history that the split pipeline will run on L8: on an L8 world these reach half as far.

## Description
Found by grepping planet/lineages for ring loops and cell-count constants (lane 266 report has the full list):
- settlements.py: the place's footprint `_rings(g, cell, {1: 0, 2: 1, 3: 2}[tier])` (a city reads its cell and two rings,
  ~120 km at L7, ~60 km at L8); `R1, R2 = _ring_index(g, 1), _ring_index(g, 2)`; `PIT_RINGS = 1` (one pit per cell and its
  ring); `MINE_EXPOSE_STEPS` "a mine within two rings".
- polities.py `HEMMED_RINGS = 2` and the live history's own two-ring table (history/polity_live.py `r2a/r2b`, also used for
  the sediment sums near lines 223 and 366): a test (test_a_live_state_seat_is_hemmed_in_over_its_own_two_rings) holds the two
  equal, so they move to km together (lane 266 tried HEMMED alone and the coarse test grid split them).
- trade_flow.py ~line 602: the coastal boat tier spreads `for _ in range(2)` rings along the coast.
- seafood.py: salinity, ice coast and the kelp/seal/reef goods read the sea `_sea_to_coast(..., 1)` one ring off the coast
  (adjacency: probably right as is, check).
- history/tags.py: an island is a landmass under `max(3, 0.004 x land)` cells (the 3 matters only on coarse grids).
- history/dispersal.py: a front advances a ring of cells per hop (HOP_EVERY_KYR), so the deep history's spread speed in km
  per kyr halves on L8. Not a problem while the deep history stays on L7 (the agreed split), but it is if the whole history
  is ever run on a refined grid.
- [x] each in km with rings_for / cells_for, L7 counts unchanged (extend tests/test_people_units.py)

If never done: on the December L8 refine, towns and cities read half the country around them, pits are four times as dense
and coastal boats reach half as far as on the same planet at L7, so the settled map changes with the grid, not the world.

## Updates
- 2026-11-10: Lane 270 (5bd8e407): every ring on the list in km (settlements TOWN_KM/CITY_KM/PIT_KM, trade_flow COAST_BOAT_KM, polities HEMMED_KM with the live history's ring table, tags ISLAND_FLOOR_KM2), L7 counts unchanged (tests/test_people_units.py, goldens pass). seafood's one-ring sea reads left as adjacency; dispersal's hop left (deep history stays on L7; lane 269c owns that file). Split rerun: cities 119 -> 244 (L7 same code 283), the ledger's rings carrying it (split.md §6). Done for the conversions; the coast remainder is PW-1630.
- 2026-11-10: Evidence from the first split run is PW-1630 (coast 7.0% -> 1.9%, cities to a third, islands lose towns on L8); take both together.
- 2026-11-10: Created from inbox draft draft-settled-window-grid-rings.md (found by lane266-pw1584).
