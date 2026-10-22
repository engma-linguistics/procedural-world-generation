# Base-climate lane B: handoff (stage 2, the CO2 stock), 2026-10-22

Branch `worktree-agent-adf7ab7eab37416aa`, merged with main at 2684f2b. **Nothing is committed yet.** The working
tree holds attempt 3 of the stock. Read `thermostat.md` section "Stage 2" first.

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

## Deciding on attempt 3 (the stage's last attempt)
- **Merge-ready if:**
  - the trends-out CO2 answer has a median ≥ ~0.35 and the term runs against drift-made dT on ≥ 8/10;
  - the deep eras end: N1 fails on ≤ 2 seeds.

  N3 (the share) is expected to fail. That is PW-559's job, the next stage.
  Then: update the golden, run scorecard and health, fill the attempt 3 column in thermostat.md, and commit with the
  owner's identity and trailers.
- **If it doesn't pass:** attempt 1's code (REF_FREEZE alone, no relief term) is the cleanest "set once" stock, and
  its thermostat passes; its deep eras come from the relief spin-up (the inbox draft). Write a needs-decision draft:
  - A: attempt 1 + fix the start's relief (surface lane);
  - B: attempt 3's relief term;
  - C: attempt 2's settling freeze.

## Next stages
- **PW-559 (set point).** Every attempt leaves the icehouse share at a median of 58-66%, with only 1-3 seeds in
  15-45%. dT = 0 is today's icehouse Earth, and the kept balance holds the planet there. A planet-relative set point
  could sit the reference balance a planet-derived margin above its own icehouse threshold: the dT at which its land
  ice reaches 20 m, measured on its own geography during the spin-up. Watch for metric-chasing: the margin needs a
  physical reason, not the 25% share.
- **PW-564 (brightening), last.** With a kept reference, brightening is now absorbed only through the sink's
  temperature factor (no relearning), so check the CO2 index trends down over 2 Gyr.
