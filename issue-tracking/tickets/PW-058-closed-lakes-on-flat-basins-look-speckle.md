---
id: PW-058
title: Closed lakes on flat basins look speckled on the run globe
type: task
status: done
parent: null
subsystem: hydrology
effort: s
impact: low
found_by: lakes
blocked_by: []
relates: []
refs: [planet/hydrology.py, "run 8dc2f2"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
On the run globe, closed lakes on flat basins show as scattered single cells rather than one lake
(demo run 8dc2f2, elevation layer, t≈180–360).

## Updates
- 2026-10-14: Status todo -> done. Fixed in the model (hydrofix): the 20 m MIN_DEPTH fill was a per-cell test against the basin's final spill, so on a flat rough floor cells deeper than 20 m stayed as separate pits, shallower ones were raised to the spill, and few-m dips stayed separate sub-basins with their own water budgets. kernels.fill_shallow now fills per basin at every saddle (all but the deepest basin meeting there, if < 20 m below it). Same terrain, 3 runs x 5 checkpoints: closed lakes 81 pieces for 338 cells -> 90 for 927; seed-13 L6 600 Myr (a61cd5 -> 28e6be) closed 5.2 -> 14.3 cells per piece. Pictures: docs/review/lakes/pw058_*.png. Lake area grew ~1.8x: see the inbox draft on lake area.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world.
