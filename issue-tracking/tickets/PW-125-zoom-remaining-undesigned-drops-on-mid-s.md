---
id: PW-125
title: "Zoom: remaining undesigned drops on mid-size streams, coarse-zoom hanging joins, edge steps"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomsmalls
blocked_by: []
relates: [PW-070, PW-069]
refs: [planet/zoom.py, "zoom:031ecf", "zoom:f2b532", "zoom:afdaf5", "world:592f2a(-9.35,-161.39)", "world:592f2a(49.32,37.38)", "world:592f2a(4.81,-72.18)", "world:592f2a(1.96,-70.44)"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
After zoomsmalls (creep no longer lifts stream beds, contrast filter in `waterfalls()`), 20 test zooms
still list 32 undesigned drops (14 >= 100 m), mostly on 50-300 m3/s streams that drop 100-490 m over
3-5 km in one concentrated step. Worst: zoom:031ecf px (457, 470), 490 m at 96 m3/s. Without the
contrast filter there are ~300 such steps (149 >= 100 m), so the terrain still has them.
- On the 4 km zoom f2b532, 5 tributaries still join a reach with falls in a hanging step (PW-069's
  "hanging joins mid-falls"); on finer zooms none were left.
- Steps into the region's edge (edge pixels are fixed at the target surface) are no longer listed
  (`WF_EDGE_PX` = 8), but are still in the terrain (e.g. afdaf5 cols 4-10, 270-320 m).
- In the synthetic `_escarpment_world(1.2, 400)` a few cascades still realise ~0.1 m (4 of ~13).
Measure with a per-zoom count of `waterfalls(..., top=100000)` kinds; find which floor/cap or
re-routing leaves each step (the zoomsmalls report has the diagnostic approach).

## Updates
- 2026-10-15: Status in-progress -> done. Done (e503044): creep as diffusivity above 2 km (owner C) + stream mask at 2 km; remap correction on hillslopes only; exact summit taper; waterfalls() requires 3x steeper than BOTH sides (as documented). 8 zooms of 592f2a: drops >=100 m 131 -> 33. Tiled reference confirms C (range 295 vs 300 ref). Stitching: seams ~10x normal step, 0-45% stream continuity, 3-10x cost: not a stand-in. Write-up docs/review/zoom-polish/pw125.md.
- 2026-10-15: Status todo -> in-progress. Agent working (creep scaling C + tiled-1km reference check).
- 2026-10-15: Status needs-decision -> todo. Owner 2026-10-15: take the sound fix (C: creep step scaled by (2 km/res)^2) even if 4 km zooms look rougher. Before finalising, check against a reference: 1 km zooms tiled over part of a 4 km zoom's area, averaged to 4 km. If C's 4 km terrain matches that roughness, C is right.
- 2026-10-15: Status in-progress -> needs-decision. Diagnosed, no code change: ~80% of 114 drops on arcs from landscape-pass steep first links below the soft summit taper; creep lift up to 470 m. Three creep fixes changed every 4 km zoom; needs owner call.
- 2026-10-15: Merged inbox draft draft-zoom-undesigned-drops-causes.md ("Zoom undesigned drops: three causes measured (arc soft-cap slopes, creep on 4 km pixels, landform bedding)", found by zoom-polish).
  For PW-125 (merge into it). Re-measured on main after PW-268/269, world 592f2a, the
  showcase zoom specs rebuilt with `zoom.build` (8 zooms): 151 `drop` falls in
  `stats.falls`, 114 of them >= 100 m. Almost all are on 20-50 m^3/s streams, not
  50-300 any more. Per drop >= 100 m, the stage where it first reaches 70% of its final
  height (heights captured after the landscape pass, after creep, after landform
  bedding, after the final drainage):
  
  1. **Landscape pass, volcanic arcs (~80%)**: -9.35,-161.39 (2000 km @ 4 km, an island
     arc, 109 volcanoes): 72-81 drops >= 100 m, up to 870 m, ARC_CLASS pixels, most
     of them tributaries joining a capped river course (foot cap = foot height). The
     lip sits one `integrate` link (s x dist) above the foot: C is refitted huge to keep
     the arc's rugged cell means, so a 48 m^3/s stream's first link is ~200 m/km, while
     above it the slope tapers (`soft`), so the detector sees a concentrated step. Not
     the young-cone pin (unpinning cones within 1-2 bank widths of coarse rivers moved
     nothing). Also 13 on 1.96,-70.44 (1 km).
  2. **Creep (2-4 km pixels)**: 49.32,37.38 (4 km): 10 of 11 drops >= 100 m; the lip
     pixel (20-50 m^3/s on the final drainage) is lifted 50-470 m by creep while its
     foot is not, because it was not a `chan > 0` stream (threshold 50 x res^2 of
     drainage, 800 km^2 at 4 km). Tried:
     - A. no-lift for any pixel >= 4 px of rain drains through: removes all 10 (2-10 px
       alike), cell means unchanged, but valleys everywhere stay V-sharp: on the
       synthetic escarpment plain (800 km @ 2 km) pixel steps > 120 m 1138 -> 2837,
       median step 15 -> 21 m (fails test_escarpment_steps_up_to_a_plateau).
     - B. no-lift for Q >= 20 m^3/s on the landscape network: no effect (those pixels
       weren't on it; the final drainage moved).
     - C. creep per step scaled by (2 km / res)^2 above 2 km (diffusion: kd ~ D/res^2;
       KD was set at 2 km): 11 -> 4 drops >= 100 m, but 4 km zooms get much rougher
       (mean |Laplacian| 32 -> 64 m, median step 35 -> 48 m).
     None taken: each changes the look of every 4 km zoom. Lean: C is the physically
     sound one (creep is a diffusivity, its per-pixel step should fall with pixel size),
     but it needs a look at 4 km hillshades first.
  3. **Landform bedding** (`lf.remap`): 5-7 drops on 4.81,-72.18 (1 km, fold belt and
     hills), 180-430 m, first appearing after the remap.
  
  Not re-checked: hanging joins on reaches with falls at 4 km (none of the 8 zooms had
  `join` drops on designed reaches), edge steps, the synthetic cascades of
  `_escarpment_world(1.2, 400)`.
  
  Options: A/B/C above for (2); for (1), let `soft` taper only above the coarse cell's
  mean summit level rather than per pixel, or have `waterfalls()` compare against the
  hillslope gradient beside the reach (so a steep stream among steeper slopes isn't a
  fall). Diagnostic: capture `h` after each stage in `build` and compare lip/foot.
  - [ ] decide on (2), then re-measure the 8 zooms
- 2026-10-15: Status todo -> in-progress. Agent started (small-ticket batch, 2026-10-15).
- 2026-10-14: Created from inbox draft draft-zoom-remaining-undesigned-drops.md (found by zoomsmalls).
