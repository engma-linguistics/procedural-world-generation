# The forked paired judge (lane 144), round 1: built, validated, not adopted

**In plain words.** Every planet learns its carbon-cycle yardstick in its first 300 Myr and then keeps it. Lane 140d
found that the yardstick is close to a random draw, so when a change is judged by re-running the same planets, it is
judged partly on a new draw of the yardstick. This harness removes that: each test planet is run once to 300 Myr,
saved, and both the current code and the candidate carry on from that same saved planet. It works exactly (the
carried-on current code is the same run, bit for bit). But on main's six coldest test planets it does **not** make the
ice in the last ~120 Myr any less random: a change that does nothing still moves those planets' peak land ice by 3-23
points, as much as without the fork, and one such do-nothing run put 2 of the 6 over the 40% frozen-over line. What
the fork does remove is the yardstick's bias: re-runs of planets picked for being cold no longer come back warmer on
average. Daniel decides whether to use it (draft `draft-fork-judge-adopt.md`); nothing in the existing judge changed.

## 1. What it is and how to run it
Files, beside the existing judge in `docs/review/base-climate/v1-finish-16/`:
- `paired_fork.sh MAIN_CODE CAND_CODE OUT_ROOT ROLL...`: the same 18 seed-draws per roll as `paired.sh` (it reads
  paired.sh's own list), the same `ice_diag` parameters (`star_brightening=1.0`, `climate_offset` = draw offset +
  roll), the same caps (`MAXSIM`, `MINFREE`, `THREADS`, `LEVEL`). Per draw: (1) MAIN_CODE runs the draw to `FORK`
  Myr (default 300 = `earth.REF_FREEZE`) and saves `Simulation.state()` plus the diag records so far to
  `OUT_ROOT/fork/r<ROLL>_<tag>/`; (2) arm `MAIN_ARM` (default `m`) continues with MAIN_CODE and arm `CAND_ARM`
  (default `c`) with CAND_CODE from that file to 1000 Myr, at once. Outputs are in paired.sh's layout
  (`OUT_ROOT/<ARM>_r<ROLL>_<tag>/seed<S>_L6.json.gz`), so `pjudge.py OUT_ROOT m c` reads them unchanged.
- `fork.py`: the simulation step (`spin`, `cont`) and the yardstick report (`yard`). It is `tools/ice_diag.py`'s run
  split in two and uses only the existing resume path, `Simulation.state()` / `Simulation.from_state()`, whose
  bit-identity `tests/test_state.py` already guards. **Nothing under `planet/` changed**; goldens untouched.
- Options: `CAND_SET="k=v ..."` and `CAND_DOFF` (added to the candidate's `climate_offset`) apply to the candidate
  after the fork only; `CAND_SPIN=1` also spins the candidate's own code to the fork (for `yard`, section 3);
  `MAIN_FROM=<paired.sh root>/<arm>` copies an existing unforked main arm's results instead of re-running them (valid
  when that arm ran the same frozen main code at the same THREADS: section 2a); `ONLY` is a regex on
  `r<ROLL>_<tag>_<seed>`.
- `tools/hard_bar.py` reads arms named `m_r*`: for another arm, point it at a folder of links
  `m_r<ROLL>_<tag> -> <OUT_ROOT>/<ARM>_r<ROLL>_<tag>` (delete the links with `find -P DIR -maxdepth 1 -type l -delete`).
- Cost per draw: the spin is ~3.5-5 min of a ~18 min L6 run (L6, THREADS 3, machine load ~44), so two arms cost ~1.7
  runs instead of 2 (1.0 with `MAIN_FROM`, +0.25 with `CAND_SPIN`). A 300 Myr state is ~44 MB on disk (zlib).

Example (2 rolls, 36 draws per arm; at 12 cores `MAXSIM=4 THREADS=3`):
```
git archive <main> | tar -x -C <scratch>/code/main;  git archive <cand> | tar -x -C <scratch>/code/cand
MAXSIM=4 docs/review/base-climate/v1-finish-16/paired_fork.sh <scratch>/code/main <scratch>/code/cand <scratch>/fj 0.0005 0.001
uv run python docs/review/base-climate/v1-finish-16/pjudge.py <scratch>/fj m c --table
```

