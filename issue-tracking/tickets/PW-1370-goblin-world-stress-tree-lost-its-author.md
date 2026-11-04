---
id: PW-1370
title: "goblin_world stress tree lost its authored densities (goblins 6, bugbears 1.5, grimlocks 2, humans 5): re-express or drop"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: xs
impact: low
found_by: lane 136 / lane 137 (density ladder build)
blocked_by: []
relates: [PW-1275]
refs: [tools/peoples_robust/trees/goblin_world.toml, tools/peoples_robust.py, "planet/lineages/spec.py::KIND_RANGE", "planet/lineages/ladder.py::is_den", docs/review/peoples/density-ladder/build.md]
created: 2026-11-02
updated: 2026-11-03
---

## Description
The authored stress tree `tools/peoples_robust/trees/goblin_world.toml` set goblins 6, bugbears 1.5, grimlocks 2 and humans 5 people
per km2: a world where goblins are the dense ones. Per-people density is gone with the ladder (PW-1275; `density` now raises at
parse), so lane 136 removed those lines and the tree runs at the kind defaults (goblins 1.2 from the dnd preset, the rest 1). The tree
no longer tests what it was written for.

Options: (A) re-express it as kind factors at the range ends (goblins 2, humans 0.5) and give its goblins a farming way, so the stress
is "goblins out-farm humans"; (B) drop the tree. Lean A, small.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-11-02: Created from inbox draft draft-goblin-world-densities.md (found by lane 136 / lane 137 (density ladder build)).
