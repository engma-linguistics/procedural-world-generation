# Plants starve at low CO2 (lane 95, PW-1227 / PW-1224, candidate 1 of co2-crash-diagnosis.md)

## In plain words

**The fix works as a mechanism and makes nothing worse, but on its own it does not clear the crash draw.** When CO2
falls below 124 ppm, the model's plants now starve. Their usual threefold speed-up of rock weathering fades with
their own photosynthesis, using physiology the vegetation model already has. Nothing changes above 124 ppm, and there
is no floor on CO2 and no floor on the volcanic source.

- **The crash draw** (`l6fix` seed 639472, second roll) now bottoms out at **85 ppm instead of 36**, and ends at
  **120 ppm and 8.0 C below pre-industrial instead of 36 ppm and 9.9 C below**. That is better than lane 94's offline
  estimate (73 ppm). But 85 is still under lane 92's 100 ppm crash line, so by that line it is still **1 CO2 crash in
  36 L6 draws**. It is not frozen over (peak land ice 32% of the land, against the 40% bar).
- **Every other dip got shallower too.** The other five draws that went under 124 ppm now bottom out at 108-121 ppm
  (before: 88-119). The recovered 88 ppm dip is now 108, so it no longer counts as a crash.
- **Nothing else moved.** The 30 L6 draws that never went under 124 ppm are identical to main, number for number
  (and all 6 L7 draws: none of them dips that low on either code). Frozen over 0, boiled 0, ocean loss 0, as on main.
  Soft pass 29/36 at L6 (main 28/36: one more draw passes) and 5/6 at L7 (main 5/6).
- **One caveat.** Once a world's CO2 goes under 124 ppm, its later history is not the same world any more: the plates
  take a different path (lane 94 showed a tiny change is enough). So the after-the-dip numbers (end CO2, end
  temperature) of those 6 draws are a fresh roll, not a clean before/after. The minimum is the number to read. The
  screen's median end temperature moved +0.30 C (lane 94's bar was "under 0.3"), five of six ended warmer, and two of
  the six scorecard seeds also diverged after 800 Myr. I read that as the chaos, not a warm bias, because the fix
  can only add CO2 while CO2 is under 124 ppm.
- **On today's main (with lane 98's inland pits, PW-1229) it does the same.** I merged main and re-ran the 7 screen
  draws on both main and main plus this fix (section 4). The pits change re-rolls every draw's history, so the dips
  move. The crash draw still crashes on main (46 ppm); with the fix it bottoms out at **83 ppm** (still under 100).
  Two other draws dip under 124 on the new main (112 and 112 ppm); with the fix they bottom out at 118 and 119. The four
  that stay above 124 are identical on both arms. No dry shift comes from the fix: the arid share moves only on the
  three draws whose history the fix changed, and in both directions.

**For your crash line (PW-1223).** With the fix, the lowest CO2 any of the 42 draws reaches is 85 ppm, then 108, 116,
119, 120, 121, then 133 (an L7 draw) and 136 and up. The fix puts the model's floor where C3 plants starve. Real Earth has stayed above
about 172-180 ppm for the last 24 Myr. If the line is 100 ppm, one draw still fails. If it is set at the plants'
starvation level (somewhere under 124), the draw still dips below it, but only just. Your call; I have not tuned
anything toward a number. As you asked, I stop here: the remaining gap is the plate-speed tail (v2, PW-1158), not
something to push further on this lever.

## The change

`planet/vegetation.py`: `CO2_FLOOR` (= `CA_REF` x 2^-`CO2_RANGE`, 123.7 ppm, the low end of the plants' existing CO2
range) and `starvation(t, pco2)`, the C3 quantum yield's ratio to its value at the floor:

    q(T, Ca) = _q3(T, 0.7 Ca) / _q3(T, 0.7 x 123.7 ppm)   for Ca < 123.7 ppm, else 1; 0 below the compensation point
    _q3(T, ci) = (ci - G*(T)) / (ci + 2 G*(T))            (Farquhar et al. 1980; G* from Bernacchi et al. 2001)

`planet/tectonics/earth.py`: `co2_law` / `co2_slope` / `co2_stock` take `starve` = (each planted cell's share of the sink
at the balance, its temperature). The planted ground's sink becomes

    planted part = FERT(X) x sum_i w_i [1/P + (P-1)/P x q(T_i, X x 500 ppm)],   P = PLANT_WEATHER = 3