## 2. Validation (lane 140's frozen main 4abc1707 and its six coldest draws, 2026-11-03)
Main = lane 140's frozen main code (`git archive 4abc1707`, the judge's main arm in round1 sections 3-8 of
`docs/review/vegetation/herb-roots/`), so the forked runs compare directly with lane 140's unforked ones: main
(the judge), **null** (lane 140c: offset + 1e-5 C over the whole run) and **null2** (lane 140d: + 2e-5 C). Forked
arms: **fm** (main continued), **mm** (main against main), **fn** (+ 1e-5 C after the fork only), **fn2** (+ 2e-5 C
after the fork only). Draws: round1 section 6's six (main's coldest by hard-window land ice). 6 spins + 19
continuations + 1 candidate spin (~16 run-equivalents). Tables: session scratchpad `l144/val.txt`, `l144/diverge.txt`,
`l144/hb_*.txt` (tools `l144/tools/val.py`, `diverge.py`).

### 2a. The fork is exact
- **fm = main, bit for bit, on all 6 draws**: every step record and every climate-update record of the forked main
  continuation equals lane 140's unforked main run (`steps` and `updates` lists compared whole). so hard_bar
  gives lane 140's main rows (5/6 soft pass, 0 frozen).
- **mm = fm** (main forked against main, 1 draw, r0.0005 l6fix 957317): identical records; pjudge m vs mm: every
  paired difference +0.000, passes 1/1 both. `fork.py yard` with the candidate's own spin (same code): dy +0.0000.
- `tests/test_fork_judge.py` (L4, 28 Myr, fork at 16 with REF_FREEZE patched to 16): a forked run with the same code
  equals the unforked `ice_diag` run, and a `--set` after the fork leaves the spin-up records and the frozen
  references unchanged.
- In the forked nulls, y = ln(source ref / sink ref) from the late records differs from fm's by 0.0000 on all 12
  (the unforked nulls: -0.30 to +0.15). The yardstick is shared exactly.

