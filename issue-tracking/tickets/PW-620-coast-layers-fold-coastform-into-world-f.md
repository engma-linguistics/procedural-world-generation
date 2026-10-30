---
id: PW-620
title: "Coast layers: fold coastform into world.finish, or keep them an add-on (planet coast)?"
type: task
status: done
parent: PW-097
milestone: v2
subsystem: coast
effort: xs
impact: med
found_by: coast-detail
blocked_by: []
relates: [PW-097, PW-155]
refs: [planet/coastform.py, planet/world.py, docs/proposals/coast_detail.md]
created: 2026-10-23
updated: 2026-10-29
---

## Description
The coast-form layers (coast_type, barrier, cliff, seabirds, seals, nav_hazard; planet/coastform.py) are made
by an add-on, `planet coast <world>`, like the resource layers, so no existing world output changes. New
worlds therefore lack them until someone runs the command.
- A: call `coastform.world_layers` at the end of `world.finish` (after humanuse): every world has them,
  ~1 s per L6 world; adds layers to every world file (no existing layer changes).
- B: keep the add-on; `planet make` / the one-command flow runs it.
- C: leave as is.
Lean: A, once the owner has looked at the classes in the viewer (docs/review/coast_detail/).

## Updates
- 2026-10-29: Removed docs/review/coast_detail/ in cleanup; last present at 9861e2df.
- 2026-10-23: Status todo -> done. fun5: A built. world.finish makes the coast-form layers for every world (0.1 s at L7); planet coast redoes them.
- 2026-10-23: Status needs-decision -> todo. Owner (2026-10-24): A: coast-form layers at the end of world.finish.
- 2026-10-23: Created from inbox draft draft-coast-layers-in-finish.md (found by coast-detail).
