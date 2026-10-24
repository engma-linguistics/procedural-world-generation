---
id: PW-777
title: Marine habitat K is only water temperature and a depth band; use sst, upwelling, kelp, reef and tide range, and let the coast realm hold the land end
type: task
status: todo
parent: PW-729
milestone: v2
subsystem: timezoom
effort: m
impact: low
found_by: fun17
blocked_by: []
relates: [PW-729, PW-775]
refs: [planet/lineages/history.py, planet/lineages/seafood.py, planet/coastal.py, planet/lineages/samples/seven_meals.toml]
created: 2026-10-24
updated: 2026-10-24
---

## Description
`history.marine_capacity` (PW-775) is deliberately small: K from `env["temperature"]` at sea within the line's `temp_c`, and the depth
band `elev_m` (negative metres). Known limits, each a data or small-code step if the owner wants more:
- The **coast realm is the sea ring only** (`tags["shore"]`: sea cells next to land). The land end of the interface (beaches, tidal flats on
  land cells) is left to the land peoples, so land peoples' ranges and the land-facing layers are exactly unchanged by a marine line;
  a coast people's cells never include a land cell. At L7 a cell is ~55 km, so "tidal" is the ring, not the flat; `elev_m` is the mean
  depth of a coarse cell (shore ring median ~1100 m at L7), so merfolk use `[-600, 0]` to mean "the shallower half".
- **Water, not air, temperature**: `env["temperature"]` at sea is what the lineages env has; ocean.py's surface temperature, upwelling,
  and the world's kelp/reef/seagrass layers (coastal.py) are in the brief's `sea_peoples.goods` only, they do not shape the range.
- The sea realm **cannot cross land** (a walker on the sea graph; no portage or river travel), has no boats, animal or crop knowledge,
  no long-crossing hops, no minimum-viable-population fade, and competes with closed-country exclusion (contact value 0 at sea).
- The `storm_coast` [[use]] rows for the storm giants were dropped (a land good); wave power could pull them instead.
- Cost: not measured separately (the sea realm adds the ocean cells to the spread passes of the sea lines only); see PW-775's
  measured cost note.

## Updates
- 2026-10-24: Created from inbox draft draft-marine-habitat-fidelity.md (found by fun17).
