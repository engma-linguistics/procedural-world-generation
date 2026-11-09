# PW-054 scout 251 / 251b, pass 3 (of 3): forked giant-lake check and the cost cut. MERGE

Branch `worktree-agent-adabb700804b9036d` on main 935ddd0e. Pass 2: `scout250.md`. Scripts: `scout251/`. Scratch
(s251) = `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s251/`
(store root for the forked runs: `s251/data`; nothing written to runs/ or worlds/; deleted after pass 3, scripts kept here).

## In plain words
Pass 2's rule (a hollow stays a closed lake basin when everything draining into it is desert by the climate's
own evaporation) is now cheaper and has one more check: a kept hollow whose lake overflows goes back to the old
rule. Tested on forked runs (the same planet state at 200 Myr continued with the old and the new code, three
re-rolled draws each), the new code lifts the land draining inland on generated worlds from 5.1% to 9.3% (L6,
4 seeds) and from 7.1% to 14.0% (L7, seed 11), baseline: the same forks on main. Giant lakes (over 1 Mkm2) show
up in 13.1% of frames against main's 10.4% at L6 (20.9% against 18.4% at L7): inside the spread main's own
draws show (main's per-draw means 7.1-14.6% at L6, 16.4-22.4% at L7), and almost all are the same lake events
main has, in the same hollows. On Earth's terrain the code gets 13.5% inland at L6 and 19.4% at L7 (real:
20.5 / 21.3%). It costs ~15% more run time at L7 (pass 2: ~29% in the same bench).

## Code (commit on this branch)
`pass2.patch` (scout 250) plus, in `planet/hydrology.py`:
1. **Cost**: the dry mask (`_dry_hollows`) is worked out once per `lakes()` call on the uncarved ground and passed
   (`keep`) across the carve tries; `_settle` returns the narrowed `keep`.
2. **Spilling kept lakes dropped**: the recheck after the rivers settle also drops the basin of a kept hollow
   whose lake spills (`keep & wet & open_`), not only a hollow whose catchment turned wet (found on seed 2's
   t = 212 fork: a 1.25 Mkm2 open lake under 2437 mm of rain, `diag_swap.py`).
The golden `tests/golden/sim_L4_s1_60myr.json` is regenerated (the only golden that moved).

