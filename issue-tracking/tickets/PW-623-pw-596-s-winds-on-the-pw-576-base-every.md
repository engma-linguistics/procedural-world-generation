---
id: PW-623
title: "PW-596's winds on the PW-576 base: every Earth bar better and the time zoom's glacial passes, but the cold-moment fixture's first plausible seed is now a hothouse moment (0.86% under sheets < 1%; ice speeds median 117 > 100 m/yr). No ice rule leans on the old winds"
type: task
status: done
parent: PW-470
milestone: v2
subsystem: timezoom
effort: s
impact: high
found_by: base-climate-laneA16
blocked_by: []
relates: [PW-596, PW-576, PW-569, PW-471, PW-366, PW-418]
refs: [planet/climate.py, tests/test_timezoom_consistency.py, docs/review/base-climate/laneA16/, docs/review/base-climate/stages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane A15 (branch `worktree-agent-a2d94046b3c8a7056`) added the seasonal westerly belts (`westerly_belt`) and the
column-deep thermal lows (`low_column`) to `planet/climate.py`. Lane A16 merged them onto main 2180b8e (PW-576: mature
start, CO2 stock, 1 Gyr default) and re-measured.

**What changed with PW-576's base:**
- The Earth bars are as A15 measured them (same code; earth_check, climate_bias and the overturning are byte-identical
  except the timings): rain r 0.620 -> 0.631, Köppen group 70 -> 71, Fennoscandia coldest -4.5 -> -2.8, stage 1
  holds.
- `test_glacials_grow_ice_and_endings_melt_it_fast` **passes**. Glacial extra / left after 15 kyr in m (bar: left <
  extra / 2):

  | source | main's climate | the branch's climate |
  |---|---|---|
  | main's world | 93.0 / 15.3 | 90.5 / 18.6 |
  | the branch's world | 37.9 / 1.8 | 49.9 / -0.5 |

- `tools/health.py --quick` on the branch is no worse than main's own on 2180b8e:
  - outlier spells 80 -> 60;
  - seeds with ice sea level below -150 m for more than 10% of the run 2 -> 0;
  - plate-collapse spells 1 -> 0;
  - giant-lake seeds (more than 5% of frames) 6 -> 3.
  - Two numbers go the other way:
    - the new ice bar (icehouse share 5-70%) fails on 3 -> 5 seeds;
    - the median seed spends 21 -> 34% of the run in an icehouse.
- Still red (assertions unchanged):
  - `test_cold_moment_has_sheets`: 0.86% of cells under more than 1 m of ice (bar > 1%);
  - newly, `test_ice_speeds_plausible`: median sheet speed 117 m/yr (bar < 100). Both are on the same fixture.

**No ice rule leans on the old winds.** The run's ice rule (`_cold`: 4 C colder, 6 climate updates) gives the
same sheets on the same world with either climate:

| world (seed) | main's climate | the branch's |
|---|---|---|
| main 28 | 2.09% | 2.10% |
| main 32 | 1.38% | 1.39% |
| main 31 | 0.46% | 0.46% |
| branch 31 | 0.74% | 0.86% |
| branch 34 | 0.94% | 0.83% |

With the belts or the column switched off, the result moves by at most 0.25 points (`xcold.txt`).

**The cause is the fixture's seed lottery, which main also wins only by luck:**
- The 300 Myr L5 runs are chaotic, so the branch's winds give other worlds.
- The fixture takes the first of seeds 25-35 that meets `_plausible`:
  - on the branch that is seed 31 alone, a hothouse moment (run dT +6.66 C) that 4 C of cooling leaves at 0.86%;
  - main's seed 31 is the same kind (+8.0 C, 0.46%); main passes because seed 28 comes first.
- Over seeds 25-50, how many plausible seeds have more than 1% under sheets:
  - main: 3 of 6;
  - branch: 2 of 7.
- The branch's first plausible seed with sheets is 46 (3.20%). With SEEDS = (46,), all three cold-moment tests pass
  on the branch: sheets, ice speeds, ice at index zero.
- Widening the window with the assertions unchanged doesn't help, because seed 31 stays first.

The fixture's comment already records that most plausible moments are warm ones with less than 1% under sheets.

Options:
- A (lean): **the fixture takes the first plausible seed whose cold moment has sheets.**
  - The precondition the drift and speed tests need is "an ordinary cold moment with sheets". The 1% bar moves from
    an assertion on whichever seed comes first into the selection.
  - `test_cold_moment_has_sheets` then asserts that the window has such a seed: SEEDS 25-50, the branch gets 46.
  - This is a change to what the assertion means, so it is the owner's call.
  - Merge PW-596 with it. main stays green, and the fixture no longer flips on any run-physics change.
- B: add a precondition "not a hothouse" (for example, the run's dT within a few C of the planet's mean). This needs
  a new threshold.
- C: hold PW-596 until a run-physics change happens to put a plausible seed with sheets first. Not recommended: that is a
  lottery, and every run-physics lane will meet it.
- D: merge with the two tests red, and fix the fixture next. This breaks "main stays green".

- [ ] rule A / B / C / D
- [ ] cold-moment tests green with PW-596 merged
- [ ] (follow-up) the branch's runs spend more time in an icehouse (median 21 -> 34%, ice-bar failures 3 -> 5) but
      none goes deep; check it on the 10-seed 1 Gyr bar when PW-559's set point lands

Coordinator (2026-10-23 night): held for the owner. Option A turns the 1% sheets assertion into a seed-choice condition, which is what lane B3 did and B4 reverted (it makes `test_cold_moment_has_sheets` true by construction), so it isn't a harness-only change. Coordinator lean: B with no new number — the fixture's "cold moment" must be colder than its own run's long-run mean (run dT at the moment below the run's median dT), since a +6.7 C hothouse moment isn't what a cold-moment fixture is meant to test; the sheets and ice-speed assertions stay as they are. Branch worktree-agent-a34e43ec48de2d53e (c0d5924) waits for the answer.

## Updates
- 2026-10-23: Status needs-decision -> done. Coordinator (2026-10-24): superseded: the cold-moment and endings fixtures are multi-seed with a pass-rate bar (PW-643, owner A) and eligibility by rule (PW-645); red single draws are no longer a merge decision.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Merged anyway on the A17 tree: there both cold-moment tests pass and main stays green with assertions unchanged. The fixture still passes or fails by which seed qualifies first; the owner's question (how the fixture should choose its source) stays open, together with PW-638 (PW-632 option B).
- 2026-10-23: Held branch is now worktree-agent-a22d5ce3841f99b73 (A16 winds + A17 island walls + A18 docs, head 5d12daf).
- 2026-10-23: The held branch is now worktree-agent-a6b65c5df0ddd0d62 (A16's winds + A17's PW-594 island walls, head 3e9855a); on that tree both cold-moment tests happen to pass (the seed lottery moved with the walls), so the fixture question stands.
- 2026-10-23: Created from inbox draft draft-pw596-winds-break-timezoom-ice-tests.md (found by base-climate-laneA16).
