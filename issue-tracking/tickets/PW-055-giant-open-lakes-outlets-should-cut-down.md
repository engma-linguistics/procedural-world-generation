---
id: PW-055
title: "Giant open lakes: outlets should cut down and drain them"
type: task
status: todo
parent: null
subsystem: hydrology
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-021]
refs: [planet/hydrology.py, planet/surface.py, "run 8dc2f2"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Open lakes stay at their spill level forever because outlets don't incise. Runs show giant shallow lakes
up to ~2.3 million km² (larger than any open lake on Earth: Superior is 82,000 km²; only the closed
Caspian is bigger). Add outlet incision so lakes drain down over time, scaled by discharge and rock.
Also the v1 note "lakes are too many and too large". Morning decision 2 option C (more coarse-scale river
erosion so big rivers grade down) belongs here too.

## Updates
- 2026-10-15: Status in-progress -> todo. Hydro (merged): outlets cut valleys (0.1 x Q^0.7 m), lakes re-solved; giant-lake frames 13->3 at L7 seed 3199. Left: lakes in continually subsiding basins.
- 2026-10-15: Status todo -> in-progress. Foundation round, worktree hydro.
- 2026-10-14: Migrated. Merged: Backlog 'Giant open lakes' (owner), 'Giant shallow lakes in runs' (lakes), v1 Also noted 'Lakes are too many and too large'.