so on each cell the plants' part of the enhancement (P - 1 of P) fades with their quantum yield, down to bare ground's
1/P at the compensation point; bare ground keeps X^0.5. GEOCARB's FERT is untouched (no double count above the floor:
the factor is exactly 1 there). `global_temperature` passes the cells (`sink_cells - bare_cells`, `sim.temp`). The
solve stays implicit (backward Euler with Newton), with the slope's starvation term analytic.

- No new constant: P, FERT, `_q3`, G*, `CA_REF`, `CO2_RANGE` all existed. No floor on pCO2 or the source.
- Above the floor it is bit-identical to main (the golden tests pass unchanged; 30/36 L6 and 6/6 L7 tally draws
  reproduce lane 92's numbers exactly).
- No C4/CAM rescue: the weathering plants' PFT mix (`npp_w`) isn't kept. Lane 94's offline estimate for 30% C4/CAM was
  65 instead of 73 ppm, so a small effect (draft `draft-weathering-starvation-c4-and-biomes.md`). The vegetation itself
  still holds its CO2 response at 124 ppm (same draft).
- `docs/overview.md`'s carbon-cycle paragraph describes the new term.

**Unit tests** (`tests/test_co2_stock.py`): `test_starvation_law` (1 at and above the floor, continuous through it, equal
to the `_q3` ratio, 0 under the compensation point, analytic slope against a numerical one, the stock settles on the new
law) and `test_starvation_lane94_offline_table`, which rebuilds lane 94's closed loop (source ln -1.29, sink gain 0.044
per C, 3.9 C per e-fold of CO2, from X 1.06) with two planted temperatures that give the diagnosis's sink-weighted
starvation (3% at 35 ppm, 13% at 50 ppm). It gives 39 ppm as the run is (lane 94: 38), 76 with starvation (73) and 87
with that plus the design gain (84).

## 1. Screen (6 draws under 124 ppm, plus a control)

One roll each, run as lane 92 did (`tools/ice_diag.py --seed S --myr 1000 --level 6 --set star_brightening=1.0
climate_offset=<draw offset + roll>`, code frozen from this branch into scratch, unregistered). Main's numbers are lane
92's `tally_L6.txt`: main's `planet/` is unchanged since lane 92's `e5b526ff` apart from `planet/lineages/`, lane 94
reproduced it bit for bit, and the control draw here (619496, never under 124 ppm) matches it exactly.

| draw (tag, seed, roll, offset) | min pCO2 main -> new | end pCO2 main -> new | end T vs pre-ind. main -> new (C) | peak land ice % main -> new | hard-bar verdict main -> new | soft pass main -> new |
|---|---|---|---|---|---|---|
| l6fix 639472 r0.001 (0.001) | **36 -> 85** | 36 -> 120 | -9.9 -> -8.0 | 33.7 -> 32.0 | CO2 crash -> CO2 crash (85 < 100) | fail -> fail |
| l6c_0 733847 r0.0005 (0.0005) | 119 -> 121 | 338 -> 206 | -2.7 -> -2.0 | 22.6 -> 22.6 | clear -> clear | pass -> pass |
| l6c_p 819014 r0.0005 (0.0015) | 117 -> 119 | 370 -> 344 | -4.6 -> -2.1 | 30.3 -> 28.2 | clear -> clear | fail -> **pass** |
| l6c_p 583167 r0.0005 (0.0015) | 105 -> 116 | 614 -> 492 | +2.5 -> +2.7 | 24.3 -> 24.3 | clear -> clear | pass -> pass |
| l6fix 957317 r0.0005 (0.0005) | 117 -> 120 | 208 -> 338 | -0.8 -> +1.4 | 41.7 -> 41.7 (outside the hard window) | clear -> clear | pass -> pass |
| l6c_p 733847 r0.001 (0.002) | **88 -> 108** | 327 -> 206 | -2.0 -> -3.5 | 28.9 -> 29.7 | CO2 crash -> **clear** | pass -> pass |
| control: l6fix 619496 r0.0005 | 258 -> 258 | 428 -> 428 | +1.0 -> +1.0 | 15.9 -> 15.9 | identical | identical |

- All six minima rose (by 2 to 49 ppm). The deeper the dip, the bigger the lift, as the mechanism says.
- End temperature: median of the six -2.35 -> -2.05 C (+0.30); mean of the paired changes +1.2 C, five of six warmer.
  These end states come after the dip, on a diverged plate history (below), so they are a re-roll, not an effect size.
