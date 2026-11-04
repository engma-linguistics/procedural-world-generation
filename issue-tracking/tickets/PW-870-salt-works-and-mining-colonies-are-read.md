---
id: PW-870
title: Salt works and mining colonies are read in the brief, not placed by the simulation
type: task
status: todo
parent: PW-692
milestone: later
subsystem: food
effort: m
impact: low
found_by: fun-lane-26
blocked_by: []
relates: [PW-854, PW-797, PW-804]
refs: [planet/lineages/mining.py, planet/lineages/salt_reach.py, planet/lineages/brief.py]
created: 2026-10-25
updated: 2026-11-03
---

## Description
PW-854 removed the salt-dwarf group and made salt a settlement-level behaviour in the brief: any settled people works the rock-salt beds in its country (salt works), a miner people (dwarves) works the beds in its own country as mines and sends colonies to beds held by others within 300 km (`mining.colony_cells`). That is derived from the final ranges: nothing in `History.run` moves a people toward salt any more (the strict `[[use]]` row went with the group), so the dwarves are not drawn to the beds, and a colony does not exist as a place with a founding date.
Options: (A) a plain `[[use]] by = "dwarf" good = "salt_rock"` pull (a weak, non-strict one) so the dwarves' habitat leans to the beds; (B) a dated colony event when a miner people's range first comes within COLONY_KM of beds held by another people (like the crossings events); (C) leave it to the civs pass (the owner said fine to defer to civs). Lean A now (one line), B with the civs.
- [ ] dwarves' habitat leans toward rock-salt beds without a subgroup

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: resources/ore layer or salt-mining detail; not needed for the first culinary brief
- 2026-10-25: Created from inbox draft draft-salt-colonies-in-the-sim.md (found by fun-lane-26).
