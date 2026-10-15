---
id: PW-154
title: Overturning schematic - deep limbs missing or roundabout on some worlds
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: viewerocean
blocked_by: []
relates: [PW-137]
refs: [planet/ocean.py, "world 2085dc"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
ocean.loop_schematic draws the deep return flow as the cheapest route through sea
deeper than 1500 m, preferring western boundaries (a step costs 1 + km to land due
west / 500), to a circumpolar channel (equatorward of 70 deg) in the other hemisphere
or else the equatorial band. On Earth (world dc3732) this reads well (NADW down the
American slope to the Southern Ocean, AABW from the Ross and Weddell seas). On the
demo world 2085dc (run f59dd6 @ 1000 Myr):
- the 13.3 Sv southern site (74 S, 27 E) has no deep limb: the nearest deep sea that
  leads to the tropics is > 20 deg away (LOOP_GAP_DEG), so only the rings and the surface
  inflow show;
- the 14.1 Sv northern site's deep limb goes west round the polar sea and down the far
  side of the planet rather than south through its own basin.
Options: start the deep route from the site through shallower sea (e.g. 500 m) for its
first few hundred km (overflows), and weigh distance more against the western-boundary
preference. It is a schematic, so this is cosmetic.

## Updates
- 2026-10-14: Created from inbox draft draft-overturning-schematic-gaps.md (found by viewerocean).
