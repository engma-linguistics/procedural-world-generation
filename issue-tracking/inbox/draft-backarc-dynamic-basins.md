---
title: Basins from back-arc extension, pull-aparts and dynamic topography are still missing
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: low
found_by: tect2
blocked_by: []
relates: [PW-054]
refs: [planet/tectonics/isostasy.py, planet/tectonics/mantle.py]
---

## Description
PW-054 (tect2) brought closed basins back with flexural moats beside
mountain belts and thermal sag after rifting (`isostasy.subsidence`). Two
other families of Earth's subsiding basins are not modelled:
- back-arc and pull-apart basins (Pannonian, Aegean, Dead Sea, Great Basin's
  extension): the model only stretches at diverging plate boundaries; an
  overriding plate behind a retreating trench, or a transform's bend,
  doesn't extend.
- dynamic topography: the mantle field (`sim.mantle`, ~+-1) doesn't move
  the surface. Earth's continents ride +-0.3-1 km on it: Africa's superswell,
  sags over cold downwellings (Congo, Eyre, the Cretaceous interior seaway).
  A term like `dyn_topo` x anomaly (~400 m per unit) in `isostasy.subsidence`
  would also tilt continents and flood assembling supercontinents; it moves
  land share (continents sit on warm mantle), so it needs a recalibration of
  `continental_thickness` with it.
Only worth it if closed-basin share or basin variety looks short after PW-054.
