# Run speed: the climate's cadence and grid (PW-247, lane 27, 2026-10-29)

The climate (`earth.update_climate`) is ~75% of a run's wall time ([profile-2026-10-29.md](profile-2026-10-29.md)).
The owner's asks, for the run only (not the time zoom, zooms or world finishing): (1) the climate half as often,
(2) an L7 run's spin-up climate on the L6 grid, (3) an adaptive cadence, and (4, added 10-29) a ramped cadence,
rare early and back to 4 Myr toward the end. All are output-changing, so they go through the paired judge.

## How each option works (commit 3da7ca1f)
- **(1) Every 8 Myr**: `climate_every = climate_every_max = 8`. Kept only as a timing arm: (4) supersedes it.
- **(4) The ramp** (`earth.climate_cadence`): `climate_every` = 4 Myr in the last `climate_ramp` = 30 Myr before
  the finish window, 8 Myr back to 300 Myr before it, 16 Myr (`climate_every_max`) before that. For a 1 Gyr run:
  16 Myr to 690 Myr, 8 to 960, 4 to 990, then the finish window's every 0.5 Myr step. Updates sit on multiples of
  the cadence. The 2 Myr step that ends at the window's start (990) now gets its own update too (`earth.finishing`;
  main showed 988's climate there), so all 21 candidate moments see their own climate.
- **(3) Adaptive, folded into the ramp**: an update comes early, at any 2 Myr step, once dT has moved
  `climate_adapt_dT` = 1 C since the last update (`earth.climate_moved`, state `sim.climate_in`). The ramp is its
  longest interval. Only dT is a trigger, because the other drivers move steadily, not in episodes. Main's L6 1 Gyr
  run, seed 4242, over its 246 four-Myr intervals:

  | change per 4 Myr | p25 | p50 | p90 | p99 |
  |---|---|---|---|---|
  | land/sea layout (share of the surface flipped) | 3.7% | 4.4% | 6.3% | 9.2% |
  | land height (area-mean abs change, m) | 150 | 174 | 222 | 329 |
  | dT (C) | 0.16 | 0.35 | 1.03 | 2.2 |
  | climate: land temperature, rms per cell (C) | 2.5 | 2.8 | 3.6 | 4.5 |
  | climate: land rain, mean abs ln change | 0.14 | 0.16 | 0.26 | 0.47 |

  Plates move ~2 L6 cells in 4 Myr, so every interval re-lays ~4% of the surface. A layout or height threshold would
  fire at an almost fixed interval, which is just a cadence. dT has episodes: ice-age onsets and recoveries, and
  CO2 swings. Replaying main's dT path through the rule (4 Myr resolution) gives 84 updates per 990 Myr for the bare
  ramp, 114 with the 1 C trigger, against main's 247. The dT gap at an update has p90 1.28 C with the trigger, 2.03
  without it, and 1.03 in main.
- **(2) The spin-up climate on L6** (`Params.climate_level` = 6, `planet/nest.py`). The levels nest: cells
  0..n6-1 of L7 are L6's, and every other L7 cell is the midpoint of an L6 edge. Before the finish window, an L7
  run's `climate.compute` runs on L6:
  - The ground is restricted with area weights (full weighting). A coarse cell is land where at least half its
    area is. It takes the mean height of its land cells, or of its sea cells, and its land's mean ice and
    vegetation feedbacks.
  - The climate is prolonged back with masked linear interpolation: land takes values from land parents and sea
    from sea ones.
  - Temperatures go to sea level and back by the lapse rate, so an L7 cell's own height still sets its air.
  - Wind and current vectors are put back onto the L7 tangent planes.
  - The water balance (runoff, aet), the lakes' evaporation and the Koppen class are redone from the L7 cells' own
    temperatures and rain.

  Ice sheets and vegetation still run on L7, so their state never changes grids. The only climate state that
  carries between updates is the rain kernel's (`rain_state`): it stays on L6 through the spin-up. The finish
  window's first L7 update starts from it prolonged (`nest.prolong_rain_state`). Ocean overturning starts cold at
  every update in main too, so it needs no hand-over. On one L7 state (seed 4242 at 120 Myr), native vs L6-solved:
  - Land mean temperature +0.08 C, with a mean absolute per-cell difference of 0.30 C.
  - Land rain -0.7%. Runoff -2.6%: a Jensen effect, because smoothed rain runs off less.
  - Same Koppen class on 89% of land; SST mean abs difference 0.29 C.
- **Keyframes and slices.** A keyframe between updates shows the last update's climate. That is what the run's
  erosion, weathering and ice used, so the viewer shows the climate the ground was shaped under (up to 16 Myr old
  early, 4 Myr late). Slicing replays the run deterministically, so a slice matches its keyframe as before. A
  world's own climate is computed fresh at the run's level (`timeline._world`), and finish-window worlds are all
  at full L7. Soil memory reads the keyframes' climate as before, so adjacent keyframes repeat early in a run.

