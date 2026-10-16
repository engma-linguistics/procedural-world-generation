---
title: "Zoom undesigned drops: three causes measured (arc soft-cap slopes, creep on 4 km pixels, landform bedding)"
type: task
status: needs-decision
parent: null
subsystem: zoom
effort: m
impact: low
found_by: zoom-polish
blocked_by: []
relates: [PW-125]
refs: [planet/zoom.py, "world:592f2a(-9.35,-161.39)", "world:592f2a(49.32,37.38)", "world:592f2a(4.81,-72.18)", "world:592f2a(1.96,-70.44)"]
---

## Description
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
