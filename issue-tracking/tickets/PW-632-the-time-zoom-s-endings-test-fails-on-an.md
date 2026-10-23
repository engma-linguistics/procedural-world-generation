---
id: PW-632
title: "The time zoom's endings test fails on any climate when sim4's run happens to end cold: on step 2 of PW-627 the L4 seed-1 world is colder (run dT 2.67 vs 5.10), and the endings leave 59% of the glacial's extra ice after 15 kyr; over seeds 1-9 both trees fail on their coldest worlds"
type: task
status: done
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: base-climate-laneA18
blocked_by: []
relates: [PW-627, PW-568, PW-588, PW-623, PW-471]
refs: [tests/test_timezoom_cycle.py, docs/review/base-climate/laneA18/, docs/review/base-climate/stages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`test_glacials_grow_ice_and_endings_melt_it_fast` (bar: extra > 10 m, left after 15 kyr < extra / 2) runs on sim4's
moment (L4, seed 1, 300 Myr) cooled by 4 C. On PW-627's step 2 it fails: extra / left 33.2 / 19.7 m.

**The world decides, not step 2's climate** (lane A16's crossing, `laneA18/xzoom_cross.txt`):

| extra / left (m) | step 1's climate | step 2's climate |
|---|---|---|
| step 1's world (run dT +5.10, 0.04% under ice) | 49.9 / -0.5, passes | 44.0 / -0.9, passes |
| step 2's world (run dT +2.67, 1.13% under ice) | 31.3 / 15.7, fails | 33.2 / 19.7, fails |

**The test fails on cold source worlds whatever the climate** (`laneA18/seedscan_2-9.txt`, each tree its own climate,
L4 300 Myr runs of seeds 1-9):
- step 1: passes 6 of 9; fails seed 5 (a hothouse, dT +12.3: extra 3.8 m < 10) and seeds 7 and 8, its two coldest
  (dT +0.75 / +1.37: left / extra 0.68 / 0.61);
- step 2: passes 7 of 9; fails seeds 1 and 8 (dT +2.67 / +0.79: 0.59 / 0.61);
- seeds 2 and 9 pass on both trees at dT 1.8-3.7. Every failure with enough ice is a cold world; most cold worlds
  fail.

So step 2 doesn't make the test fail more often (7 / 9 against 6 / 9); seed 1 moved from a warm world to a cold one by
the run's chaos. The test holds only when sim4's run ends warm, which is a lottery any run-physics change can lose.

**What holds the ice** (`laneA18/xflows_s{1,2}world.txt`, the index-on run's budget in 5 kyr windows, Gt/yr, both
on step 2's climate):
- warm world (step 1's, passes): at the ending ablation jumps 1890 -> 3352 and the NH net goes -234 / -935;
- cold world (step 2's, fails): ablation only 873 -> 890 -> 1206 -> 1611 over the 15 kyr, and the NH net stays
  positive (+1907 / +1639 / +1005): the sheets keep growing through the ending, and lose ice mainly by calving
  (~3300, against ~2000 in the no-index run).
So on a cold world the glacial's sheets stand above their equilibrium line even at I = 0, held by their own height
(PW-588's hysteresis): the 6 C the ending gives back doesn't bring their surfaces into ablation.
Whether that is a flaw (missing termination physics: isostatic lag, proglacial lakes, dust / albedo on the margins)
or right for a cold planet, where a glacial's ice need not melt in 15 kyr, is part of the decision.

**No harness-only change is legitimate here.** The fixture has no search window: the source is the session's sim4
(seed 1), shared with ~100 other tests. The options that keep the assertions:
- another seed for this module only: a pick by outcome, not a window that finds a suitable frame;
- a precondition such as "the source moment isn't already a deep icehouse": a new threshold, and it would hide what
  the failures show, that the zoom's endings leave too much ice on big, cold sheets (PW-568 / PW-588: the extra ice
  held poleward by the sheet's own height and albedo).

Options:
- A (lean): find why the zoom's endings leave over half of a cold world's extra ice after 15 kyr (the ice budget
  around the ending: `laneA18/xflows.py`), fix it, then merge PW-627's step 2. The bar to meet: the endings test on
  every seed 1-9 with enough ice (extra > 10 m), on both trees.
- B: the endings test's fixture runs its own source chosen by a rule that isn't the outcome (for example the run's
  moment closest to its own median dT, the coordinator's PW-623 idea): owner's call, as it changes the set-up.
- C: hold PW-627 until a run-physics change makes sim4 warm again. Not recommended: a lottery.
- [ ] A / B / C

## Updates
- 2026-10-23: Status needs-decision -> done. Coordinator (2026-10-24): superseded: the cold-moment and endings fixtures are multi-seed with a pass-rate bar (PW-643, owner A) and eligibility by rule (PW-645); red single draws are no longer a merge decision.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Created from inbox draft draft-endings-test-fails-on-cold-source-worlds.md (found by base-climate-laneA18).
