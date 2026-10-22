# Ice v2, checkpoint 0: main measured with the stage-0 tools (PW-555)

2026-10-21/22, ice v2 lane, on main b35de08 (coast_loss + cost cut, PW-514 option A). Run physics unchanged: the
diagnostics only read the run (a test checks runs are bit-identical with them on). Criteria:
`docs/review/ice-v2-criteria.md`. Scratch (not committed): session scratchpad `icev2/` (`diag/`, `long/`, `probe/`,
`tz/`, the batch scripts and `table.py`). Moment pickles: regenerate with
`tools/ice_diag.py --seed S --myr 1000 --moments T --out ice_v2_moments` (deterministic).

## The runs: 10 seeds × 1 Gyr L6, plus 2 × 2 Gyr, diagnostics on

Spin-up 300 Myr (owner). Old bar: worst ice sea level ≥ −450 m and ≤ 2% of the time below −430 m (from t = 0). New
bar: N1–N4 (criteria §3.3), with an icehouse = ice holding ≥ 20 m of sea level.

| run | old bar (worst, % < −430) | new bar | fails | icehouse % (eras, longest Myr) | deep < −150 % (longest Myr) | worst after 300 | dT range | CO2 index range | basin term range (end) |
|---|---|---|---|---|---|---|---|---|---|
| s3199 1 Gyr | ok (−228, 0%) | ok | | 49 (3, 196) | 11 (76) | −228 | −6.2..3.4 | −1.21..+0.76 | −239..113 (20) |
| s11 1 Gyr | ok (−417, 0%) | ok | | 43 (6, 76) | 0 | −92 | −4.1..5.1 | −1.68..+0.75 | −164..173 (13) |
| s2 1 Gyr | F (−560, 3.6%) | F | deep 604–760 (160 Myr); an icehouse 340 Myr | 63 (5, 340) | 39 (160) | −560 | −11.0..4.5 | −1.06..+1.79 | −319..62 (−123) |
| s21 1 Gyr | ok (−254, 0%) | ok | | 26 (4, 128) | 13 (88) | −254 | −5.6..7.8 | −1.30..+0.56 | −241..129 (−83) |
| s1 1 Gyr | ok (−397, 0%) | F | deep 460–656 (200 Myr) | 49 (6, 288) | 28 (200) | −397 | −5.8..5.3 | −1.05..+0.49 | −130..98 (−30) |
| s5 1 Gyr | ok (−285, 0%) | ok | | 63 (4, 292) | 30 (148, on at end) | −285 | −7.1..6.0 | −2.72..+0.30 | −297..211 (−297) |
| s7 1 Gyr | ok (−282, 0%) | ok | | 61 (6, 220) | 32 (108, on at end) | −282 | −7.9..5.0 | −2.84..+0.41 | −306..121 (−272) |
| s13 1 Gyr | ok (−379, 0%) | F | icehouse 82% of the time | 82 (3, 300) | 17 (100) | −268 | −11.5..2.1 | −2.43..+0.82 | −335..82 (−227) |
| s42 1 Gyr | F (−510, 6.8%) | F | very deep 440–504 (68 Myr) | 63 (3, 240) | 21 (140) | −510 | −9.8..5.4 | −1.84..+0.40 | −268..179 (−59) |
| s99 1 Gyr | ok (−349, 0%) | F | deep 304–724 (424 Myr); icehouse 100% | 100 (1, 704) | 77 (424, on at end) | −349 | −11.1..2.0 | −2.03..+0.51 | −338..161 (−337) |
| **1 Gyr seeds** | **8/10** | **5/10** | | median 62 | | | | | |
| s11 2 Gyr | ok (−431, 0.2%) | F | an icehouse 352 Myr | 57 (13, 352) | 15 (112) | −381 | −7.9..6.9 | −3.59..+0.94 | −372..129 (−209) |
| s2 2 Gyr | ok (−397, 0%) | F | an icehouse 400 Myr | 57 (9, 400) | 19 (144) | −397 | −12.9..7.3 | −1.25..+1.49 | −251..170 (−95) |

