---
id: PW-804
title: Salt dwarves rarely reach rock-salt beds because evaporites lie in deserts the dwarves do not hold
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: food
effort: s
impact: low
found_by: fun-lane-23
blocked_by: []
relates: [PW-797, PW-796]
refs: [planet/lineages/mining.py, planet/lineages/samples/dnd.toml, "run d22731 (deleted), world 6fbc2c"]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-797 first pass: salt mining is read from the land, so any people with the `miner` trait that leads rock-salt country
(good `salt_rock`) is a salt (or salt-and-ore) miner. It happens occasionally, as asked: over 10 existing runs the dwarves
work 0 to 154 bed cells (run b36648: dwarves are salt-and-ore miners, 9% of the region's land gets salt only through their mines).
The `salt_dwarf` group in the dnd sample (strict pull 0.8 on `salt_rock`, rain floor 100 mm) did NOT reach the beds on
world 6fbc2c: groups are born inside the parent people's range, the beds of that world lie in deserts held by the
dragonborn, and the dwarves hold only 1 bed cell, so salt dwarves ended as ore miners.
Options: (A) leave it, since an occasional salt-dwarf culture is the owner's wish; (B) let a group seed on a nearby bed when its
people's range touches the ring around one; (C) make the group a standalone line with its own origin in bedded mountain foothills.
Lean: A until a showcase world needs one, then B.
- [ ] a showcase run where a salt-dwarf group leads at least one bed district

## Updates
- 2026-10-24: Placed under PW-692.
- 2026-10-24: Created from inbox draft draft-salt-dwarves-reach-the-beds.md (found by fun-lane-23).
