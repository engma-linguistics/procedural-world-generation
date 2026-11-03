---
id: PW-797
title: "Salt-miner dwarves: where rock salt (evaporite beds) sits in a dwarf range, some dwarf cultures mine salt (alone or with ore), like Hallstatt and Wieliczka"
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: food
effort: s
impact: med
found_by: owner
blocked_by: []
relates: [PW-796]
refs: []
created: 2026-10-24
updated: 2026-10-24
---

## Description
Owner 2026-10-24: real rock-salt mines (Hallstatt ~7000 yr, Wieliczka, Khewra) are substantial enough that an occasional dwarf culture could be salt miners rather than ore miners, or both if useful deposits sit nearby. Light: a data-driven group/[[use]] row reading evaporite deposits; salt as a trade good feeds salt reach (PW-796). Mineral licks stay a human salt source (precedent: Big Bone Lick and other lick springs boiled for salt).

## Updates
- 2026-10-24: Created.
- 2026-10-24: fun-lane-23 v0 on branch worktree-agent-a99c39742fd313a6b: land good `salt_rock`; `planet/lineages/mining.py` reads each miner-trait people's cells (salt, ore, salt and ore; nothing authored per people); brief v8 `mining` section, suggested note and salt-reach `from_mines_share` (mined salt trades 1.6x further, `salt_reach.MINED_CAP`); dnd sample gains a `salt_dwarf` group (strict pull on `salt_rock`). Run b36648: dwarves are salt-and-ore miners and 9% of the region's land gets salt only through their mines. On world 6fbc2c the salt_dwarf group did not reach the beds (drafts salt-dwarves-reach-the-beds, salt-mine-goods-in-fuels-and-trade). Tests: test_salt_miners_happen_where_the_beds_are_and_not_where_they_are_not, test_salt_dwarves_hold_the_beds_in_the_sample_tree; full suite 677 passed.
