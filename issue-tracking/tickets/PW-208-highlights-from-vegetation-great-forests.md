---
id: PW-208
title: "Highlights from vegetation: great forests, savannas, wetlands, Mediterranean coasts, the treeline"
type: task
status: todo
parent: null
subsystem: highlights
effort: s
impact: low
found_by: veg
blocked_by: []
relates: [PW-187]
refs: [planet/highlights.py, planet/vegetation.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
highlights.py still reads `biome` (now a coarse grouping of the vegetation's named types) for its rainforest, desert and diversity detectors. Worlds now carry `vegetation` (60 named types), `tree_cover`, `npp`, `fire_return`, `flooded`: candidates for new detectors such as the largest closed forest, the great savanna, wetlands like the Sudd or Pantanal (named types 11, 50-54), the larch taiga, Mediterranean coasts with maquis, and a "most varied vegetation" square (Shannon diversity of named types instead of biomes).

## Updates
- 2026-10-15: Created from inbox draft draft-veg-highlights.md (found by veg).
