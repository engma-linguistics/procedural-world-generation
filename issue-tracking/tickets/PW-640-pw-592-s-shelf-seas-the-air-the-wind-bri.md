---
id: PW-640
title: "PW-592's shelf seas (the air the wind brings) is green on every Earth bar, but the run's chaos turns three fixture tests red: sim4 draws a colder world (run dT +5.10 -> +2.01) and the forest-to-tundra test's forcing goes +0.079 W/m2; the cold-moment fixture's first plausible seed becomes 29 (0.28% under sheets)"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: ocean
effort: s
impact: high
found_by: base-climate-laneA20
blocked_by: []
relates: [PW-592, PW-623, PW-627, PW-638, PW-450]
refs: [planet/climate.py, tests/test_timezoom.py, tests/test_timezoom_consistency.py, docs/review/base-climate/laneA20/, docs/review/base-climate/stages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane A20's commit (`_shelf_air`, see `docs/review/base-climate/stages.md`, lane A20) changes no assertion or fixture.
On Earth L6 it moves only shelf seas and the coasts downwind of them. The overturning on Earth and the 9 worlds is
identical. Rain r and the SH coastal range are unchanged.

`uv run pytest -q`: 593 pass and 3 fail. All three are on fixtures that are a chaotic run's draw.
- `test_glacial_cooling_turns_forest_to_tundra_and_cools_further` (sim4: L4, seed 1, 300 Myr). Its forcing is
  F = +0.079 W/m2 (bar < 0). Crossed by `laneA20/xforest.py`:

  | | main's climate | the branch's climate |
  |---|---|---|
  | main's world (run dT +5.10) | F -0.038, passes | F -0.023, passes |
  | the branch's world (run dT +2.01) | F +0.082, fails | F +0.079, fails |

  The world decides. The branch's climate on main's world passes; main's climate on the branch's world fails.
  The new world is a colder one: the class lane A18 found for the endings test. That test passes here.
- `test_cold_moment_has_sheets` and `test_ice_at_index_zero_is_the_runs`: the fixture's first plausible seed in
  25-35 is now 29, with 0.28% under sheets (bar > 1%) and a sea level change of 26.6 m (bar < 25). This is PW-623's
  seed lottery, which is with the owner.

Options:
- A (lean): merge with main red on these three. The mechanism is right and every Earth bar is better or the same.
  The forest test then waits on a fixture ruling of PW-623's kind: a source world chosen by a rule, not by outcome.
- B: hold the commit until PW-623 and PW-638 settle how the fixtures pick their worlds.
- [ ] A / B

Coordinator (2026-10-23 night): this is the third physics change tonight blocked only by chaotic single-world fixtures (PW-623 cold moment, PW-638 endings, now the forest-to-tundra forcing test). Each lane traced the flip to the run's chaos with a climate swap. Coordinator lean for one ruling covering all three: make these time-zoom/ice fixtures multi-seed with a pass-rate bar, in line with the owner's seed-pass rule (~70% of seeds pass), each seed's assertion unchanged; seeds and moments chosen by a fixed rule (not by outcome). Costs test time (a few L4 300 Myr runs, cached per session). Until then, held: branch worktree-agent-a2b66e784ed5186c3 (1d076ad, the shelf-air rule).

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Correction 2 (lane A21, 240 worlds via climate_offset +-0.001 C re-rolls): main passes the forest test 103/144 (72%), A20 63/96 (66%), ~1 SE apart; mean F identical (-0.054 vs -0.053). A20's 12/24 was the tail of the draw; its nudged draw passes every multi-seed bar except none. No physics side effect: the shelf-air rule is ready on the physics; merge waits only on the fixture ruling (PW-643). Under PW-643's 70%/24 bar main itself is red in 3 of 4 draws.
- 2026-10-23: Correction (multi-seed lane, PW-643): over 24 seeds the forest-to-tundra test fails on 12/24 worlds from A20's runs vs 4/24 on main (~0.7% by chance), and A20's climate on main's worlds gives main's numbers: so A20 changes what the runs make, a real multi-world signal, not one world's luck. The single-world climate swap couldn't show that. A20 stays held as a physics question (why do its runs' worlds force positive under forest loss?).
- 2026-10-23: Created from inbox draft draft-shelf-air-turns-sim4-fixtures-red.md (found by base-climate-laneA20).
