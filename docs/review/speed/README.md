# Run speed: the climate's cadence and grid (PW-247, lane 27, 2026-10-29)

**Outcome (lane 27b, final).** The run's climate cadence is an **8/4/2 Myr ramp plus a 1 C dT trigger**: every
8 Myr, then 4 Myr in the 30 Myr before the finish window, then every 2 Myr step in the last 10 (the owner's fine
end, `climate_ramp_fine`). An L7 run's spin-up climate is solved on the L6 grid. These are the branch defaults.
- **L6:** the 8/4 ramp (arm C) passed the 18-pair paired judge: no measure moved, 16/18 passes against main's 14/18,
  at **1.5x per L6 run**. The fine end changes only the last 10 Myr. On 6 of the draws it sits right next to C.
- **L7 (4 seeds, 1 Gyr):** the full default passes 3/4 against main's 4/4, with 1 icebox each. Its runs took
  3279 s against main's 11591 s (medians). That is not a same-load comparison; see below.
- **Convergence (arm E, every 2 Myr):** main's warm finish (+2.8 C) is mostly its own 4 Myr lag. E finishes 4.1 C
  cooler than main, and C is within 0.3 C of E. But E has **10 iceboxes in 18 against main's 2 and C's 3**: the
  ice and the climate catch up one step per update, so the amount of ice depends on the update rate. Neither main
  nor C is converged in ice. That is a separate soundness gap, written up as an inbox draft
  (draft-ice-climate-loop-steps-per-update.md), not a reason to hold this branch: iceboxes are colour, not
  failures, and C's ice is close to main's.

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
  **Defaults now (lane 27b, cfbed283):** `climate_every_max` = 8 (arm C), and a fine end, `climate_ramp_fine` =
  10 Myr at half `climate_every` (2 Myr, every step). For a 1 Gyr run: 8 Myr to 960, 4 to 980, 2 to 990, then
  the window. That is 2 more updates a run (982 and 986).
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

## Judge results (L6, roll 0.0005, 18 paired draws each against main; pjudge.py and tco2.py)
| arm | moved (CI excludes 0) | end T B-A | moment T B-A | late dT | late CO2 | sink ref | pass (main 14/18) | iceboxes (main 2) | dT sd 300-990 B-A | coldest dT 300-990 B-A | run s, median main / arm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B: 16/8/4 ramp + trigger | moment T | -3.4 | -3.4 * | -1.4 | -0.18 | -0.08 | 11/18 (p 0.51) | 6 | +0.45 (13/19) | -2.0 | 2500 / 1783 |
| C: 8/4 ramp + trigger | none | -3.3 | -3.3 | -1.0 | -0.21 | +0.02 | 16/18 (p 0.69) | 3 | -0.01 (9/18) | +0.2 | 2566 / 1711 |

- B's failure is the lag (risk 2). From 300 Myr on, its dT swings more and dips colder. Its erosion supply,
  relative to its own spin-up, barely shifts (supply.py: within +-0.04 ln per window), so it is not the sink
  reference (risk 3). C's swings match main's.
- Both arms end ~3.3 C cooler than main. Main's finish moments run warm (median +2.8 C against the -6..+3 band,
  PW-980), and C's -0.6 C is inside it. Whether main's warm end is itself a lag artefact is what arm E answers.
- Main and B roll 0.001 (8 more pairs) ran too. Fold them in with `pjudge.py <J> main B` (all rolls).
- Speed: the paired per-run medians come from runs launched back to back (judge2/3.sh start both arms of a draw
  together), so load swings hit both. C is 1.5x at L6. B's 16 Myr step bought only ~5% more.
