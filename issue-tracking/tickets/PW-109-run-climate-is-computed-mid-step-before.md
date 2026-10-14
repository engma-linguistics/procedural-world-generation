---
id: PW-109
title: Run climate is computed mid-step, before events reshape the ground
type: task
status: done
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: coordinator
blocked_by: []
relates: []
refs: ["run:428083@1000Myr(0.62,-41.32)", planet/tectonics/simulation.py, planet/tectonics/earth.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Simulation.step runs _physics (which calls earth.update_climate when climate_due) before events.sutures / absorb_slivers / maybe_rift. Cells those events change keep a climate for ground that no longer exists: run 428083 t=1000 cell 33867 (0.62,-41.32) shows 27 C at 1229 m, cell 4495 (8.03,-41.31) 26 C at 5358 m. Lag is <= one step (2 Myr) and mostly visible because of the churn ticket filed alongside; fix by computing the climate after events, or at keyframe output.

## Updates
- 2026-10-14: Status todo -> done. Climate now computed at the end of Simulation.step, after events (first step still mid-step so erosion has a climate); w_elev follows the ice-driven sea shift. Test test_climate_fits_ground_after_events fails on old code, passes now. No rng draws moved.
- 2026-10-14: Created.