- The crash draw over its last 70 Myr (new run): 338 ppm at 930 Myr, 155 at 952, 120 at 960, 107 at 980, 92 at 984-990,
  **85 at 993**, 87 at 996, 120 at 1000; dT -7.7 to -8.0 C over 984-1000. Its tectonic history diverged from main's at
  the 866-890 Myr dip (main went to 110 ppm there, so starvation acted): at 930 Myr source_raw is 3278 here against
  lane 94's 3238, and at 1000 Myr 1957 against 890. So part of the lift at the end is a gentler source drop in this
  re-rolled finish, not starvation alone; lane 94's offline loop on the original source path (76 ppm, the unit test)
  is the clean estimate of the mechanism's size.

## 2. Hard-bar tally (36 L6 pooled + 6 L7, lane 92's definitions)

Commands (scratch `l95/`, deleted after; tables kept here as `plant-floor_tally_L6.txt`, `plant-floor_tally_L7.txt`):
`docs/review/base-climate/v1-finish-16/paired.sh <frozen code> <scr> m 0.0005 0.001` (MAXSIM 4, THREADS 2), the 6 L7
draws (the 4 `l6fix` seeds at roll 0.0005, 957317 and 619496 at roll 0.001) at 4 threads, 2 at once, then
`docs/review/v1-cut/tally.py <dir> 6|7`.

