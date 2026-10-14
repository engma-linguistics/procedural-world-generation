---
id: PW-116
title: Arc chains are still blocky arc-crust islands with a few cones; real arcs have a volcano every ~50-70 km
type: task
status: todo
parent: PW-001
subsystem: zoom
effort: m
impact: med
found_by: volcanoes
blocked_by: []
relates: [PW-004]
refs: [planet/tectonics/volcanism.py, planet/zoom_volcanoes.py, planet/tectonics/params.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Arc volcanoes are now objects like hotspot vents (one per `volcano_spacing` = 120 km of active arc,
`volcano_km3` = 2000 km³ each, active ~8 Myr, then eroding), and the zoom draws each as a steep
stratocone with a crater. On the "Indonesia-like" check (an arc on a flooded shelf at 17°N, -19°E in a
seed-13 level-7 test run, since deleted; any active arc on a shelf shows it, e.g. world a099c6, run
39d004) the shelf gets a scatter of small volcanic islands, but the
arc itself is mostly the coarse arc crust: two or three big blocky islands with only ~15 cones on them,
and a cone is ~3 px across at 2 km pixels. Real arcs (Java, Sumatra, the Aleutians) have a volcano every
~50-70 km in a line along the arc, which is what makes them read as volcanic chains.

What to try:
- [ ] Lower `volcano_spacing` to ~70 km (with `volcano_km3` lowered to keep the arc crust per km of arc;
      the thermostat on arc growth absorbs the rest), or
- [ ] In the zoom, add minor cones between the listed volcanoes along the active arc's trend
      (plate_boundary converging cells), sized from the neighbours.
- [ ] Re-check the shelf case: a line of volcanic islands and peaks along the arc, not blocks.

## Updates
- 2026-10-14: Created from inbox draft draft-arc-volcano-density.md (found by volcanoes).
