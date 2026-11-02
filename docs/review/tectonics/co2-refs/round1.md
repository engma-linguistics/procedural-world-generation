# Lane 135: finished-frame orbit response (PW-1325), CO2 references over the whole spin-up (PW-1316), the spin-up audit

Main fc4e0398. Scratch: `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l135` (S below).

## 1. PW-1325 (owner: A). Done, committed separately

**In plain words:** a finished world used to add its moment's orbit to the months at the ice rule's 0.25 C per W/m2.
Now it uses each cell's seasonal response (`icemass.seasonal_k`, ~0.03 C per W/m2 in the tropics, 0.08-0.09 at mid
and high latitudes), whatever the time zoom's own rule. The time zoom's ice and the runs don't change.

- Code: `planet/finish.py::orbit_dt` forces `orbit_resp='seasons'` (one `dataclasses.replace`), and always builds the
  seasonal response from the frame's climate at the mean orbit (the branch that 'seasons' time zooms already used).
- What it touches: only `finish.orbit_dt`, called by `finish._finish` and `refine` (a finished world's regional zoom).
  Runs have no orbit_dt; the time zoom's own climate and ice use `forcing.orbit_anomaly` with their own `p` (unchanged);
  earth_check doesn't finish a frame. Goldens (`tests/test_golden.py`) pass unchanged. `finish_key` changes with the
  finishing code (provenance hash), so `api.find_slice` won't reuse a world finished under the old rule.
- Test: `tests/test_finish.py::test_finished_climate_has_the_orbit` now checks the anomaly equals the 'seasons' one
  although the fixture's time zoom is 'run', and that its mean size on bare land is under 0.6 of the run rule's.

dba204 (time zoom 56dee1, 202 kyr; orbit obliquity 22.43, eccentricity 0.0348, perihelion 90.7), re-solved on its
stored elevation and ice at the frame's dT with its plants ([pw1325_dba204.py](pw1325_dba204.py); 'before' reproduces
the stored world):

| ice-free land | stored | before (0.25 C per W/m2) | after (seasons) | no orbit |
|---|---|---|---|---|
| warmest month 0-20 deg (C) | 30.5 | 30.6 | **25.5** | 25.4 |
| 20-40 deg | 28.7 | 27.4 | 26.8 | 26.6 |
| 40-60 deg | 22.6 | 22.9 | 20.0 | 18.9 |
| land with warmest month >= 30 C | 45.4% | 45.0% | **15.5%** | 14.8% |
| land >= 35 C | 18.3% | 17.9% | 2.9% | 0.3% |
| mean July anomaly on 0-20 deg land | | 7.7 C | 1.1 C | 0 |

The diagnosis's ~45% -> ~19% was at dT 0.7; this re-solve uses the frame's own dT, hence 15.5%. The ticket's check
(0-20 deg within ~1 C of the no-orbit climate) holds: 25.5 against 25.4.

## 2. PW-1316 (owner: B, the references as the mean over the whole spin-up)

**Code** (uncommitted until the judge is read; frozen copies in `S/code/main` = 9f37de72 and `S/code/b` = that plus
the two files): `planet/tectonics/earth.py::global_temperature`, while t < REF_FREEZE, `refs += dt / ref_myr x (learn
- refs)` with `ref_myr` the Myr counted so far (new EARTH_STATE field, `planet/tectonics/simulation.py`), so at 300 Myr
each reference is the step-weighted mean of the whole 0-300 Myr spin-up. `REF_MYR` is gone. What is learnt (the source
without its drift; the sink at the balance climate with the potential plants) is unchanged.

### 2a. Lane 115's check: does end T still track the reference mismatch?

Harness [envref.py](envref.py) (envdraw.py's world: test_envelopes' L5, `Params(run_end=400)`, 0-100 Myr then 4 Myr
chunks), seeds 1-20 per arm, summarised by [envsum.py](envsum.py). "Late imbalance" is lane 115's measure: mean over
300-400 Myr of ln(src/src_ref) - ln(sink/sink_ref). "Source-ref mismatch": ln(src_ref / mean source over 300-400).