| Hard failure (lane 92's definition) | L6 main | L6 new | L7 main | L7 new |
|---|---|---|---|---|
| Frozen over in the judged window (40%+ of land under ice in `ice_criteria.hard_window`) | 0/36 | **0/36** | 0/6 | **0/6** |
| Boiled / hellhouse (dT median > +10.5 or max > +15.5 C) | 0/36 | **0/36** | 0/6 | **0/6** |
| Ocean loss (ocean < 40% of the surface or abs(sea level) > 1000 m after 300 Myr) | 0/36 | **0/36** | 0/6 | **0/6** |
| CO2 crash (pCO2 < 100 ppm at any step after 300 Myr) | 2/36 (36, 88) | **1/36 (85)** | 0/6 | **0/6** |

| Soft measure | L6 main | L6 new | L7 main | L7 new |
|---|---|---|---|---|
| Soft pass (bar + finish moment) | 28/36 (78%) | **29/36 (81%)** | 5/6 | **5/6** |
| Frozen any time after 300 Myr (reported only) | 3/36 | 3/36 | 0/6 | 0/6 |
| End pCO2 outside 180-600 ppm (diagnostic) | 14/36 | 13/36 | 4/6 | 4/6 |

### Minimum pCO2 of every draw (after 300 Myr), for PW-1223

L6, sorted, new code (main in brackets where it differs):
85 (36), 108 (88), 116 (105), 119 (117), 120 (117), 121 (119), 136, 141, 145, 148, 150, 155, 156, 165, 166, 167, 170,
171, 174, 180, 185, 206, 213, 216, 217, 221, 233, 241, 258, 271, 286, 288, 289, 322, 346, 398.

| L6, 36 draws | main | new |
|---|---|---|
| lowest | 36 | 85 |
| 10th percentile | 117 | 120 |
| median | 172 | 172 |
| under 100 ppm | 2 | 1 |
| under 124 ppm | 6 | 6 |
| under 150 ppm | 10 | 10 |
| under 180 ppm | 19 | 19 |

L7, 6 draws, new code: 133, 162, 172, 256, 272, 324 (identical to main: every L7 row reproduces lane 92's `tally_L7.txt` exactly).

Per-draw minima with their draws are in the `pCO2min` column of the two tally tables.

## 3. Tests and scorecard

- `uv run pytest -q -m 'not slow'`: 850 passed, 1 skipped, 3 failed, the 3 being `test_kernel_threads.py`, which fail only because I ran the suite with `NUMBA_NUM_THREADS=1` to stay inside the core cap; rerun without it they pass (13/13 with `test_co2_stock.py`). Climate files (`tests/test_co2_stock.py`, `test_vegetation.py`,
  `test_polar_climate.py`, all markers): 30 passed. Golden outputs unchanged (no `--update-golden`).
- `tools/scorecard.py --seeds 1 2 3 4 5 6 --myr 1000` at L6 (`plant-floor_scorecard_L6.txt`; one line appended to
  `docs/scorecard.jsonl`), against `scorecard_L6.txt`:

| item | main | new |
|---|---|---|
| Earth group agreement / exact; log-rain corr | 71.1% / 38.4%; 0.721 | identical (the Earth climate has no carbon cycle) |
| seeds 2, 3, 4, 5 | | identical in every number |
| seed 1: land / dry / tree cover / NPP / largest plate (max) / ocean age / peak | 31.6% / 20.0% / 42.8% / 462 / 24.9% (54.7) / 54.2 Myr / 6801 m | 35.9% / 25.4% / 34.8% / 360 / 44.5% (54.7) / 70.7 Myr / 5730 m |
| seed 6: land / dry / tree cover / NPP / largest plate (max) / ocean age / peak | 34.9% / 16.0% / 38.1% / 405 / 39.8% (74.4) / 102.3 Myr / 7437 m | 34.7% / 13.6% / 39.0% / 372 / 31.3% (66.8) / 72.1 Myr / 7092 m |

Seeds 1 and 6 match main's tracks up to 800 Myr and differ from 900 Myr on (the scorecard keeps no CO2, but the only
code path that changed acts under 124 ppm, so both must have dipped there in 800-900 Myr). Their 1000 Myr states are
re-rolled finishes: seed 1's land share (35.9%) sits at the top of its own run range and its largest plate is 44.5%,
the known plate-size family (PW-969), and seed 6 moves the other way on most items. No threshold applies to the
scorecard.

## 4. The screen again on main with PW-1229 (lane 98's inland pits)

The coordinator asked for this after PW-1229 merged. Sections 1-3 are on the old base (main `db40504e`). Here, local
main `adb02d5b` was merged into this branch (`1a90ab48`). Both arms were frozen with `git archive`: main `adb02d5b`
(arm M) and the merged branch (arm C). Same 7 draws, same commands, one roll each. The pits change re-rolls every
draw's history, so compare M with C here, not with section 1.

| draw | min pCO2 M -> C | end pCO2 M -> C | end T M -> C (C) | peak land ice % M -> C | arid % M -> C | hard bar M -> C | soft pass M -> C |
|---|---|---|---|---|---|---|---|
| l6fix 639472 r0.001 | **46 -> 83** | 185 -> 246 | -5.3 -> -4.2 | 29.9 -> 29.0 | 21.7 -> 21.8 | CO2 crash -> CO2 crash | pass -> pass |
| l6c_0 733847 r0.0005 | 132 -> 132 | 511 -> 511 | -0.2 -> -0.2 | 25.5 -> 25.5 | 24.6 -> 24.6 | clear (identical) | pass -> pass |
| l6c_p 819014 r0.0005 | 112 -> 118 | 684 -> 567 | +1.5 -> -0.8 | 35.4 -> 35.4 | 23.7 -> 22.1 | clear -> clear | pass -> pass |
| l6c_p 583167 r0.0005 | 132 -> 132 | 171 -> 171 | -4.1 -> -4.1 | 20.2 -> 20.2 | 21.1 -> 21.1 | clear (identical) | pass -> pass |
| l6fix 957317 r0.0005 | 112 -> 119 | 852 -> 633 | +1.5 -> +2.2 | 26.2 -> 26.1 | 23.1 -> 25.8 | clear -> clear | pass -> pass |
| l6c_p 733847 r0.001 | 142 -> 142 | 340 -> 340 | -4.3 -> -4.3 | 26.0 -> 26.0 | 28.2 -> 28.2 | clear (identical) | pass -> pass |
| control l6fix 619496 r0.0005 | 372 -> 372 | 394 -> 394 | +1.9 -> +1.9 | 10.2 -> 10.2 | 24.5 -> 24.5 | identical | identical |

- Same picture as on the old base: every dip under 124 ppm rose (46 -> 83, 112 -> 118, 112 -> 119), and every draw
  that stays above 124 is identical. The crash draw is still a crash by lane 92's 100 ppm line (83 ppm).
- On this base the crash draw passes the soft bar on both arms (its finish moment passes); on the old base it failed
  on both.
- The arid share moves only on the three draws the fix re-rolled, -1.6, +2.7 and +0.1 points, so the fix has no dry
  bias of its own. Lane 98's drier L6 scorecard is a property of the new base (arm M), not of this change.
- The full combined tally is left to the v1 tag sequence, as the coordinator asked.

## Follow-ups

- `issue-tracking/inbox/draft-weathering-starvation-c4-and-biomes.md`: C4/CAM rescue and the vegetation's own 124 ppm hold.
- `issue-tracking/inbox/draft-diag-co2-slope-ignores-starvation.md`: the diagnostics' `w_a` uses the old slope below 124 ppm.
- PW-1223 (crash line) is Daniel's, with the minima above. PW-1158 (plate-speed and source tail) stays v2, out of scope here.

Combined-screen tables: `plant-floor_screen_pw1229_main.txt` (arm M), `plant-floor_screen_pw1229_floor.txt` (arm C).

Scratch (`l95/`: frozen code copies, 56 runs, logs) deleted after; nothing registered, so nothing to `planet delete`.