(The 2 Gyr runs are separate trajectories: the CO2 baselines and plant timelines scale with the run's length.)

Icehouse share against the threshold (1 Gyr seeds, % of the time after 300 Myr): ice ≤ −10 m: 39–100 (median 77);
≤ −20 m: 26–100 (median 62); ≤ −40 m: 17–100 (median 45); ≤ −65 m (Earth today): 6–96 (median 38). Land ice never
drops below 1% of the land on 4 of 10 seeds (1–4% on high tropical plateaus and polar mountains, at any dT the runs
reach; the probe keeps 0.4–2.7% at dT +10..+16), so an iced-land threshold calls every run a permanent icehouse.
The criteria count sea level from ice instead.

Without the icehouse-share and length bars (N3), 6/10 pass (N1 recovery, N2 floor, N4 hot eras).

Plots: `seed2_L6.png`, `seed13_L6.png`, `seed21_L6.png`, `seed99_L6.png`, `seed2_L6_2gyr.png` (per run: the two
sea-level terms, dT and its terms, CO2 source and sink against their baselines, the sheets' budgets),
`hysteresis.png`.

## What the diagnostics say about why cold eras last

Each deep era, with the mean of its terms (from `tools/ice_diag.py --summary`; deep = ice below −150 m):

| era | Myr | worst | dT | drift | CO2 term | albedo term | sink / src vs baseline | iced land | sheets' net (m SL/kyr) |
|---|---|---|---|---|---|---|---|---|---|
| s2 464–574 | 114 | −428 | −5.8 | −6.2 | +2.1 | −1.4 | 0.86 / 1.13 | 34% | +29 |
| s2 604–762 | 162 | −560 | −4.4 | −3.6 | +0.1 | −1.1 | 1.01 / 1.05 | 24% | +25 |
| s1 460–658 | 202 | −397 | −3.3 | −1.9 | −0.1 | −1.3 | 1.18 / 1.17 | 26% | +18 |
| s42 432–570 | 142 | −510 | −5.7 | −1.1 | −3.1 | −1.4 | 1.21 / 0.81 | 35% | +27 |
| s99 304–726 | 426 | −349 | −4.4 | −2.4 | −0.7 | −1.2 | 1.16 / 1.07 | 27% | +17 |
| s13 808–906 | 102 | −268 | −8.2 | −3.0 | −3.9 | −1.1 | 1.24 / 0.77 | 21% | +21 |
| s5 788–934 | 150 | −285 | −1.7 | +3.4 | −3.9 | −1.1 | 1.58 / 0.94 | 21% | +16 |

1. **The CO2 clip is never reached.** Over all 12 runs the CO2 index stays within −3.6..+1.8 e-folds against the
   ±3 clip, and it is never clipped (0% of steps) in any deep era. **Base assumption A4 isn't what holds cold eras on
   main.** It will matter once CO2 can rise (A3), but it isn't today's brake.
2. **The thermostat is weak or runs the wrong way in cold eras.** In 5 of 7 deep eras the CO2 term is ≤ +0.1 C, and
   in 3 it is −3..−4 C (cooling). The weathering sink stays at or above its baseline (×0.86–1.58): ice covers only a
   fifth to a third of the land, and the cold slows weathering by only `exp(0.09 dT)`. Meanwhile the source falls
   (×0.77–0.94 in the worst eras: slower spreading). Over the whole run the sink sits above its slowly-learning
   baseline (CO2 index median −0.4..−0.9 on most seeds), so the thermostat leans cold. The 1000 Myr baseline can't
   keep up with the run's own trends (the plants spreading, mountains growing). That is a new base assumption to
   list (A3b, below).
3. **The drift sets the depth.** Deep eras sit where the random drift is −2..−6 C, for 100–400 Myr: much longer than
   its 40 Myr memory, because the thermostat doesn't pull back. Seed 99's 426 Myr deep era is the clearest.
4. **The run's sheets aren't in deficit.** Measured on the run's own climate, every deep era's sheets gain far more
   snow than they lose to melt and the sea (+16..+29 m of sea level per kyr, against Antarctica's ~5), and the ice
   kept in deficit is ~0–1 m. So on main (with the 408 m edge) the cold eras are **climate-supported**, not held by
   a sheet that can't thin. (A surplus that big also says the equilibrium rule has no way to spend it: real sheets
   would flow out to the sea faster. That is the run/zoom gap, below.) The review's root cause 2 (no sheet-wide
   budget) is real for PW-460's honest margins, but isn't what ends or holds eras on main.
5. **Low-latitude ice.** Ice reaches below 30° on 28–56% of updates, at every dT: high tropical plateaus. The
   Chandler & Sohl onset check (ice below 30° only after ice beyond 60°) flags 1 update in s21 and 6 in s2 (2 Gyr),
   all mountain ice. A sea-level version of the check needs a height cut (draft).
6. **The frozen sea in `diag.py` was mis-measured in these runs** (it read the SSTs, which never reach freezing
   because sea ice is a separate share). Fixed after the runs to use the winter sea-ice growth. The probe's numbers
   below use the fixed measure only on the seed-5 staircase.

## Hysteresis probe (`tools/ice_probe.py --stair`, `hysteresis.png`)

Fixed geography, 3 climate updates per 2 C step, from the run's own ice at the moment:

| moment | run's ice at its dT | warming leg: ice gone (> −30 m) at | back at the start dT | gap between the legs | snow on the ice |
|---|---|---|---|---|---|
| s2 @ 500 (dT −10.4) | −428 m | dT +1.6 (+12 C) | −395 m | ≤ 30 m at the ends, 100–170 m mid-way (dT −2..−0.4) | 303 → 880 mm/yr from dT −10 to +6 |
| s5 @ 800 (dT −1.7) | −191 m | dT +2.3 (+4 C) | **−27 m** | **165 m at the run's own dT** | 284 → 900 mm/yr |

- **Two states at the same dT on seed 5:** the run's ice (−191 m) holds itself at a dT where the same planet,
  coming from warm, grows only −27 m. That's the height/air-mass hysteresis (B3), and it is large. On seed 2 the
  state is close to the climate's own equilibrium: −430 m is simply what dT −10 gives that geography (~35 m per C).
- **Exit:** both deep sheets go at dT ≈ +2 C, i.e. 4–12 C of warming from where they sit. The run reaches that
  only through the drift (the CO2 term doesn't give it, above).
- **The moisture brake works per unit area but not in total.** Snow on the ice falls ~3× from warm to cold (880 → 300
  mm/yr), but the sheets' total snow gain *rises* as they spread (s2: 10 → 50 m SL/kyr), so it doesn't limit depth
  at these temperatures. Chandler & Sohl's self-starving happens near a snowball, which the model can't reach (A6).

## The zoom as a window (`tools/tz_mean.py`, 400 kyr, index on, default zoom)

| moment | run ice | zoom mean after 100 kyr vs the run | tol | ok | start in the zoom's range | iced area ×run | endings / backstops |
|---|---|---|---|---|---|---|---|
| fixture (L5 s1 @ 300, −4 C) | −52 m | **−116 m** | 53 | F | 5th pct (interglacial edge) | ×2.68 F | 4 / 0 |
| s2 @ 500 (deep) | −425 m | **+79 m** | 29 | F | 100th (glacial edge) | ×0.88 | 4 / 0 |
| s1 @ 600 (deep) | −307 m | **+84 m** | 26 | F | 100th | ×0.87 | 4 / 0 |
| s5 @ 800 (moderate) | −183 m | +33 m | 30 | F | 94th | ×0.95 | 4 / 0 |
| s3199 @ 800 (mild) | −90 m | +11 m | 16 | ok | 81st | ×1.0 | 3 / 0 |
| s21 @ 700 (warm) | 0 m | −2 m | 15 | ok | 3rd | ×8.3 F (0.02% → 0.2%) | 4 / 0 |
| Earth L6 | — | not measured: blocked (below) | | | | | |
| **within tol** | | **2/6** (PW-467 bar: ≥ 5/7) | | | | area 4/6 | |

Same picture as the PW-462 deep dive, now on main: deep moments start at the zoom's glacial edge and the zoom sheds
~80 m (the run's sheets are bigger than the zoom's dynamics keep, as item 4 suggests); the fixture starts at the
interglacial edge and the zoom grows 116 m. Cycles are 86–116 kyr everywhere, with no backstops.

## Earth (blocked) and the other bars

- **Blocked:** the Earth time zoom and the Earth hysteresis staircase need `tools/earth_data.py` to build the Earth
  grid, and its Köppen download (`koeppen-geiger.vu-wien.ac.at`) failed with connection resets (curl exit 35) on
  every try. Earth's L6 grid isn't cached in this worktree. Main's Earth zoom numbers are PW-514 option A's
  (bit-identical code): cycles 98.5–108.5 kyr, maxima −84..−104 m, interglacial ice 9.1–11.9% of land, Laurentide to
  42.5 N, at `glacial_cool` 6.5 C. **Needed:** the network to that site, or a cached Earth grid from the main
  checkout's data directory.
- Unforced zoom start (< 25 m in 20 kyr, `tests/test_timezoom_consistency.py`): passes on main (pytest).
- Basin term (PW-549, another agent): −372..+211 m over the runs, ending −337..+20 m; on 6 of 10 seeds it ends
  below −50 m. Health now flags it under its own envelope.

## Checkpoint-0 summary

| bar | main |
|---|---|
| old cold-era bar (worst ≥ −450, ≤ 2% < −430), 10 seeds | 8/10 |
| new whole-history bar N1–N4 (≥ 70% to pass) | **5/10** (fails: 3 recovery, 1 very deep length, 2 icehouse share/length) |
| N1–N2–N4 only | 6/10 |
| icehouse share (ice ≤ −20 m), median over seeds | 62% (Earth ~10–30%) |
| PW-467 window mean | 2/6 (Earth blocked) |
| hysteresis: Earth's ice held at dT 0 | blocked (Earth data) |
| hysteresis: cold era's extra ice gone within 2 updates of returning to its start dT | not met on s5 (the run's −191 m state exists only from cold; from warm −27 m), n/a on s2 (no extra) |
| deep exit dT | ≈ +2 C on both probe moments |
| CO2 clip hit in deep eras | 0% of steps |
| sheets in deficit during deep eras | ~0 m (all in surplus) |
| Earth zoom (PW-471 bars) | pass (PW-514 option A numbers) |
| diagnostics cost | L6 1 Gyr 654–678 s with 8 runs at once at 4 threads each; 2 Gyr 1058–1130 s; json ~0.2 MB per Gyr, `--fields` 81 MB per 2 Gyr |

## What this changes in the plan
- The review's stage 1 (honest margins in the zoom) stands: the zoom/run gap is measured (2/6).
- **New, before stage 3:** the carbon cycle's cold-era response (A3, A3b) matters more than the clip (A4). A run's
  deep eras end when the drift turns, not when CO2 builds up. The CO2 stock draft now says so.
- **The default planet is icier than Earth's long-run history:** dT 0 is today's icehouse Earth, and the thermostat
  pulls back toward its own mean, so a default planet spends ~60% of its time in an icehouse (Earth ~10–30%). That is
  base assumption A0 in the criteria. Whether that's a bug or a preference is the owner's call (draft).
