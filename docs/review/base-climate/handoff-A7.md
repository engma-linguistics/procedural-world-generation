# Lane A handoff A7 (2026-10-22, ~95 tool calls)

## State of the branch
- Main 5c4c0fd is merged in.
- PW-582 attempt 1 is committed on this branch (stages.md, "PW-582"). It is **not merge-ready**:
  - `test_store::test_run_lakes` fails unchanged. It is a chaotic L4 lake count (`draft-run-lakes-test-chaotic.md`,
    needs-decision).
  - The scorecard was not run.
  - The bar is not met: Fennoscandia is −7.9 against ±6, the Barents is still frozen, and Iceland is −10.3 against
    −7.8.
  - The Nordic Seas improve −8.3 → −4.2, and the Norwegian coast's sea air −0.7 → +2.0.
- Steps 2 (PW-579) and 3 (stage 3) are not started in code. The handoff-A6 notes for both still stand.

## Tools (in `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA7/`)
- `nordic.py` / `nr.sh "fields|..." variant...`: lat-lon maps (64–82N, 30W–66E by default) of the overturning's
  share, sinking, ice lid, January SST, coldest-month bias, winter density, salinity and currents. Each takes ~10 s.
- `probe.py` / `pr.sh out variant...`: A6's Earth probe, pointed at this worktree.
- `meas.sh tag`: pytest, earth_check, climate_bias and the 9-world overturning report, in parallel, into `laneA7/`.
- `melt.py`: the numbers of `test_meltwater_weakens_the_overturning`.
- `tz.sh plugin`: the two time-zoom tests.
- `lakes.py`: `test_run_lakes`' lake count over 60 steps.
- `plug/mp_*.py`: pytest plugins that switch one part off.
- `exp_pw582.diff`: the experiment switches, including Knudsen's exchange and the thermal wind.

## PW-582, next attempt
The lock: the inflow is routed only to sinking cells, and the Barents is too fresh to sink, so it is never fed.
Options are in `draft-barents-still-frozen-after-pw582.md`. The most physical is the inflow's salinity relaxing
toward the water it passes, as its temperature does. Today `_along` with rate 0 does no lateral mixing, so the Nordic
inflow reaches 35.6–36.1 psu against ~35.2. That would narrow the Barents' density gap, but it weakens every site, so
re-check the stage-1 bars and the time-zoom tests.

## Step 2 (PW-579) and step 3
Unchanged from `handoff-A6.md`. Watch the two time-zoom tests: they react to any change in the overturning's routing,
as Knudsen's exchange showed.
