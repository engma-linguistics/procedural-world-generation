---
id: PW-1200
title: "World export targets: Minecraft, Dwarf Fortress, Valheim and engine presets (grows PW-475 into an epic)"
type: epic
status: todo
parent: null
milestone: later
subsystem: store
effort: xl
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-475, PW-100, PW-099, PW-206]
refs: [planet/export.py]
created: 2026-10-31
updated: 2026-11-03
---

## Description
**In plain words.** The owner (2026-10-31) wants exports to interesting game targets. None has to work; each is an experiment that shows what the world carries. Built on `planet export` (PW-100) and the engine presets of PW-475 (Unity/Unreal/Godot heightmaps).
- [ ] Minecraft: a region of a zoom as a Java world (Anvil region files): height, water, biome ids mapped from ours, ores from the resource layers, at 1 block = some metres; size limits stated.
- [ ] Dwarf Fortress: a world-gen parameter set / map import (elevation, rainfall, temperature, drainage, volcanism, savagery) from a finished world; check what DF's import accepts.
- [ ] Valheim: check whether its world format or mods accept a heightmap and biome map; if not, record why.
- [ ] PW-475 presets for Unity/Unreal/Godot stay the first, cheapest target.
Later (owner: "v4"): a walkable city-sized setting (Unity or web), which needs large asset work (trees, buildings); recorded as its own ticket.

## Updates
- 2026-11-03: Milestones 11-03: v3 -> later: v3 is now states and war v0; this waits for after v1.0
- 2026-10-31: Created from inbox draft draft-world-export-targets-epic.md (found by coordinator).
