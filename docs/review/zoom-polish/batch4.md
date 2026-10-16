# Zoom batch 4: PW-341, 343, 350, 349, 345 (2026-10-16)

Measured as in pw298.md: world 592f2a (showcase L7 seed 3199 @ 380 Myr), its 8 highlight zooms plus the
glaciated plateau -48.48, 60.12, each built with zoom seeds 1-5 (`zoom.build` in memory). "Drops" are
`stats.falls` of kind `drop` >= 100 m; "inland" is `stats.inland_cell_mean_*`.

## PW-341: plunge pools at the fall's foot

`waterfalls()` recorded the pool's pixel as the one right below the fall's top (`rec[i]`); it is now the
pixel its drop is measured to (`jj`), and a designed lip's pool goes to the foot of its listed fall. On
4.81,-72.18 (zoom e33c3d's spec), seed 1: all 23 pooled falls (3-4 px long, 140-325 m) now have their whole
drop above the pool; before, the pool was on the first pixel, with almost all of the drop below it.
Test: `test_plunge_pool_lies_below_the_whole_fall`.

## PW-343: kernels.flood_fill for filled-only callers

`zoom.coarse_lakes` and highlights' lakes / water surface: same bits as `priority_flood(...)[0]` on 592f2a,
bd9a7a, fac2af. Test: `test_coarse_lake_levels_are_the_priority_flood_spill`.

## PW-350: glacier snouts

The ice's thickness from its flux is capped by Nye's plastic profile H = sqrt(2 tau x / (rho g))
(tau = 100 kPa: ~150 m 1 km back, ~330 m 5 km back), x measured down the flow to where the ice ends on
open land; a pixel holds the profile's mean over its length (172 m on a 3 km pixel's last step, 212 m on a
diagonal one; ~100 m at 1 km). Calving fronts and ice leaving the region keep their thickness. The sides
of a tongue take the nearest tongue pixel's thickness (they took the max within 4 px, upstream included).

Test massif of `test_zoom_ice` (900 km at 3 km): land snouts 384 / 502 / 573 m (p50 / p90 / max) -> 212 m,
356-375 m one pixel back; ice volume -0.6%; the ice mask is unchanged. The 0.5% allowance on > 12 C ground
stays: the big tongues end by the 100 km run cap still carrying ~2.8 km^3/yr against -20..-30 m/yr of
melt, because for most of their run they hug the ice cap's margin, which feeds them, and the flux is
re-clipped to GL_F_MAX at every pixel (~4 km^3/yr discarded along the biggest one): inbox draft
`draft-zoom-tongue-run-along-margin.md`. Thinning the snout doesn't move where the ice ends.

## PW-349: delta plains on low ground

The plain's weight now fades from full at 30 m of coarse ground to none at 250 m (was 250 -> 800 m), and
what it still takes off an inland cell's mean goes back on that cell's land beyond the plain (12 smooth
passes; coastal cells left to the delta; no clamp in those passes: `clamp()` isn't idempotent, and
twelve extra clamps lifted low coastal land by metres).

| Zoom (seeds 1-5) | inland bias / RMS before | after | coastal land | sea cells |
|---|---|---|---|---|
| 4.97,-114.51 (1000 @ 2) | -25.3 / 54 | **-1.9 / 10** | -15.8 -> -13.6 | +70 (same) |
| 1.96,-70.44 (500 @ 1) | -27.4 / 87 | **-0.2 / 33** | +4.3 -> +5.1 | +311 (same) |

(coastal and sea columns: seeds 1-3.) The all-cells bias of these two rises (+2 / -7 -> +16 / +17 m):
the plain's deficit had been offsetting the sea cells' shallowing (trench and prodelta cells, +70 / +311 m),
which is unchanged. The test world of `test_zoom_water` gets a coastal lowland (8-30 m, ~250 km wide)
for its delta: its coast stood 60+ m in the world, where the zoom no longer lays a plain.

## Drops and inland means after the batch

| Zoom | drops before | after | inland bias / RMS before | after |
|---|---|---|---|---|
| 4.97,-114.51 | 0 | 0 | -25.3 / 54 | -1.9 / 10 |
| 1.96,-70.44 | 0 | 0.4 | -27.4 / 87 | -0.2 / 33 |
| 4.81,-72.18 | 1.6 | 1.6 | -2.7 / 54 | -2.7 / 54 |
| 60.6,-40.48 | 0 | 0 | -1.6 / 8 | -1.6 / 8 |
| 49.32,37.38 | 0.8 | 0.8 | +1.3 / 55 | +1.3 / 55 |
| -9.35,-161.39 (arc) | 3.4 | 3.6 | -5.8 / 58 | +0.2 / 55 |
| -2.22,-169.11 | 0.2 | 0.2 | +1.1 / 41 | +1.1 / 41 |
| -63.44,71.66 | 3.0 | 3.0 | -0.9 / 24 | -0.9 / 24 |
| **8 zooms** | **9.0** (4-12 by seed) | **9.6** (4-13) | | |
| -48.48,60.12 (plateau) | 0.6 | 0.6 | +1.5 / 14 | +1.5 / 14 |

Only the zooms with deltas moved. The three new drops >= 100 m (1.96,-70.44 seeds 1 and 5; the arc) lie
beyond the plains (r / R 1.0-1.4) on 360-1170 m ground the old plains' reach had damped, and are there
with or without the mean restoration: the landscape pass's own drops (PW-125's kind), within the seeds'
spread.

## PW-345: zoom soils' slope conversion

`tools/zoom_soil_check.py` on seven 400 km zooms of a1d3b9 @ 1000 Myr (keyframe world: a gentle plain
-33.08,-94.56, plateaus -17.46,108.58 and 1.68,-98.31, hills -6.14,30.52, a range -16.77,25.75, dry
-22.25,-165.83, wet lowland -2.66,-84.35). Pixel/cell erosion ratio (median over cells):

| Site | 4 km before | 4 km after | 2 km | 1 km | 0.5 km |
|---|---|---|---|---|---|
| plain | 0.94 | 0.82 | 0.81 | 0.81 | 0.83 |
| plateau | 1.19 | 0.81 | 0.75 | 0.85 | 0.91 |
| plateau2 | 0.93 | 0.62 | 0.86 | 1.09 | 1.08 |
| hills | 1.44 | 0.95 | 0.94 | 1.02 | 1.08 |
| range | 0.50 | 0.34 | 0.36 | 0.27 | 0.34 |
| dry | 0.93 | 0.63 | 0.45 | 0.65 | 0.73 |
| wet | 0.44 | 0.33 | 0.41 | 0.44 | 0.44 |

Finer than 2 km the self-affine (2 km / res)^0.6 holds (1 and 0.5 km within 0.75-1.6x of 2 km, median
1.1), so option B (a fixed baseline) isn't needed; the pixel slope from 2 to 4 km falls only as
(2 km / res)^0.27 (median of the seven; PW-125's creep makes a 4 km pixel the mean of the finer terrain),
so the exponent above 2 km is now 0.3. The regional spread (0.3-1.1) is the zoom's own roughness against
the cell's measure: option A, as the ticket leaned; C (a per-cell pull) not taken.
