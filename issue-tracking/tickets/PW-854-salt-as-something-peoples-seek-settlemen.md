---
id: PW-854
title: "Salt as something peoples seek: settlement-level salt works and mining colonies (dwarves predisposed), not a salt-dwarf subgroup"
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Owner: salt miners should not be their own subspecies/group; people find and care about salt, dwarves' mining bent may mean colonies doing it; fine to defer to civs. Relates PW-797, PW-804.

## Updates
- 2026-10-25: Created.
- 2026-10-25: fun lane 26. The `salt_dwarf` group and its strict `[[use]]` row are gone from dnd.toml. Salt is now settlement-level (mining.py, salt_reach.py, brief._salt_works): any settled people works the rock-salt beds in its country as salt works (traded WORKS_CAP = 1.25x further than unworked beds); a miner people (dwarves, the `miner` trait) works the beds in its own country as mines and sends colonies to beds held by other peoples within COLONY_KM = 300 km of its country (MINED_CAP = 1.6x). The brief's mining section gains `salt_works` (mines/colonies/works shares of land). Brief version 9. Test: test_salt_is_sought_by_settlements_not_by_a_salt_dwarf_group. Not done: colonies are read in the brief, not placed by the simulation (no ranges moved); see draft salt-colonies-in-the-sim.
