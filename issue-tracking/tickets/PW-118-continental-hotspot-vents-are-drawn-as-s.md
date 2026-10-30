---
id: PW-118
title: Continental hotspot vents are drawn as shields; they should be calderas on a lava plain
type: task
status: todo
parent: null
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: volcanoes
blocked_by: []
relates: [PW-004, PW-010, PW-649]
refs: [planet/zoom/volcanoes.py, planet/tectonics/volcanism.py, docs/review/zoom-polish/pw118_caldera_after.png]
created: 2026-10-14
updated: 2026-10-26
---

## Description
A plume under a continent also leaves a chain of vents (every ~100-150 km: continental plates are
stiff), each up to ~3 km of relief, and the zoom draws them like ocean islands: Gaussian shields.
Continental hotspot tracks look different: a broad basalt plain (the Snake River Plain) with large
calderas (Yellowstone's ~70 km), rhyolite domes and only modest cones. Draw continental vents
(`floor_m > 0`, or the coarse crust) as a caldera ring with a low resurgent dome on a flat lava plain,
and lower their height limit in the run (`volcanism.new_vent`, hmax ~3 km now).

## Updates
- 2026-10-26: Parent PW-001 (done) -> none. (PW-900 backlog reorg).
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-16: Status in-progress -> todo. Zoom side done; the run's continental volcano height cap (volcanism.TOP_MAX 3,500 m) remains.
- 2026-10-16: Coordinator 2026-10-16: the new 'highest active volcano' highlight always finds 3,500 m on every world: volcanism.TOP_MAX's continental cap binds (a clamp; real continental volcanoes reach ~5.9-6.9 km: Kilimanjaro, Chimborazo, Ojos del Salado). The run height limit part of this ticket should replace the cap with a sound edifice height (e.g. relief above the local base limited by crustal strength/flank failure).
- 2026-10-15: Zoom side done (ff02dc7): oval caldera + lava plain for above-sea hotspot vents. Run height limit in volcanism.py remains (merged draft).
- 2026-10-15: Merged inbox draft draft-continental-vent-run-height.md ("Continental hotspot vents: the run's height limit (zoom side of PW-118 done)", found by zoom-polish).
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
- 2026-10-15: Status todo -> in-progress. Agent started (small-ticket batch, 2026-10-15).
- 2026-10-14: Created from inbox draft draft-continental-hotspot-calderas.md (found by volcanoes).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
