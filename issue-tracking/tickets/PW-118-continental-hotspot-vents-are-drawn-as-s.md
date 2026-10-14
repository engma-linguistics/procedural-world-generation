---
id: PW-118
title: Continental hotspot vents are drawn as shields; they should be calderas on a lava plain
type: task
status: todo
parent: PW-001
subsystem: zoom
effort: s
impact: low
found_by: volcanoes
blocked_by: []
relates: [PW-004, PW-010]
refs: [planet/zoom_volcanoes.py, planet/tectonics/volcanism.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
A plume under a continent also leaves a chain of vents (every ~100-150 km: continental plates are
stiff), each up to ~3 km of relief, and the zoom draws them like ocean islands: Gaussian shields.
Continental hotspot tracks look different: a broad basalt plain (the Snake River Plain) with large
calderas (Yellowstone's ~70 km), rhyolite domes and only modest cones. Draw continental vents
(`floor_m > 0`, or the coarse crust) as a caldera ring with a low resurgent dome on a flat lava plain,
and lower their height limit in the run (`volcanism.new_vent`, hmax ~3 km now).

## Updates
- 2026-10-14: Created from inbox draft draft-continental-hotspot-calderas.md (found by volcanoes).
