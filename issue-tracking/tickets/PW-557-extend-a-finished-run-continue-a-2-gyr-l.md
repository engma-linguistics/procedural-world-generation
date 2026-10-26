---
id: PW-557
title: "Extend a finished run: continue a 2 Gyr L6/L7 run to 4 Gyr from its last checkpoint"
type: task
status: todo
parent: null
milestone: v3
subsystem: tectonics
effort: m
impact: med
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-21
updated: 2026-10-26
---

## Description
Owner 2026-10-21 (for fun, a v2 experiment): pick a long-running L6 or L7 run as a seed for further work, and continue it from where it ended, e.g. 2 Gyr + 2 Gyr = 4 Gyr, to see whether the coupled systems hold up or the planet falls apart. 'planet simulate' has checkpoints (--checkpoint-every; replays start from the nearest one) but no option to extend a finished run past its end. Needs: an extend/continue command that restarts from the final state, keeps the same RNG streams and keeps the run deterministic (A then +B should match a single A+B run, or say why not), and records the extension in the run's metadata. Then the experiment: one L6 and one L7 run taken to 4 Gyr, with the health tool and the stage-0 ice diagnostics (PW-555) over the whole span. Watch sea level (PW-549), plate count, crust volume, mantle heat and the climate's long-term trend, including stellar brightening if it's modelled.

## Updates
- 2026-10-26: Milestone v2 -> v3: other planet kind. (PW-900 backlog reorg).
- 2026-10-21: Created.