## Method
Main (`git archive main` = 935ddd0e, `s251/code/main`) runs each seed to 200 Myr (`fork_run.py spin`, default
params, run_end 400); main and the candidate continue that state to 400 Myr as stored runs (`fork_run.py cont`,
keyframes every 4 Myr), each in three re-rolled draws: `climate_offset` 0 / 1e-5 / 2e-5 C after the fork only
(the null offset of lane 144's forked judge, `docs/review/base-climate/fork-judge/round1.md`). The candidate's
missing `pet` state is None until its first climate update (<= 8 Myr). Measures: health's per-frame measures
(`tools/health.measure_run`), frames after 200 Myr (67: the 4-Myr frames plus the finish window's fine steps).
Note: the draws share their first ~30-50 Myr (the 1e-5 C offset takes that long to diverge; `giant_times.py`).

## Interim fork table: main vs the pass-2 rule with change 1 only (`code/cand`, superseded)
Giant-lake frames % (largest lake > 1 Mkm2) of the 67 frames after 200 Myr; inland median %.
| seed | main d0 / d1 / d2: giant, inland | rule (change 1) d0 / d1 / d2: giant, inland |
|---|---|---|
| 1 L6 | 37.3 / 14.9 / 10.4; 5.9 / 3.5 / 4.0 | 14.9 / 19.4 / 17.9; 6.8 / 6.7 / 6.0 |
| 2 L6 | 0 / 0 / 0; 4.5 / 4.8 / 4.3 | 3.0 / 3.0 / 3.0; 18.9 / 17.8 / 16.2 |
| 3199 L6 | 6.0 / 3.0 / 3.0; 4.8 / 4.6 / 5.2 | 4.5 / 3.0 / 4.5; 10.5 / 12.4 / 14.0 |
| 77 L6 | 14.9 / 10.4 / 25.4; 7.0 / 6.7 / 6.1 | 11.9 / 11.9 / (killed); 13.0 / 12.5 |
| 11 L7 | 16.4 / 16.4 / (pending); 7.3 / 7.5 | 16.4 / (killed); 13.9 |
L6 mean giant frames: main 10.4% (12 runs), rule 8.8% (11 runs): no rise. Seed 2 alone rises (0 -> 3%, 2 frames
in every draw, t = 212 and 232): t = 232 is a deep hollow main keeps too (3851 m); **t = 212 is a 1.25 Mkm2 OPEN
lake under 2437 mm of rain** in a 5.3 Mkm2, 71 m deep hollow the rule kept (catchment P/PET 0.64, just under
0.65: a wet corner of a mixed catchment), which spills only after the carve tries (`diag_keep.py`: open cells
0 / 12 / 139 in tries 0 / 1 / 2). Change 2 drops it (`diag_swap.py`, same terrain and climate: largest lake
1.25 -> 0.07 Mkm2, lakes 2.15 -> 1.11% of land, inland sinks 265 -> 266). Seed 1's rule-only giants (t = 216,
224, 236: closed lakes 1.2-1.3 Mkm2 under ~850 mm, 20-50 m deep flat hollows, dry catchments) stay with change 2:
closed-lake balance in a dry catchment, the rule's intent; they are early (shared by all draws) and gone by 260.


## Final fork table: main vs the final code (`code/cand3`), frames after 200 Myr (67 per run)
Giant = % of frames whose largest lake > 1 Mkm2; inland = median % of ice-free land draining inland; lakes =
mean % of land. Baseline: main (935ddd0e) continued from the same 200-Myr state with the same draws.

| seed | main d0 / d1 / d2: giant; inland; lakes | final d0 / d1 / d2: giant; inland; lakes |
|---|---|---|
| 1 L6 | 37.3 / 14.9 / 10.4; 5.9 / 3.5 / 4.0; 0.95 / 0.96 / 0.77 | 43.3 / 16.4 / 17.9; 7.4 / 5.3 / 5.9; 1.15 / 0.78 / 0.81 |
| 2 L6 | 0 / 0 / 0; 4.5 / 4.8 / 4.3; 0.68 / 0.62 / 0.67 | 1.5 / 1.5 / 1.5; 7.9 / 8.2 / 8.7; 0.71 / 0.69 / 0.62 |
| 3199 L6 | 6.0 / 3.0 / 3.0; 4.8 / 4.6 / 5.2; 0.72 / 0.64 / 0.62 | 6.0 / 6.0 / 1.5; 14.7 / 10.8 / 11.1; 0.79 / 0.98 / 0.69 |
| 77 L6 | 14.9 / 10.4 / 25.4; 7.0 / 6.7 / 6.1; 0.95 / 0.86 / 0.95 | 20.9 / 20.9 / 19.4; 10.6 / 10.6 / 11.1; 0.72 / 0.72 / 0.76 |
| 11 L7 | 16.4 / 16.4 / 22.4; 7.3 / 7.5 / 6.4; 0.90 / 0.94 / 0.89 | 19.4 / 20.9 / 22.4; 11.5 / 14.3 / 16.3; 1.32 / 1.41 / 1.36 |

| mean | giant | giant, t >= 300 (health's window) | inland | lakes | largest lake, median Mkm2 |
|---|---|---|---|---|---|
| L6 main (12 runs) | 10.4 | 7.2 | 5.1 | 0.78 | 0.22 |
| L6 final (12) | **13.1** | **6.0** | **9.3** | 0.78 | 0.21 |
| L6 change 1 only (`cand`, 11, superseded) | 8.8 | 0.8 | 12.2 | 0.84 | 0.20 |
| L7 main (3) | 18.4 | 3.1 | 7.1 | 0.91 | 0.36 |
| L7 final (3) | **20.9** | **0.8** | **14.0** | 1.36 | 0.16 |

- **Giant lakes stay inside main's draw-to-draw spread.** Main's per-draw L6 means (4 seeds) are 14.6 / 7.1 / 9.7%,
  the final code's 17.9 / 11.2 / 10.1%; per seed, seeds 1, 3199 and 77 fall in main's own range of draws (seed 1's
  d0 43.3 against main d0's 37.3: both draws carry the same late giant, t = 390-400). Seed 2 gains one frame
  (t = 232, a 1.43 Mkm2 lake in a 3851 m deep hollow main keeps too; the open wet t = 212 lake is gone). At
  t >= 300, the frames health judges, the final code has fewer giant frames than main at both levels.
  `giant_times.py`: the giant events are main's events (seed 1 t = 228-256, seed 77 t = 208-260, seed 11
  t = 204-256 in every draw of both codes); at L7 the rule makes that 204-256 event's lake larger (2-4 Mkm2 against
  main's 1.5-2.9) and it lasts to 256 rather than 252, then none to 368. Caveat: the 1e-5 C draws share
  their first ~30-50 Myr and seed 77's final d0 / d1 are identical, so the 12 runs are fewer independent samples.
- **Inland lifted**, but less than with change 1 alone at L6 (9.3 against 12.2%): change 2 removes most of seed 2's
  gain (17.6 -> 8.3%), hollows whose lake spills after the carve tries, which drain on to the sea and are rightly
  not closed. On Earth change 2 costs 0.4 points at L6 and nothing at L7 (below).
- Lakes % of land is unchanged at L6 (0.78 / 0.78) and up at L7 (0.91 -> 1.36), largest lake median not larger.

## Earth (terrain + the model's climate, nothing imposed; `scout250/earth_dry.py 6` and `7`, final code)
| | L6 main | L6 pass 2 | L6 final | L7 main | L7 pass 2 | L7 final |
|---|---|---|---|---|---|---|
| inland % (HydroSHEDS real 20.5 / 21.3) | 10.7 | 13.9 | **13.5** | 16.9 | 19.4 | **19.4** |
| share of real closed area found | 42% | 49% | 48% | 53% | 59% | 59% |
| false + (% of land; mean rain) | 2.1 (589 mm) | 3.9 (496) | **3.6 (488)** | 5.5 (480) | 6.8 (432) | **6.8 (432)** |
| land added: % of land, real closed share, rain | - | 3.2, 43%, 266 mm | 2.8, 47%, 219 mm | - | 2.5, 47%, 194 mm | 2.5, 47%, 194 mm |
| lakes % of land, largest lake Mkm2 | 1.77, 0.24 | 1.81, 0.24 | 1.80, 0.24 | 2.71, 0.22 | 2.71, 0.22 | 2.71, 0.22 |
(pass 2 and main columns from `scout250.md`; main's here reproduce them.)

## Cost (L7 seed 11 state at 200 Myr, 30 Myr each, 4 threads, one after another; `bench.sh`, `prof.py`)
| code | 30 Myr wall s | lakes() s (15 calls) |
|---|---|---|
| main | 77.9, 69.7 | 4.0, 3.8 |
| pass 2 | 92.6, 92.1 | 10.2, 10.7 |
| change 1 with the 3-round recheck every try | 84.8, 86.9 | 8.3, 8.8 |
One erosion-step lakes() call (`prof.py`): rule off 0.20-0.23 s, pass 2 0.73 s, change 1 with the recheck in the
first try only 0.41 s. Most of the cost is `route()` (34 -> 20 calls per lakes()) in the recheck rounds, not
`_dry_hollows` (0.04 s). Change 2 needs the recheck in every try again (the spill appears in later tries), but a
round reruns only when something is dropped. Still to do: `bench.sh 30 main p2 cand3 cand3 p2 main` for the final
number (needs `code/cand3` in the bench's code list: it takes `code/<name>`).

Final bench (11-09 12:23, load ~30-33, one after another, L7 seed 11, 30 Myr, 4 threads):
| code | 30 Myr wall s | lakes() s (15 calls) |
|---|---|---|
| main | 78.8, 70.4 (mean 74.6) | 3.8, 4.0 |
| pass 2 | 103.3, 88.7 (96.0, +29%) | 10.2, 9.5 |
| final (`cand3`) | 89.9, 81.8 (85.9, **+15%**) | 8.3, 8.1 |
One erosion-step lakes() call (`prof.py code/cand3`): rule off 0.25 s, final 0.50 s (pass 2 0.73 s, change 1 alone
0.41 s; main's own 0.20-0.23 s in scout 251's run). `route()` is still most of it (75 calls over 3 lakes() calls,
0.67 s of 1.35 s) against `_dry_hollows` 0.03 s per call.

## Checks on the final code
- `tests/test_water.py`: 13 passed. Goldens: `sim_L4_s1_60myr.json` regenerated. Not-slow suite: 1927 passed, 15 skipped. Area tests (test_water, test_water_units, test_world_land, test_zoom_water, test_golden, slow included): 57 passed.
- Kept from the scratch: `scout251/measure.json` (the fork table), `bench_final.txt`, `earth6.txt`, `earth7.txt`.
- Scorecard (`tools/scorecard.py`, line tagged 59d14ccc; baseline: main's line 750aa071, 11-09 08:13): Earth group
  agreement 71.4% (same). Seed 1 / 2 at 1000 Myr: land 34.5 / 35.6% (main 35.1 / 31.5), dry 27.9 / 29.2% (18.0 /
  29.7), ice 1.7 / 0.6% (2.3 / 0.6), largest landmass 7.8 / 13.8% (18.5 / 12.4), peak 6799 / 4743 m (6750 / 5765),
  land NPP 524 / 496 g C/m2 (609 / 671), crust volume x1.019 / 1.037 (1.001 / 1.012). Single 1-Gyr draws diverge
  from main by chaos (the rule moves where the erosion step's rivers end); no frozen or boiled world. The crust
  volume drift (+1.9 / +3.7% against main's +0.1 / +1.2%) is the largest of the last four scorecard lines (-0.7 to
  +1.2%): one draw per seed, so watch it on the next lines (filed as a draft only if it repeats).

## Verdict: merge
Giant-lake frames stay inside main's draw-to-draw spread at both levels (and fall in health's t >= 300 window),
inland drainage is lifted (L6 5.1 -> 9.3%, L7 7.1 -> 14.0%, still under the same code's Earth numbers 13.5 / 19.4%
and Earth's real 20.5 / 21.3%), the Earth false positives are desert (mean rain 488 / 432 mm), and the cost is
+15% run time at L7. Leftovers: inbox drafts (route() cost in the recheck rounds; the L6 gain is half of L7's).
