---
id: PW-045
title: Sliced worlds don't store wind, current or jet layers
type: task
status: done
parent: null
subsystem: store
effort: s
impact: med
found_by: overview
blocked_by: []
relates: []
refs: [planet/world.py, planet/store.py, "world 7c5adf"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Only runs and the Earth world store `wind_e/n`, `current_e/n` and `jet_e/n`, so those overlays never
appear on generated (sliced) worlds, e.g. 7c5adf. Add them to the world layers in `world.py`/`store.py`.

## Updates
- 2026-10-14: Status in-progress -> done. world.finish now stores wind_e/n, current_e/n (0 on land) and jet_e/n (annual means of the July/January fields, via timeline.vec_layers) for every world, sliced or generated; tools/earth_world.py drops its second climate pass that used to add them. Store specs already existed. Verified: sliced 01b0f7 --at auto -> world 7d17a4 (384 Myr) has the layers, and a headless-Chrome screenshot shows the wind and current overlays on it. Older worlds (e.g. 7c5adf) still lack them until re-sliced. Tests pass; goldens unchanged.
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world (found by the overview agent; confirmed: 7c5adf has no wind layers).
