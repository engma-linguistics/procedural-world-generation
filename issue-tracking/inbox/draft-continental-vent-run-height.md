---
title: "Continental hotspot vents: the run's height limit (zoom side of PW-118 done)"
type: task
status: todo
parent: PW-001
subsystem: tectonics
effort: xs
impact: low
found_by: zoom-polish
blocked_by: []
relates: [PW-118]
refs: [planet/tectonics/volcanism.py, planet/zoom_volcanoes.py, docs/review/zoom-polish/pw118_caldera_after.png]
---

## Description
For PW-118 (merge into it). The zoom now draws a hotspot vent with `floor_m > 0` as an
oval caldera (rim, sunk floor, resurgent dome) in a flat lava plain 2x the vent's radius
holding the run's volume (so ~1/4 of its height), laid on the smooth coarse ground
(`zoom_volcanoes._caldera`, `bump_flat`). Before/after: docs/review/zoom-polish/
pw118_caldera_*.png (world:592f2a(73.58,124.18), 250 km @ 0.5 km).
Left: the run side, outside the zoom agent's files. `volcanism.new_vent` still gives a
continental vent hmax ~3 km x U(0.7, 1.1) and the table's `top_m` reaches 4,200 m
(vent at 73.58,124.18: floor 487, height 3,738); a basalt plain plus calderas stands a
few hundred m to ~1 km above its surroundings. Lower hmax (or spread the volume wider,
`radius_km`) and note it in docs/overview.md.
