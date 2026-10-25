---
id: PW-853
title: Name the continents (at least), stored with the world and shown in the viewer
type: task
status: done
parent: null
milestone: v2
subsystem: store
effort: s
impact: med
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Owner: needs names for convenience, e.g. Jangwa, a vaguely Africa-like continent from a previous campaign the owner keeps.

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 26 (80c1df3).
- 2026-10-25: Created.
- 2026-10-25: fun lane 26. `planet/names.py` generates pronounceable names from (world seed, rank by area); `world.landmasses(seed=)` stores them as `name` (with `letter` A, B, ...) in the world summary (new worlds only; old worlds such as 2a7385 keep letters in their stored summary) and the viewer's landmass lines show them; the peoples' history (`Pass.world_seed` -> `Crossings.names`, field `called`) uses the same function, so crossings and discoveries read 'the continent of <name>' for any world, old or new. Not done: names drawn on the map itself, and an owner-given name (e.g. Jangwa) override. Test: test_landmasses_are_named_from_the_worlds_seed_and_rank.