## Speed (Threadripper, load 60-160 from two other lanes; 4 numba threads per run; wall and CPU of the process)
One update on one state (median of 3, 8 threads):

| | compute wall / CPU | whole update wall / CPU |
|---|---|---|
| L6 native | 5.1 s / 4.9 s | 5.2 s / 8.2 s |
| L7 native | 15.5 s / 58.7 s | 21.1 s / 69.8 s |
| L7 on the L6 grid | 3.2 s / 10.6 s | 12.7 s / 40.2 s (the ice passes ran long: this state's ice came from an L7 climate) |

Whole runs, launched together (one at a time per arm, so under the same load), seed 4242:

| run | wall | CPU | climate updates | climate wall |
|---|---|---|---|---|
| L6 500 Myr main | 1198 s | 1390 s | 144 | 1012 s |
| L6 500 Myr (1) every 8 | 813 s (1.47x) | 1074 s | 84 | 662 s |
| L6 500 Myr (4) ramp, no trigger | 670 s (1.79x) | 933 s | 77 | 518 s |

| L7 200 Myr main | 3812 s | 5565 s | 69 | 3378 s |
| L7 200 Myr (2) L6 grid, main's 4 Myr cadence | 2382 s (1.60x) | 3070 s (1.81x) | 70 | 1926 s |
| L7 200 Myr (2)+(4) L6 grid and ramp, no trigger | 1915 s (1.99x) | 2203 s (2.53x) | 50 | 1477 s |

At this load, a native L7 update costs ~49 s, a spin-up update on the L6 grid ~18 s (0.37 of it), and an L6
update ~7 s. A 200 Myr run is dominated by its finish window's 21 native updates. A steady-state L7 update on the
L6 grid (cProfile, load ~60) took 10.5 s: compute on L6 4.5 s, the nest ~1.0 s, and ice (2.9 s) and vegetation
(1.9 s) still on L7 (draft-l7-spinup-ice-and-plants-on-l6.md).

**Expected per Gyr**, from these per-update costs and the counts (main 247 spin-up + 21 window updates; B ~114
spin-up with the trigger + 21):
- L6: ~2250 s -> ~1300 s, **~1.7x**.
- L7: ~15300 s -> ~5300 s, **~2.9x** wall, more in CPU.
The judge's own paired run times are below.

## Risks to the physics, and how each is judged
1. **Stale climate while continents move** (up to 16 Myr: 300-1600 km at 2-10 cm/yr). Rain and runoff fall where
   the mountains were. Erosion reads the last update's runoff, so a range that moved gets eroded on its old
   footprint, and a new one is under-eroded until the next update. The ramp keeps 4 Myr for the last 30 Myr and 8
   back to 300 Myr before the window, so the finished worlds' last landscape shaping is at main's cadence.
   Judged by land %, land rain, arid % and trees % (pjudge), the scorecard's erosion and relief lines, and
   earth_check.
2. **The CO2/weathering thermostat and the ice-albedo loop with a long lag.** dT relaxes over 5 Myr, and the ice
   that feeds its albedo term is updated only with the climate. A 16 Myr lag is longer than that relaxation and
   could overshoot or oscillate (icehouse and snowball flips). The dT trigger is the guard: the climate follows
   any 1 C move. Judged by the pass count, icebox and hellhouse colour, late dT and late CO2, and the T/CO2
   histories of main against the arm over whole runs (from the judge's own records; no extra sims).
3. **The sink reference learnt by 300 Myr (PW-980)** would be learnt from 16 Myr cadence erosion, and at L7 from
   L6 runoff (-2.6%). A bias that is the same in the learning and in the late run cancels. The question is
   whether the late run, at 4-8 Myr, erodes differently from the spin-up at 16. Judged by the sink and source
   references and late CO2 (pjudge).
4. **Early ice-sheet and sea-level history**: ice changes only at updates, so early sea level steps every 16 Myr.
   Judged by the iced-land checks at the finish moment, and by the early ice share in the T/CO2 plots.
5. **L7's land-sea mask at L6**: coasts and narrow seas below ~110 km vanish from the climate solve, and
   orographic rain is smoothed. The fine cells keep their own lapse rate and water balance. Judged on an L7 set
   (below).

**Judge plan (lean).** Arm B = (4)+(3)+(2) at commit 3da7ca1f against main (287ca3d0), in the L6 paired judge
(18 draws x 2 rolls; at L6, (2) is a no-op). Then an L7 check of (2) on fewer draws, because L7 runs are 4x the
cost. Split the arms only if B fails. Skipped: separate arms for (1) and for the bare ramp (timing only), 4 rolls,
and an L7 determinism re-run (test_nest covers the coarse spin-up's resume at L4 on L3).