### 2b. Does the land-ice swing shrink? No
Hard-window peak land ice (max over 884-1000 Myr, as lane 140d's `six.py`; the hard window is 884-1000 on all six),
%, and late (600-1000 Myr) dT difference against the arm's own main:

| draw | main = fm | null | null2 | **fn** | **fn2** | late dT null / null2 | late dT **fn / fn2** |
|---|---|---|---|---|---|---|---|
| r0.0005 l6c_0 819014 | 33.5 | 15.4 | 21.4 | **11.5** | **15.3** | +4.66 / +1.83 | **+2.30 / +4.39** |
| r0.001 l6c_p 957317 | 19.7 | 16.7 | 7.1 | **24.2** | **43.0** | +0.40 / +4.52 | **+1.35 / -1.77** |
| r0.001 l6c_0 819014 | 32.3 | 5.7 | 38.6 | **16.7** | **40.5** | +7.50 / +3.66 | **+4.93 / +3.91** |
| r0.001 l6c_0 53669 | 28.6 | 24.6 | 21.8 | **24.3** | **32.0** | -2.26 / -2.16 | **-0.49 / -1.74** |
| r0.0005 l6fix 957317 | 25.9 | 9.4 | 24.1 | **9.0** | **30.0** | +1.99 / +0.38 | **+0.06 / +1.82** |
| r0.001 l6fix 957317 | 24.7 | 22.0 | 20.2 | **21.4** | **29.3** | +0.01 / +0.22 | **+1.27 / -2.73** |
| \|swing\| mean (median), range | | 11.8 (10.2), 2.7-26.6 | 7.3 (6.5), 1.7-12.6 | **11.1 (10.1), 3.4-22.0** | **10.3 (6.4), 3.5-23.3** | rms 3.81 / 2.65 C | **rms 2.35 / 2.93 C** |
| pooled, 12 pairs | | **9.6 (6.5)**, late dT rms 3.28 C | | **10.7 (6.4)**, late dT rms 2.66 C | | | |

tools/hard_bar.py per arm: main 5/6 soft pass, 0 frozen; fn 5/6, 0 frozen; **fn2 3/6, 2 HARD frozen over in the
window** (r0.001 l6c_p 957317, pkIce 44.6; r0.001 l6c_0 819014, 41.1). Lane 140c/d's unforked nulls: 0 of 12.

- **The land-ice swing does not shrink.** Against lane 140c's unforked null (3-27 points) the forked nulls swing the
  hard-window peak by 3-23 points (mean 10.7 against 9.6 pooled; medians 6.4 and 6.5). With 12 pairs a side, no
  difference either way is resolved.
- **Late dT shrinks a little.** rms paired late-dT difference 3.28 -> 2.66 C (-19%; small n). That is roughly the
  yardstick's part (lane 140d: 1.5 C per draw of the 1.7 C within-seed sd, over all 36 draws); on these cold draws
  the rest is larger than on the average draw.
- **Why: the chaos after the fork saturates within ~200-300 Myr.** rms dT difference fork pair vs unforked pair, by
  era (`diverge.txt`): 310-350 Myr 0.0 vs 2.0-2.2 C; 350-400 0.4-0.6 vs 2.2-3.1; 400-500 1.4-2.0 vs 3.3-3.7; 500-600 3.6-4.5
  vs 4.5-5.0; 884-1000 3.9-4.8 vs 3.9-5.1. Land ice |difference| in the hard window: 9.7-10.5 vs 8.0-12.4 points. A
  1e-5 C nudge at 300 Myr has grown to the full spread by ~600 Myr, long before the window opens at 884: the window's
  ice is set by when the glacial eras fall (round1 section 6), which the fork does not share.
- **What the fork does remove is the yardstick's bias on selected draws.** These six were picked as main's coldest,
  and main is cold on them partly because their yardstick drew high (lane 140d: main's 8 coldest have y 1.46 against
  1.32 for all 36). Unforked re-rolls redraw y and come back warmer on 11 of 12 (regression to the mean); forked
  re-rolls keep y and come back warmer on only 6 of 12 (fn 5, fn2 1). So for a targeted screen on selected cold draws,
  the fork compares like with like, where the unforked nulls of round1 sections 7a and 8b set a warm-biased baseline.

## 3. What it measures and what it does not
- **Measures:** what the change does to a planet from 300 Myr on, given main's 300 Myr planet: the same geography,
  carbon stock, ice, plants and the same frozen references. The pass definition, hard bar, thresholds and windows
  are the existing ones, read by the existing tools.
- **Misses the change's effect on the yardstick itself**, and on anything else in the first 300 Myr. A change that
  alters what the spin-up learns (e.g. PW-1261's herb respiration lowers the reference plants' factor, `w_pot`, by
  ~1.2%; round1 8b) is judged as if it did not. Report that separately, as lane 140d did: run the arms with
  `CAND_SPIN=1` (each candidate draw also spun to 300 Myr with its own code, ~0.25 run more) and
  `fork.py yard OUT_ROOT fork fork_cand`, which lists per draw the frozen references' ln source and ln sink, y = ln(src
  ref / sink ref) and the spin-up's `w_pot`, candidate minus main. Translate dy with lane 140d's within-seed slopes
  (late dT -10.7 C per unit of y; hard-window peak land ice +35 points per unit of y over the 36 draws; herb-roots
  round1 8a), as an order of magnitude next to the forked judge's result, not as a pass/fail.
- **A change that adds simulation state** (a new name in `Simulation.STATE`) cannot be continued from main's state
  as is: `fork.py cont` stops with the missing names. `--fill-missing` (in `fork.py`, not passed by the script) takes
  them from a fresh simulation's t=0 values, which is a judgement per case. A change to the state's own classes
  (`Plates`, events) that breaks unpickling stops the same way.
- **The fork at 300 Myr is a step change for the candidate**: its first steps start from main's ice, plants and
  climate fields. For a change in a slow store this is a transient of order its own response time, inside the
  700 Myr that follow.

## 4. For Daniel's choice (draft `draft-fork-judge-adopt.md`)
- The fork does what lane 140d's option B said for the yardstick: exact, cheaper than paired.sh (1.7 runs per draw,
  1.0 with an existing main arm), and it removes the re-roll's warm bias on selected cold draws.
- It does not make the hard bar on main's cold tail less of a coin toss. A do-nothing change, forked, failed the hard
  bar on 2 of these 6 draws; unforked do-nothing changes failed 0 of 12. With main's coldest draws 4-7 points under
  the 40% line and post-fork swings of 3-23 points, either harness reads chaos there. Adopting the fork would not by
  itself have changed PW-1261's verdict.
- Where it helps most: continuous measures (late dT ~19% narrower on these six; more expected on ordinary draws, where
  the yardstick is a larger part of the spread, not measured here) and targeted screens on selected draws.