- earth_check L6 and L7: bit-identical to main (the climate code is unchanged; the change is the run's cadence
  and grid). tools/scorecard.py: not run (two more L6 1 Gyr sims; the judge's 18 draws cover its run measures).
  Run it at merge if the coordinator wants the scorecard line.

## Lane 27b results (2026-10-29)
All on roll 0.0005. pjudge.py and tco2.py as in the handoff below; the frozen code of the new default is
`code/F` (the branch at cfbed283), and its draws are `F_*` under `judge/` and `judge7/`.

**1. The fine end (cfbed283).** `Params.climate_ramp_fine` = 10 Myr: `earth.climate_cadence` returns half of
`climate_every` (2 Myr) in the last 10 Myr before the finish window. Updates now fall at ..., 976, 980, 982, 984,
986, 988, 990 (C: 980, 984, 988, 990): 2 more per run (186 against C's 184 on seed 957317). Goldens unchanged
(no golden run reaches a finish window). Tests: `test_nest.py` checks the cadence at 979/980/989 and the update times
from 952 to 990.

**2. Arm E, every 2 Myr (18 draws).** Does main's warm finish come from its own 4 Myr lag? Mostly, yes.

| arm | climate | finish-moment T, median | moment T vs main (95% CI) | passes | iceboxes | land-ice share of 300-990 (iced10) | coldest dT 300-990 | run s, median |
|---|---|---|---|---|---|---|---|---|
| main | 4 Myr | +2.8 C | - | 14/18 | 2 | 0.32 | -5.2 | 2566 |
| C | 8/4 + trigger | -0.6 C | -3.3 [-4.4, +0.7] | 16/18 | 3 | 0.25 | -5.1 | 1711 |
| E | 2 Myr | -0.8 C | **-4.1 [-5.6, -0.7] \*** | 13/18 | **10** | 0.50 | -6.4 | 4088 |

- E against C: moment T -0.3 C (CI -6.2 to +3.5; 9 up, 9 down), so on temperature C is close to the 2 Myr limit
  and main is the outlier. E has more trees than C (+1.6 points, CI excludes 0). No other measure moved.
- E's iceboxes are real, not a sampling effect: the icebox flag is a time share (90% of 300 Myr+ below the
  icehouse sea level, or 30% below -150 m), and E spends 17% of its late steps below -150 m against main's 7%
  and C's 0%.
- **Why (cheap probe, iceprobe.py):** every update moves the ice's sea level by about the same amount in
  all three arms (median 2.2-3.4 m per update that moved it). So the ice moves faster per Myr when updates come
  more often: 1.8 m/Myr in E, 1.1 in main, 0.8 in C. `earth.ice_sheets` settles the sheets under each update's
  climate, but that climate saw the previous update's ice, so the ice-climate loop takes one step per update.
  E's albedo term runs at -0.28 C against main's +0.12. Candidates and the decision are in
  draft-ice-climate-loop-steps-per-update.md. No new sims were run for it.
- E costs 1.6x main per run.

**3. The fine end on 6 draws (l6fix x4, l6c_0 819014 and 958504; no new main runs).** It lands between C and E,
right next to C, as it should: F and C are identical up to 980 Myr.

| on these 6 draws | main | C | F (default) | E |
|---|---|---|---|---|
| finish-moment T, median | +2.9 | +1.2 | +1.0 | -3.7 |
| passes | 4/6 | 5/6 | 5/6 | 5/6 |
| iceboxes | 1 | 2 | 2 | 2 |

F - C: moment T -0.16 C (5 of 6 cooler, sign p 0.22); late dT, CO2, arid, rain and trees all within +-0.1. The
fine end cannot reach E's ice: E's extra ice is built over hundreds of Myr, and the fine end covers only 10.
Verdict: no change to the judge's picture, so no more runs. F's run times (median 738 s) are not comparable to
C's (1680 s): F ran later, at load ~22 against ~100. The 2 extra updates cost about 1% of a run.

**4. Arm G at L7 (4 seeds): main's 4 Myr cadence plus the L6-grid spin-up climate.**
**5. The full default at L7 (arm F, same 4 seeds; main's runs reused).** Four pairs can catch only a large
shift. The bar at L7 is ~60% passing.

| L7, 4 pairs | main | G (L6 grid) | F (default: ramp + L6 grid) |
|---|---|---|---|
| passes | 4/4 | 4/4 | 3/4 (seed 619496 fails, warm: end T +6.4) |
| iceboxes | 1 | 2 | 1 |
| finish-moment T, median (vs main, paired) | +0.8 | -1.8 (-1.8; 1 up / 3 down) | +1.5 (+2.0; 2 / 2) |
| late dT vs main | | -3.3 (1 / 3) | -1.3 (1 / 3) |
| arid % vs main | | -2.2 (0 / 4) | -2.1 (0 / 4) |
| hot desert % vs main | | -3.3 (0 / 4) | -2.3 (0 / 4) |
| land rain, trees, land %, sink ref | | no direction | no direction |
| land-ice share 300-990 (iced10), median | 0.20 | 0.59 | 0.40 |
| run wall, median | 11591 s | 6512 s (1.8x) | 3279 s (3.5x) |

- The arid and hot-desert drop (0 of 4 up, sign p 0.125) is in the spin-up records only. pjudge averages the
  climate updates 600-1000 Myr, and for G and F those are mostly the L6-grid solve's Koppen classes. Over the
  native L7 finish window, which is what the worlds get, the arid share is main 21.9%, G 24.0%, F 23.4% (means of
  the 4 seeds; aridwin.py). So the finished worlds are not drier. The coarse solve classes a little less
  land as desert in the spin-up, which fits its smoothed rain and temperature fields.
- Nothing else has a direction across the 4 pairs. G's extra land ice (0.59 against 0.20, 3 of 4) is the same
  ice-loop sensitivity as arm E's, at 4 pairs; F's is 0.40.
- **Speed:** the run times are not paired under the same load. main's 4 L7 runs ran at load 60-150. G's
  overlapped them. F's ran later, at load 22-110. G at 1.8x is the fairer number for the grid alone; F's 3.5x
  overstates the default somewhat. The expected per-Gyr gain from the per-update costs is ~2.9x (Speed, above).
  An L7 speed figure under equal load needs F and main launched together. That costs no judge draws:
  `planet simulate` timings at merge would do.

**What to merge.** The branch defaults: the 8/4/2 ramp, the 1 C trigger and the L6-grid spin-up. They passed at
L6 (18 pairs, arm C; the fine end is a 10 Myr change on top) and showed no large shift at L7 (4 pairs).

## Handoff (lane 27, at ~230k context; items 1-5 are done above, by lane 27b)
Outputs are in `<scratchpad>/lane27/`. The frozen code is in `code/<arm>` (main = 287ca3d0; B = 3da7ca1f; C, E
and G = B's code with params edited: C `climate_every_max` 8; E `climate_every` 2, max 2, trigger off; G max 4,
trigger off, `climate_level` 6). The L6 draws are in `judge/`, the L7 draws in `judge7/`.
1. **Arm E (convergence; owner's ask 10-29).** 18 draws, launched by `judge4.sh`. Judge it with
   `pjudge.py <J>/judge main E --rolls 0.0005` and `tco2.py <J>/judge main E`.
   - If E is about main, 4 Myr is converged and B's problem was the lag alone.
   - If E differs (fewer cold dips, a different end T or pass rate), main is under-resolved and partly tuned to
     its own lag: report that plainly.
   - E's cost is the `secs` row of tco2.py.
2. **L7 set, option (2) alone.** Arm G (main's 4 Myr cadence, spin-up climate on L6) against main: the 4 l6fix
   seeds, roll 0.0005, 1 Gyr. Launched by `judge7g.sh` and `judge7m.sh`, at most 4 at once. Judge with
   `pjudge.py <J>/judge7 main G --level 7` and `tco2.py ... --level 7`. Four pairs can only catch a large shift:
   read the paired direction of end T, land rain, arid % and trees %, and the run times. The bar at L7 is ~60%
   passing (owner, v1).
3. If G is clean, the branch's defaults (C's cadence plus `climate_level` 6) are what to merge. The L7 cadence
   plus grid together was never judged at L7. C's cadence is judged at L6 only.
4. **Task for 27b (owner, 10-29): a 2 Myr stage at the ramp's end**, 8 -> 4 -> 2 Myr before the finish window.
   Make it a param (e.g. `climate_ramp_fine` = 10 Myr at 2 Myr, every tectonic step) in `earth.climate_cadence`,
   with 4 Myr from there back to 30 Myr as now. It adds only ~3 updates per run. Don't run a new 18-pair set for
   it: judge it with arm E's tally, as E shows the every-2 Myr limit. Its finish-moment T should land between
   C's and E's.
5. The lane 26b coasts judge was paused for this lane. Tell the coordinator when E and G no longer need the CPU.
