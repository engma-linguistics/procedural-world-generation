---
title: "PW-596's seasonal westerlies and column-deep thermal lows pass the Earth bars but break two time-zoom ice tests and deepen the runs' ice ages (glacial extra ice 71.8 -> 38.2 m, 15 kyr left 11.7 -> 21.2; cold-moment sheets 0.72% < 1%)"
type: task
status: needs-decision
parent: PW-470
milestone: v1
subsystem: timezoom
effort: m
impact: high
found_by: base-climate-laneA15
blocked_by: []
relates: [PW-596, PW-569, PW-439, PW-575, PW-026]
refs: [planet/climate.py, tests/test_timezoom_cycle.py, tests/test_timezoom_consistency.py, docs/review/base-climate/laneA15/, docs/review/base-climate/stages.md]
---

## Description
Lane A15 (branch `worktree-agent-a2d94046b3c8a7056`) changed two wind mechanisms in `planet/climate.py`:
- `westerly_belt`: each season's and hemisphere's westerlies scale with that season's zonal-mean poleward
  temperature contrast over 30-65 deg, relative to the planet's own mean of the four. On Earth the belts are
  N summer 0.75, N winter 1.17, S summer 0.91, S winter 1.17.
- `low_column`: a land's thermal lows and highs are as deep as the share of the air column its warmth fills,
  `sum_h / fetch_h + (1 - that) x the land within fetch_km`, the same rule as `_summer_fetch`.

On Earth L6 both pass their bars and improve the rest:
- log-rain r 0.620 -> 0.631; Köppen group / exact 70 / 32 -> 71 / 34;
- W Europe warmest -1.2 -> -0.9; Fennoscandia coldest -4.5 -> -2.8; Iceland coldest -3.7 -> -2.3;
- SH coastal range 12.4 -> 12.3; stage 1 holds (Earth NH 13.98 Sv, 90% open polar sea, Norwegian coast 100% open;
  all 9 worlds sink in both hemispheres).

`uv run pytest -q` then fails two time-zoom ice tests. The assertions are unchanged; the goldens were updated on
purpose:
- `test_glacials_grow_ice_and_endings_melt_it_fast` (glacial extra ice / ice left after 15 kyr, m; the bar is
  left < extra / 2):
  - main 71.8 / 11.7;
  - step 1 alone (belts) **8.5** / – (fails `extra > 10`);
  - steps 1+2 **38.2 / 21.2** (fails: 21.2 > 19.1).
- `test_cold_moment_has_sheets`: the share of cells under more than 1 m of ice at the cold moment is **0.72%**
  (bar > 1%). It passes on main and with step 1 alone.

`tools/health.py --quick` (8 L6 seeds, 500 Myr; `laneA15/health_before.md` / `health_after.md`) goes the other
way: the runs grow more ice.
- Outlier spells 54 -> 61.
- Seeds with ice sea level below -150 m for more than 10% of the run: 2 -> 5 (seed 77 0 -> 61%, 42 25 -> 49%,
  1 10 -> 29%, 21 0 -> 24%).
- New ice bar failures 5 -> 3 (seed 77 now icehouse 100%).
- Giant-lake frames: seed 1 0 -> 18%, 77 0 -> 14%.

Likely mechanism (time zoom): the NH summer westerlies are 25% weaker, so less of the sea's summer air reaches the continents
(`_summer_km`, U x sum_tau). Continental summers warm a little: Labrador warmest +3.2 -> +4.0 on Earth. The time
zoom's glacial ice sits at its summer-melt margin, so it loses most of its growth. Its rules were calibrated on the
old one-strength winds (the defaults are green; the honest rules were already red, PW-569 / PW-439).

Options:
- A (lean): merge the winds, which are physically right and pass their own bars, as a "global, not local, optimum".
  Then recalibrate or fix the time zoom's ice (PW-569) on the new winds before anything else in the ice lane.
  main is red on these two tests until then.
- B: keep the branch unmerged until the ice lane has a fix that keeps the two tests green on the new winds.
- C: merge step 2 alone (`low_column`, rain r 0.633 on its own). Needs its own pytest run; not measured on the
  time-zoom tests.

- [ ] rule A / B / C
- [ ] the two time-zoom tests green on the seasonal westerlies, assertions unchanged
