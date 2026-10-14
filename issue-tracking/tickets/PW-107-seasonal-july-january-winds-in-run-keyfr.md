---
id: PW-107
title: Seasonal (July / January) winds in run keyframes
type: task
status: todo
parent: null
subsystem: store
effort: s
impact: low
found_by: quickwins
blocked_by: []
relates: [PW-044]
refs: [planet/tectonics/simulation.py, planet/tectonics/output.py, planet/tectonics/earth.py, planet/timeline.py, planet/store.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-044 gave worlds `wind_jul_e/n` and `wind_jan_e/n` (world.finish) and the viewer a Winds season picker
(year / July / January, `?season=jul`). Run keyframes still store only the annual-mean `wind_e/n`, so on a
run the picker is hidden and the overlay shows the yearly mean.

To add them: keep the two half-year winds on the simulation (`sim.wind` is set as their mean in
`tectonics/earth.py` and the climate step; the snapshot in `tectonics/output.py` copies `sim.wind`), add them
to the snapshot, to `timeline.RUN_LAYERS` and `timeline.frame_values` (via `vec_layers`, names `wind_jul`,
`wind_jan`). The store specs (`store.LAYERS`, int8, scale 0.02) and the viewer (`OVERLAY_NEEDS.winds`,
`windKey()`) already handle them. Costs 4 more int8 layers per keyframe (~160 kB per frame at L6) and a
new run to see them. Deferred because it touches the simulation state and snapshot, which the volcanism
work was changing at the same time.
- [ ] new L6 run shows the season picker on the timeline, and July/January winds differ over the monsoon coasts

## Updates
- 2026-10-14: Created from inbox draft draft-seasonal-winds-in-run-frames.md (found by quickwins).
