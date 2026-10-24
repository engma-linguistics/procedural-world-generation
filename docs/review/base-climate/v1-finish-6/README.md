# v1-finish-6: PW-750, options B, D (and C, measured) against the owner's icehouse bar (2026-10-24)

Branch `worktree-agent-a887b48c43cf726e8`, from main 3b7eb40 (run physics identical to v1-finish-5's PW-741 code:
nothing under `planet/tectonics` changed since 04b9fff). **No model change merged**: none of the options reaches the bar.

## Numbers first (L6, 1 Gyr, judged on 300-1000 Myr, the same 18 seed-draws as v1-finish-5)

8 seeds (957317 619496 583167 639472 53669 733847 819014 958504), draws = climate_offset 0 / -0.001 / +0.001 exactly as
v1-finish-5 (`launch*.sh`); the 4 showcase seeds are among them (`l6fix` = showcase seeds, offset 0). Bar: icehouse
share <= 40%, no always-icebox, no hellhole (`passrate.py`, v1-finish-3's, plus reporting-only never-ice (< 5%) and
median dT columns). Per-seed lines in `passrate_*.txt`; `agg.txt` the share distribution.

| option | pass | icehouse median | early / late (300-500 / 600-1000) | always-icebox | never-ice | hellhole | dT median | deep ice (mean % of updates < -150 m) |
|---|---|---|---|---|---|---|---|---|
| base (PW-741, drift 3 C; v1-finish-5's runs) | 5/18 (28%) | 46% | 24 / 57 | 2 | 0 | 0 | +1.1 | 12% |
| **B**: climate_drift 2 C | 9/18 (50%) | 46% | 31 / 65 | 2 | 0 | 0 | +1.5 | **17%** |
| **D**: source reference = its running mean since 100 Myr | 8/18 (44%) | 46% | 15 / 57 | 1 | 0 | 0 | +1.6 | 10% |
| D + B | 7/18 (39%) | 47% | 24 / 59 | 2 | 0 | 0 | +1.6 | 10% |
| probe: climate_offset +1.5 C (not a fix) | 10/18 (56%) | 36% | 2 / 54 | 0 | 0 | 0 | +2.3 | 8% |
| C (measurement): star +0.9%/100 Myr | 17/18 | 1% | 0 / 0 | 0 | **16** | 1 | +7.4 | 0% |
| C + B | 18/18 | 0% | 0 / 0 | 0 | **15** | 0 | +7.6 | 0% |

Showcase seeds (offset 0), icehouse %: base 45/10/11/82 (957317/619496/583167/639472), B 36/65/82/86, D and D+B see
`passrate_D.txt`, `passrate_DB.txt`.

## B: narrower drift reshuffles the draws, it doesn't move the climate

The drift is an OU wander with mean 0, so narrowing it can't change the mean climate, only the excursions; the
pass count 5 -> 9 is within the draws' noise (18 draws: sd ~11 points; only 2 of B's 9 passes are base passes, Fisher
p ~0.3). The icehouse median stays 46%, and B has **more** deep ice, not less (17% of updates below -150 m against
12%; runs with >= 20% deep: 8 against 5): with smaller warm excursions a planet near its ice threshold escapes an
icehouse less often. PW-368's expectation (fewer deep icehouses) does not hold after PW-576's CO2 stock. Lean: don't
apply B (it is the PW-240 decision, so the coordinator's call; draft below).

## D: the frozen reference is not a breakup-time high

The premise for D was that the 200-300 Myr reference sits above the source's long-run level. Measured (`dref.py`,
8 base runs; ln of source / reference over 300-1000 Myr): -0.04 median as run; -0.06 against the source's running
mean since 100 Myr, -0.08 since 0. So the window is ~4% above the long run at most, and any causal long-run mean
is *lower* (the young planet's first 100-200 Myr outgas more): D's reference warms nothing (steady-state estimate
-0.25 C), as the runs confirm (`d_run.py`: monkeypatched, causal, past steps only; median 46%). The only references
that warm are ones that keep relearning (an exponential mean over 300-500 Myr: +0.6 / +1.7 C), which PW-576 dropped
because they forget real lasting changes. No physically argued D exists that helps.

## Where the ice comes from: a late trend, not the mean

Every config without C has the same shape: early (300-500) 15-31%, late (600-1000) 54-65%. A uniform warming (the
+1.5 C probe; dT median +1.1 -> +2.3) empties the early window (2%) and
leaves the late one at 54%: 56% pass, still short. The late cooling is v1-finish-2's PW-708 finding: the weathering
supply rises ~12-20% as relief builds and the flora arrives (by design), counted against the reference frozen at
300 Myr. So a fix needs a warming *trend*, which is what C is.

## C (measurement only, not merged): the physical rate overshoots to ice-free worlds

`c_run.py`: luminosity +0.9% per 100 Myr from the run's start (Sun-like star today), forcing 238 W/m2 x dL/L at
~0.6 C per W/m2 (PW-564's estimate): +1.3 C per 100 Myr into the temperature's target. The model's thermostat lets
about half of a sustained forcing through (steady state X^0.4 exp(0.09 dT) = const: CO2 answers -0.97 C per C), so
by 600-1000 Myr dT is +7.4: 16/18 never-ice, N1-N4 2/18. Fails the other half of the bar. A star as young as the
planet brightens a bit slower (Gough 1981: ~0.67%/100 Myr over the first Gyr, `YOUNG=1` in c_run.py, not run) —
still +9.5 C raw by 1 Gyr, so it would overshoot too. C as a v1 fix would mean either a much weaker star or a
stronger thermostat: a design question for PW-564, not a number to pick here.

## Not done (deliberately)

- No change to `planet/`: no goldens, no pytest (only docs under `docs/review/` and an inbox draft), no scorecard or
  earth_check (nothing they measure changed).
- No showcase remake (no option passed); old showcase untouched.
- No L7 confirmation (nothing to confirm).

Scripts here (`launch.sh` B; `launch_d.sh` + `d_run.py` D; `launch_c.sh` + `c_run.py` C; `launch_o.sh` the offset
probe; `passrate.py`, `agg.py`, `terms.py` the temperature's parts, `dref.py` D's offline estimate). Raw outputs in
the session scratchpad `v1f6/` (B, D, DB, C, CB, O15).
