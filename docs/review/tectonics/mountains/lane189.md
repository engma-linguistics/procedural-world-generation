# PW-1462 lane 189: zoom land detail from local relief

Lane 189, 2026-11-04, on main 9520e8f7. Applies scout 188's `scout2_land_amp.patch` (see `scout2.md` §4), settles the three tests it broke, and checks `SUBCELL_K` = 1.5 on a second world. Scripts beside this file: `lane189_trial.sh` (builds 3 zooms in a scratch data root), `lane189_measure.py` (the tables below).

## In plain words

- The zoom's land detail now follows how rugged the neighbourhood is, not how high it is. On world 899985 (an Earth-like top at 5.5 km), the highest pixel of the plateau zoom falls from 7,535 to 7,217 m, and the 3 km plateau zoom from 4,717 to 3,932 m. Plateau relief inside a cell falls by about 40%. Lowlands barely change.
- K = 1.5 stays. Changing it by 20% either way moves the plateau figures by 6 to 16% and the highest pixel by under 7%: stable when nudged.
- On 899985, flat high cells still come out 3 to 5 times as rough as Earth's at any K. Most of that is not the detail noise (one draft on file).
- The three tests: all three were harness problems the new terrain exposed, not regressions. None of their thresholds changed.

## 1. Before and after on world 899985

Baseline: main (same code without the patch). Earth: scout 188's 4 km p75 of (highest pixel - block mean) by local relief, HydroSHEDS 0.5-degree blocks (`scout2.md` §3), in brackets. Zooms: 1200 km wide, 4 km pixels. Z1 at 37.5S 143W (the 5.5 km plateau and the rugged range beside it), Z2 at 37S 176.8E (a 3 km craton plateau), Z3 at 47.8N 22.1E (lowland). Each cell keeps its mean (median zoom-world cell mean -8 to +8 m in every build).

| zoom | code | highest pixel | flat 0-300 [128] | 300-700 [554] | 700-1200 [844] | 1200-2000 [1,255] | plateau p75 (mean > 2 km, relief < 700) |
|---|---|---|---|---|---|---|---|
| Z1 | main | 7,535 | 1,435 | 1,585 | 1,591 | 1,795 | 1,585 (Earth ~508) |
| Z1 | K 1.2 | 7,208 | 685 | 1,074 | 1,303 | 1,786 | 1,040 |
| Z1 | **K 1.5** | **7,217** | 667 | 942 | 1,220 | 1,689 | **938** |
| Z1 | K 1.8 | 6,963 | 557 | 800 | 1,112 | 1,499 | 795 |
| Z2 | main | 4,717 | 854 | 1,092 | 1,067 | 1,360 | 1,074 (Earth ~310) |
| Z2 | K 1.2 | 4,186 | 474 | 875 | 1,076 | 1,702 | 738 |
| Z2 | **K 1.5** | **3,932** | 442 | 781 | 1,011 | 1,525 | **638** |
| Z2 | K 1.8 | 3,844 | 384 | 712 | 911 | 1,449 | 598 |
| Z3 | main | 1,317 | 281 | 382 | | | lowland p75 260 (Earth ~219) |
| Z3 | **K 1.5** | **1,299** | 231 | 411 | | | lowland p75 274 |

Z1's 2000-3000 m and 3000+ m relief bins: main 2,352 / 3,074 [1,703 / 2,086], K 1.5 2,027 / 2,665.

Against dba204 (scout 188, K 1.5): there the 8 km plateau zoom came out under Earth for 300-2000 m relief and the two 4 km ones over. On 899985 all high ground is over. K = 1.8 would help 899985 and push dba204's plateau further under. The response to K is gentle, so 1.5 stays as the middle.

The flat high cells: from K 1.2 to 1.8 the amplitude falls by a third, but Z1's flat p75 only falls from 685 to 557 m and Z2's from 474 to 384 m (Earth 128). So most of what is left there comes from something other than the detail's amplitude. Candidates (not tested): the landscape pass's valleys and the mean-keeping that lifts the ground between them, the base surface between cells, and the ruggedness's own height term (`stage_terrain.ruggedness`: `0.9 × smoothstep(600, 3500, elev)`).

## 2. The three tests

Each was re-rolled over seeds 1-6 on main and on the patch (`zoom.build(..., seed=k)`) before calling it.

1. **`test_rift_has_fault_blocks_along_its_axis`.** Its plain was a dead-flat 900 m continent. With the patch the zoom draws that plain flat (75% of pixels under 3 m/km, against the rift's 53%), which is right by Earth, so the rift's floors couldn't come out flatter. The harness now gives both worlds low hills: each cell up or down by up to 100 m (a fixed draw), a local relief of 110-190 m. The plain then has 14% flat pixels and the rift 38%. The assertion (`low(rift) > low(plain) + 0.1`) and the steep-scarp ones are unchanged and pass. Rifts on Earth cut hilly uplands, so this compares like with like.
2. **`test_plunge_pool_lies_below_the_whole_fall`.** Main passes 6 of 6 seeds, the patch 3 of 6. Both kinds of failure are harness artefacts:
   - Seeds 1 and 4: the fall sits on the last row or column of the zoom. Its river runs into the cropped halo after one pixel, so its foot and pool are off the delivered grid. Such falls are now skipped. At least one fall must still be checked.
   - Seed 3: a 350 m fall listed over 2 pixels (WF_MAX_KM at 2 km pixels) is also a carved fall with tier basins (`zoom.falls.carve`, PW-517). The test took the first pool down the river, a tier basin 199 m down. The fall's own 60 m pool is at its foot, 350 m down, as PW-341 wants. The test now looks for a pool on the next 5 pixels that lies at least 0.9 × the fall's height below its top. That is the same threshold, without the "first pool" shortcut.
3. **`test_matched_section_carries_the_neighbours_rivers_on`.** On main it fails 3 of the 5 seeds that have crossings, and the patch 4 of 5 (seed 3 has none). So it is chaos on both. The cause: in the 5×5 window the test took the section's largest discharge, and where one of the section's own tributaries joins the river right at the line, that is the river plus the tributary (seed 1 on the patch: 252 m³/s handed on, 604 at the entry pixel, of which ~300 comes from 306 pixels of the section's own ground). The handed-on water itself was right in every case. The harness now measures what each pixel puts in (its discharge minus its donors'), takes the most in the window, and checks the river's course for 5 pixels below. The bounds are the same, 0.8-1.5 × the crossing. It passes on every crossing of seeds 1-8 on the patch and 1-6 on main.

## 3. Tests

Zoom, refine, summit and golden: 142 passed. Not-slow suite: 1012 passed, 1 skipped. Goldens did not move (no zoom in them).
