# PW-054 scout 251, pass 3 (of 3): forked giant-lake check and the cost cut. INTERIM (handed off)

Branch `worktree-agent-adabb700804b9036d` on main 935ddd0e. Pass 2: `scout250.md`. Scripts: `scout251/`. Scratch
(s251) = `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s251/`
(store root for the forked runs: `s251/data`; nothing written to runs/ or worlds/).

## State at hand-off (11:10, 2026-11-09)
- Worktree: `pass2.patch` applied, plus two changes in `planet/hydrology.py` (uncommitted until the WIP commit):
  1. **Cost**: the dry mask (`_dry_hollows`) is worked out once per `lakes()` call on the uncarved ground and
     passed (`keep`) across the carve tries; `_settle` returns the narrowed `keep`.
  2. **Fix found by the forks**: the recheck after the rivers settle also drops the basin of a kept hollow whose
     lake spills (`keep & wet & open_` -> its `basin` ids), not only a hollow whose catchment turned wet.
- `tests/test_water.py` passes (13) with change 1 + the earlier sink variant; re-run with the final code.
  Goldens not regenerated yet; scorecard not run.
- `s251/run_all.sh` (PID 1368469, started 11:09) waits for load < 30, then runs the final candidate's forks
  (`code/cand3` = worktree's planet at hand-off): `l6c.jobs` (seeds 1, 2, 3199, 77 x draws d0-d2, names
  `s<seed>_cand3_d<k>`), `l7a.jobs` (`s11_cand3_d0`, `s11_main_d2`), then `l7b.jobs` (`s11_cand3_d1`, `_d2`).
  Its log: `s251/run_all.log`, per-run logs `s251/logs/`. Measure: from the worktree,
  `uv run python docs/review/basins/scout251/measure.py <s251>/data` (table + `s251/measure.json`).

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

## Left to do (the successor)
1. Wait for `run_all.sh` ("all done" in `s251/run_all.log`), run `measure.py`, build the final fork table
   (main d0-d2 vs `cand3` d0-d2, all five seeds), and judge: merge if the rule's giant-lake frames stay within
   main's draw-to-draw spread.
2. Bench (above), Earth check (`docs/review/basins/scout250/earth_dry.py 6` and `7`, from the worktree: inland %,
   false +), `uv run pytest -q tests/test_water.py`, goldens (`uv run pytest tests/test_golden.py --update-golden`),
   `uv run python tools/scorecard.py`, area tests, commit (amend the WIP commit into one real commit), finish this file.
3. Delete `s251/` when done (keep >= 40 GB free in /tmp).
