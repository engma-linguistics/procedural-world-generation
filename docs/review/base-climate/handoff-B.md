# Base-climate lane B: handoff (stage 2, the CO2 stock), 2026-10-22

Branch `worktree-agent-adf7ab7eab37416aa`, merged with main at 2684f2b. Attempt 3 of the stock is committed (WIP fb04857 plus the results commit). Read `thermostat.md` section "Stage 2" first.

## State
- Code (uncommitted):
  - `planet/tectonics/earth.py`: `co2_stock`, `co2_term`, CO2_MAX 6 (tanh), CO2_TAU 0.4, REF_MYR 100, REF_FREEZE
    300, RELIEF_MYR 200; no 10 Myr smoothing.
  - `simulation.py`: the `ref_rate` state.
  - `diag.py`: `relief` per step.
  - `tools/ice_diag.py`: `co2_hp`/`fb_hp`, the trends-out gain; band 0.35-0.9; the deep eras are printed again.
  - `tools/health.py`: the co2 envelope text.
  - `tests/test_co2_stock.py`.
  - inbox draft `draft-relief-spinup-erosion-rise.md`.
- Tests: only `test_golden.py::test_golden_sim` fails, as expected (outputs changed on purpose). Before
  committing, run `uv run pytest tests/test_golden.py --update-golden`.
- **Attempt 3's sweep was paused (SIGSTOP by the coordinator) mid-run.** Output:
  `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneB2/stock3/`.
  - The sweep script writes `summary.txt` when all 10 seeds finish.
  - Then tabulate:
    `uv run python <scratch>/laneB2/summ.py <scratch>/laneB2/stock3`
    `uv run python <scratch>/laneB2/tab.py <scratch>/laneB2/stock3`
  - Other result dirs: `base/` (main), `stock1/`, `stock2/` (attempts 1 and 2), `g2/` (2 Gyr, seeds 5 and 13, on
    attempt 1's code).
- Not yet run: `tools/scorecard.py`, `tools/health.py` on the sweep, the commit.

## Attempt 3's result (sweep finished after the pause; committed)

| seed | N1-N4 | icehouse % | deep longest Myr | CO2 answer C/C | sink fb | mean dT |
|---|---|---|---|---|---|---|
| 1 | ok | 37 | 100 | +0.10 | 0.30 | +0.6 |
| 2 | ok | 49 | 68 | +0.14 | 0.34 | −0.3 |
| 5 | ok | 14 | 0 | −0.01 | 0.48 | +2.6 |
| 7 | F (share 2%) | 2 | 0 | +0.41 | 0.68 | +5.4 |
| 11 | ok | 34 | 0 | +0.58 | 0.60 | +1.2 |
| 13 | ok | 39 | 40 | +0.21 | 0.21 | +0.2 |
| 21 | ok | 8 | 0 | +0.50 | 0.01 | +4.0 |
| 42 | F (icehouse 304 Myr) | 47 | 128 | −0.07 | 0.31 | +0.1 |
| 99 | ok | 37 | 0 | +0.77 | 1.06 | +0.5 |
| 3199 | ok | 33 | 0 | +0.39 | 1.16 | +2.2 |
| **median** | **8/10** | **35** (5 in 15-45) | | +0.30 (trends out +0.28; 3/10 in band) | 0.41 | +0.9 |

(The per-seed CO2 answer here is with the trends in; the summary's trends-out median is +0.28. Against drift-made
dT: 10/10.)

What the next agent does:
1. Golden update, scorecard and health on `laneB2/stock3`.
2. Then the merge.

The owner should see:
- the relief term departs from "set once";
- the thermostat sits at ~0.3 C/C, a little under "close enough";
- the share bar holds on 5/10 seeds (the bar asks ~7/10), with three planets too warm.

PW-559 now looks like it needs, if anything, a *spread* fix rather than a warmer set point; measure it before
building one.

## Next stages
- **PW-559 (set point).** Every attempt leaves the icehouse share at a median of 58-66%, with only 1-3 seeds in
  15-45%. dT = 0 is today's icehouse Earth, and the kept balance holds the planet there. A planet-relative set point
  could sit the reference balance a planet-derived margin above its own icehouse threshold: the dT at which its land
  ice reaches 20 m, measured on its own geography during the spin-up. Watch for metric-chasing: the margin needs a
  physical reason, not the 25% share.
- **PW-564 (brightening), last.** With a kept reference, brightening is now absorbed only through the sink's
  temperature factor (no relearning), so check the CO2 index trends down over 2 Gyr.
