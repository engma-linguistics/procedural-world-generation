---
title: "PW-915: measure the finish window's drift with the step-length thresholds at the 2 Myr step"
type: task
status: todo
parent: null
milestone: v1
subsystem: tectonics
effort: s
impact: low
found_by: v1-finish-17
blocked_by: []
relates: [PW-915, PW-866]
refs: [planet/tectonics/crust.py, planet/tectonics/volcanism.py]
---

## Description
v1-finish-17 changed arc_rock, the hotspot rock tag and the arc-volcano candidates to compare growth/plume rates at
the run's step (sim.dt) instead of the step's own length (dt_now), so the finish window's 0.5 Myr steps no longer
raise the bar 4x. Measured neutral on the pass rate (set A vs A + PW-915, L6 18 + L7 8 draws: same per-draw
results within ~1 C). Not measured: the drift it was meant to remove, i.e. how many ARC/HOTSPOT cells and arc
volcanoes appear per Myr in the finish window against the steps before it.
- [ ] count new ARC / HOTSPOT rock cells and new arc volcanoes per Myr in the last 10 Myr vs the 10 Myr before, on 2-3 L6 runs, with and without PW-915
