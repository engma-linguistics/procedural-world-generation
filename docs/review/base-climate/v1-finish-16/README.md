# v1-finish-16: the finished world at a human-habitable moment (PW-866), 2026-10-26

Status: **code committed (7657fb9). Measurement partial**: 8 of 26 draws finished. The other 18 died or never
started: they stopped with no error in the log, so something outside killed them, not a crash.

## Mechanism
- `Params.finish_window = 10` Myr and `finish_step = 0.5` Myr. `Simulation.step_length` makes the run's last 10 Myr
  0.5 Myr steps. Each of those steps gets a climate update (`earth.climate_due`) and a keyframe
  (`timeline.simulate`, which now keys frames on time, not step count). That gives 20 candidates, 21 counting
  the 2 Myr step at the window's start. `sim.dt_now` is the step's length; `sim.dt` is the run's 2 Myr step.
- **Bug found and fixed on the way.** The carbon cycle's per-step amounts are new ocean floor, plume melt and the
  weathering supply. They are now counted per 2 Myr step, the unit the references are learnt in. Without this the
  0.5 Myr steps warmed the end: the L4 forest-to-tundra multi-seed test went from 16/17 to 0/2 eligible. After
  the fix, re-rolled seeds 1-48 give 16/17 and 18/18, the same as main.
- Frame stats now carry `true_temp_c`, `iced_land_pct` and `wet_eq_trees_pct` (`output.habitability`; the diag
  steps record them too). `highlights.finish_moment` takes the latest candidate that passes the existing finish
  checks: true mean -6..+3 C of 13.8, land ice 1-25% at that moment, wet-tropics trees >= 20%. If none passes,
  it takes the end and flags it ("NO human-habitable moment ..."). The result is stored in `run.json`
  `meta.finish_moment` (t, before_end_myr, passes, candidates, passing, fails_at_end, why).
- Who reads it: `--at auto` and `make`. The time zoom (300 kyr, interglacial) starts from the chosen moment's
  keyframe. `slice` snaps to the finish window's keyframes; the replay matches the stored keyframe (checked at
  L4). The viewer opens a run at its finish moment, with a "Finish moment" line giving the reason and a link to
  jump there.
- Cost: about 15 more steps and 20 more climate updates per run (~+8%).

## Measures (prefix `fm`; L6/L7 1 Gyr; `fmtally.py`)
| draw | bar | end: all checks | moment | look-back (Myr) | candidates skipped |
|---|---|---|---|---|---|
| L6 l6fix 957317 | ok | yes | yes | 0 | 0 |
| L7 d1 583167 | ok | yes | yes | 0 | 0 |
| L7 d1 619496 | ok | no (T +3.8) | yes (T +2.9) | 5.5 | 11, too warm |
| L7 d1 639472 | ok | yes | yes | 0 | 0 |
| L7 d1 957317 | ok | no (T +3.0) | yes | 0.5 | 1, too warm |
| L7 d2 583167 | ok | yes | yes | 0 | 0 |
| L7 d2 619496 | ok | yes | yes | 0 | 0 |
| L7 d2 957317 | ICEBOX | yes | yes | 0 | 0 |

- L7 (7 of 8 draws): bar 6/7, bar + checks at the end 4/7, **bar + checks at the moment 6/7**. Every draw had a
  passing moment.
- L6: only 1 of 18 draws finished, so no rate.
- Main had: L6 bar 16/18 and all checks 12/18; L7 bar 7/8 and all checks 4/8.
- Every skipped candidate was skipped as too warm. No draw needed the end fallback.

## To resume
- Outputs are in the session scratchpad: `v1f16/fm_*`.
- Delete the `log_<seed>.txt` of every draw that has no `seed*.json.gz`. The launcher skips any draw with a log.
- Then run `nohup docs/review/base-climate/v1-finish-16/launch.sh fm &`. It allows up to 8 simulations at once
  and needs 40 GB free before each launch.
- Tally with `uv run python docs/review/base-climate/v1-finish-16/fmtally.py <V>/fm_*`.
- Not done yet: `tools/scorecard.py` and `tools/earth_check.py`, and committing the scorecard line.