| arm | end T median | sd | range | out of band | corr(end T, late imbalance) | sd imbalance | corr(end T, src mismatch) | sd src mismatch |
|---|---|---|---|---|---|---|---|---|
| main (e-folding) | 15.3 | 1.86 | 13.2..19.1 | 0 | 0.56 | 0.087 | -0.24 | 0.153 |
| B (spin-up mean) | 14.8 | **4.02** | 8.5..24.1 | 0 | **0.91** | **0.163** | -0.58 | 0.120 |

- **On this world B is worse, not better.** The correlation doesn't drop, it rises (0.56 -> 0.91), and the imbalance
  and end-T spread double. The source's reference is a little closer to the source that follows (sd 0.153 -> 0.120),
  but the post-freeze imbalance, sink included, is wider.
- Why: this test judges the 100 Myr right after the freeze. Rates are persistent over ~100 Myr, so a reference that
  weights the spin-up's last 100 Myr is the better guess for 300-400 Myr; a 0-300 mean leaves the planet further from
  balance when the references freeze. (Main's own spread here, 1.9 C, is also smaller than lane 115's 3.2 C on older
  code, so main's frozen-reference trips are rarer now than in pw1295-note.md: 0 of 20 out of band, warmest 19.1 C.)
- The trajectories part from ~100 Myr (the references feed the spin-up's CO2), so this is 20 independent draws per
  arm, not paired runs. Variance ratio 4.7 on 20 v 20 (F-test p ~0.001, though B's tail is 4 draws: 8.5, 8.8, 12.1 and
  24.1 C).

### 2b. Offline: which spin-up average predicts the source a 1 Gyr run goes on to have?

[refpredict.py](refpredict.py) on 72 stored 1 Gyr L6 ice_diag draws (two arms of an older judge in the session
scratch, `scratchpad/judge/A_*` and `D_*`, 2026-10-29 code): the source's reference each way, from the logged raw
source, against the mean source over 300-400, 300-500 and 300-1000 Myr (ln(ref / later mean); median, sd over draws).

| predictor | 300-400 (A / D) | 300-500 | 300-1000 |
|---|---|---|---|
| main's e-folding | -0.12, sd 0.167 / -0.04, sd 0.131 | -0.02, 0.143 / -0.03, 0.116 | +0.03, **0.132** / +0.04, **0.105** |
| B: mean 0-300 | -0.17, 0.162 / -0.07, 0.132 | -0.07, 0.126 / -0.06, 0.114 | -0.03, **0.107** / -0.00, **0.086** |
| mean 100-300 | -0.20, 0.186 / -0.14, 0.142 | -0.13, 0.153 / -0.10, 0.127 | -0.06, 0.141 / -0.06, 0.114 |

- For the source, over the rest of a 1 Gyr run, B's reference is ~19% closer draw to draw (sd 0.13 -> 0.11 and 0.105
  -> 0.086 e-folds; at lane 80's ~11 C per e-fold, ~1.4 -> ~1.1 C of end-T scatter from the source's reference).
  Over the 100 Myr after the freeze it is no better, which is what 2a sees.
- The sink's learnt value (at the balance climate) isn't logged, so the sink half can't be checked offline. It is the
  L6 judge's job.

### 2c. L6 sanity and paired judge (running; see section 5 for the read-it recipe)

At hand-off (11:10, 2026-11-02): 3 of 72 draws done (main l6fix 957317 and 619496, b l6fix 957317), not yet read.
The 4 sanity seeds (l6fix r0.0005) are the first 8 draws; read them with pjudge.py as soon as all 8 are in.

## 3. Is the first ~500 Myr "in flux unlike the rest of the run"? (Daniel's worry; written alongside B)

### 3a. How big the spin-up's transients are, in the runs

[spinup.py](spinup.py) over 72 stored L6 1 Gyr ice_diag draws (`scratchpad/judge/A_*`, `D_*`, 2026-10-29 code, 36
draws each; the two arms agree to ~0.02, A shown). Each window's mean against the same draw's 300-1000 Myr mean
(ratio for the CO2 source and the weathering sink as counted; difference for the rest); median [10-90%] over draws.

| | 0-100 | 100-200 | 200-300 | 300-500 | 500-700 | 700-1000 |
|---|---|---|---|---|---|---|
| CO2 source (ridges + arcs + plumes) | 1.08 [0.97, 1.17] | **0.78** [0.66, 0.91] | 1.09 [0.87, 1.28] | 1.05 [0.94, 1.14] | 1.01 [0.91, 1.09] | 0.97 [0.89, 1.03] |
| weathering sink | **0.50** [0.40, 0.65] | 0.47 [0.39, 0.58] | 0.58 [0.47, 0.64] | 0.55 [0.51, 0.62] | 1.05 [0.94, 1.16] | 1.24 [1.17, 1.32] |
| land (points) | -1 | -1 | -1 | -1 | 0 | 0 |
| star forcing (C) | -9.3 | -7.9 | -6.4 | -4.2 | -1.1 | +3.2 |
| dT (C) | +0.7 [-2.0, 3.6] | -1.6 [-4.9, 1.3] | +1.2 [-2.1, 3.6] | +1.1 [-0.4, 2.8] | -0.5 [-3.0, 1.8] | -0.4 [-1.7, 1.2] |
| ln CO2 (e-folds) | +1.44 | +0.68 | +1.04 | +0.81 | +0.28 | -0.64 |

- Land plants arrive at 506 Myr median (502-530) and the sink steps up by +0.53 e-folds there (x1.7; 10-90% +0.48 to
  +0.60), then keeps rising as more groups come (x1.24 of the late mean by 700-1000).
- From the scorecard's two L6 1 Gyr worlds (docs/scorecard.jsonl, last entry fdc631a4, seeds 1 / 2): plate speed 7.5 /
  7.4 cm/yr at 100 Myr against 2.4-4.6 after; continental crust 36.3 / 36.7% at 200 Myr against 38-43%; largest
  landmass 31 / 34% at 200 Myr (the start's breakup, then a first reassembly), 6-31% after. Land stays 31-36% throughout.
- So yes, the first ~500 Myr are unlike the rest, in four ways, two of them large:
  1. **Bare land until ~506 Myr**: the sink runs at half its later rate and steps up x1.7 when plants come. This is
     designed for: the sink's reference is learnt with the potential plants at the balance climate (PW-809, v1-finish-11),
     so bare early land holds more CO2 (+1.4 to +0.8 e-folds of CO2 over 0-500 Myr) instead of being learnt as normal.
  2. **The faint young star**: -9 C of forcing at the start against the late mean, +12.5 C over the run, ~1.5 C per
     100 Myr. Also designed for (start_carbon, the end-anchored GEOCARB frame), and it is steady, not a transient.
  3. **The start's breakup and first reassembly (~100-250 Myr)**: fast plates at first, then a CO2 source lull to
     0.78x at 100-200 Myr on nearly every draw (10-90% 0.66-0.91), and a recovery to 1.09x at 200-300. This is the
     part the references see. Main's 100 Myr e-folding mostly forgets the lull; B's whole-spin-up mean includes it.
  4. The start's supercontinent itself (largest plate ~47% at t = 0, PW-969) and fast early plates.
- Land % and crust volume barely move (they're set at the start, thermostat.md). The sink's x0.5 before plants is the
  largest single swing in the carbon cycle over a run.

### 3b. How many past CO2 problems traced to the spin-up (survey of tickets and review notes)

32 distinct CO2 / thermostat / climate-drift episodes (PW-264 to PW-1332, a read-only sweep of issue-tracking/tickets,
docs/wiki/decisions.md and docs/review notes; not exhaustive over every v1-finish-N README):
- **Spin-up-rooted (10)**: references learnt on bare, low-relief or still-emerging ground, then a different regime
  later: PW-576 (relearning baselines lost ~30% of the thermostat; the old start's erosion at 0.18-0.26 of its late
  rate until ~150 Myr, thermostat.md), PW-612, PW-708 (runs icier after 500 Myr as weatherability rises against
  references frozen at 300), PW-798 / PW-799 (water world: references frozen while land still emerges), PW-809 / PW-890
  (the reference learnt the faint star and bare land), PW-980 (spin-up erodes ~20% more than the late run), PW-1163
  (sink reference learnt on bare-ground erosion, ~+1.6 C), PW-1316 / PW-1317 (a spin-up lull frozen in).
- **Partly (9)**: PW-264, PW-574, PW-636/657 (plants' arrival), PW-741/750 (the reference is the 200-300 Myr balance,
  "a breakup-time high"), PW-894, PW-895, PW-1158 (the late source decline is real tectonics, but measured against the
  0-300 Myr yardstick), PW-1161 (lane 80: red variance plus two cancelling biases, one of them spin-up), PW-1315.
- **Not spin-up (13)**: PW-368 (drift), PW-558 (clip), PW-559 (icy balance), PW-611, PW-806, PW-819, PW-865/891,
  PW-893 (drift double count), PW-1142 (ice), PW-1224 (a late assembly's CO2 crash), lane 67's per-step bug, PW-1332
  (grass NPP), PW-565/969 (late plate ageing).
- The spin-up has been the most common single root of the reference trouble, and most of the big fixes (mature
  start, end-anchored GEOCARB balance with potential plants, PW-576's stock) were spin-up fixes. The recent large
  incidents (PW-1224's crash, the finish spread, lane 67's bug, PW-1332) mostly were not.

### 3c. Verdict on the worry

- **Founded, with numbers, but mostly already designed around.** The first ~500 Myr really are different: bare land
  weathers at x0.5 until ~506 Myr then steps x1.7; the start's breakup gives a source lull to x0.78 at 100-200 Myr on
  almost every world; CO2 sits x2-4 above its late level to hold off the dim star. The two biggest (bare land, faint
  star) are handled by construction since v1-finish-10/11 (sink reference at potential plants and the balance climate;
  start_carbon). What leaks through: PW-1163 (~+1.6 C) and PW-1158's yardstick (~-1.6 C), which cancel, and the
  draw-to-draw scatter of the kept references (sd ~0.09-0.13 e-folds each, ~1-1.5 C at the loop's ~11 C per e-fold).
- **Is it why CO2 kept eating time?** Partly: a third of past episodes were spin-up reference problems, and a third
  more had it as a part. But the current spread (lane 80) is mostly genuine tectonic variance, and B's checks (section
  2) show averaging the spin-up differently trades one error for another rather than removing it.
- **Beyond B**: nothing urgent. The one mechanism-level option worth a decision is learning the sink's yardstick only
  once plants are established (draft-co2-references-spinup-unlike-the-run, option B), which would retire PW-1163's
  correction instead of adding another. A longer spin-up for everything (option C) isn't warranted: thermostat.md
  found judging after 500 Myr changes no verdict and halves the sample.

## 4. Tests

- PW-1325 commit (9f37de72): `uv run pytest -q -m "not slow"` 929 passed; the 4 thread tests failed only because that
  run forced NUMBA_NUM_THREADS=1, and pass at the default (with test_golden: 6 passed). Goldens unchanged.
- B: `tests/test_envelopes.py` (slow) 10 passed, 1 skipped (Earth data not in the worktree). Not-slow suite on B: see
  929 passed, 1 skipped (`-m "not slow"` at -n 3 with NUMBA_NUM_THREADS=1; the two thread-count test files deselected
  for that reason, B doesn't touch threading and they passed on 9f37de72). Golden `sim_L4_s1_60myr.json` updated in
  fe1e2849: the references differ from the first step, so every run's output changes.

## 5. State at hand-off, and the read-it recipe

S = `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l135`.

- Judge launched ~10:40 on 2026-11-02, detached: `S/launch.sh` (one queue for both arms, so at most 3 sims run at once;
  it reads the cap from `S/maxsim` each time a slot is wanted; 3 now, set to 2 while running tests). Arms: `S/code/main` (git archive 9f37de72) and `S/code/b` (the same plus B's earth.py and simulation.py),
  through `tools/ice_diag.py` (L6, 1 Gyr, star_brightening 1), v1-finish-16's 18 draws x rolls 0.0005, 0.001 into
  `S/judge/{main,b}_r<roll>_<tag>/`. The 4 sanity draws (l6fix r0.0005) go first. Log `S/launch.log`, ends "all done".
  ~30-40 min per run at 3 threads: expect ~12 h at 3 at once.
- **Never edit `S/launch.sh` while it runs** (bash reads it as it goes); kill its two PIDs (`ps -eo pid,args | grep
  "bash ./launch.sh"`), edit, relaunch with `cd S && nohup bash ./launch.sh > launch.log 2>&1 < /dev/null &` (it skips
  draws with a log or result). A draw that died has a log but no seed*.json.gz: delete the log and relaunch.
- To read: `ls S/judge/*/seed*.json.gz | wc -l` should be 72. Then
  `uv run python docs/review/base-climate/v1-finish-16/pjudge.py S/judge main b --table` and `tools/hard_bar.py` per arm
  (as pw1295-note.md section 3), plus `uv run python docs/review/tectonics/co2-refs/spinup.py "S/judge/main_r*/seed*_L6.json.gz"`
  (and b) to redo section 3a on current code, and refpredict.py on main's draws.
- Bar: hard failures 0; soft pass ~main's or better; no threshold change. Also look at the spread of end T and late dT
  (sd per arm): B's case rests on a smaller 1 Gyr spread; section 2a says it widens the 300-400 Myr one.
- Then: B commit stays on the branch either way; if it fails, the coordinator reverts it (three strikes: this is
  variant 1; no second variant tried, because 2a/2b point at a trade-off, not a tuning slip).
- After reading: delete S (`rm -rf "${S:?}"`; it has no symlinks).

## 5. PW-1316 B: the L6 paired judge (read by the coordinator, 2026-11-02)

L6, 1 Gyr, 2 rolls, 36 paired draws, main 9f37de72 (with the PW-1325 orbit fix) against b fe1e2849. `pjudge.py` and
`tools/hard_bar.py` per arm.

- **Hard failures:** 0 in both arms (frozen over, boiled, ocean loss, CO2 crash).
- **Soft passes:** b 28/36 against main 32/36. Both pass 26, main only 6, b only 2, neither 2; McNemar p 0.29, within
  chance but the wrong way.
- **Moved:**
  - trees -1.45 points [-3.19, -0.30];
  - sink ref -0.08 [-0.12, -0.02].
- **Not moved:** end T -0.88 [-2.44, +1.27], late dT, late CO2, arid, land rain.
- **What B was for, spread:** b is wider, not narrower.
  - End-T sd 3.59 against 3.28.
  - 7 draws end beyond +-5 C against 4.
  - 8-fold CO2 falls within 50 Myr: 26/36 against 18/36.
  - Frozen spells under the dim star (reported only): 2 against 0.

**Verdict: B fails.** It doesn't do what it was for (fewer runaway imbalances). The L5 check already showed this, and the
1 Gyr judge agrees. So fe1e2849 is not merged: strike 1 on PW-1316's reference averaging. Section 2b's offline result
stands: a mean over the whole spin-up includes the breakup lull and the bare-ground sink, so it trades one error for
another. The open mechanism-level option is the sink learnt over a planted window (the draft's B), which goes to Daniel.
