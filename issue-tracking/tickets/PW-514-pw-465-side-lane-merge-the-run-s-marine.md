---
id: PW-514
title: "PW-465 side lane: merge the run's marine ice budget (coast_loss)? It fixes the I = 0 drift (9/10) but the 10-seed cold-era check drops 8/10 -> 7/10"
type: task
status: in-progress
parent: PW-470
milestone: v2
subsystem: tectonics
effort: xs
impact: high
found_by: pw465
blocked_by: []
relates: [PW-465, PW-492, PW-461, PW-436]
refs: [docs/review/audit/PW-465-side-lane.md, planet/icemass.py, planet/tectonics/earth.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Branch `worktree-agent-af748cc6ffa533997` (side lane, not merged). The run's ice sheets now pay the
time zoom's own marine losses: `icemass.coast_loss` (the zoom's shallow-ice flow across the coast,
lost where the ice would float, less a standing shelf's buttressing, or calving in shallow water),
charged to the accumulation zones as well as the ablation ring. A sheet that can't pay gives up its
dearest coastal cells. `ICE_CALVE` is gone. The zoom's marine constants now live in `icemass` and
`TZParams` takes them as defaults, so the zoom's output is unchanged (Earth's zoom is identical).

Which loss it was: not calving and not mostly shelf melt. It was the **flow across the grounding
line into deep water** (shelf spreading or breakup: 70-85% of the zoom's marine loss; shelf melt
10-20%; front calving of grounded ice 5-25%). It runs at 1-2e5 m2/yr per m of coast beside deep water
and ~1e3-5e4 beside shallow water; the run charged 5e4 everywhere, and nothing to accumulation zones.

Results (full tables in `docs/review/audit/PW-465-side-lane.md`):
- 10 PW-471 moments (fresh L6 runs, seeds 5/3/2/11), drift at I = 0 in 50 kyr within 25 m:
  **9/10** (main 4/10). The original 7/10 bar with the index: **2/10** (main 0/10). The rest fail
  by the target's form (tiny targets on moments with little snowline land) and by deep glacials on
  cold moments (PW-492's second finding), not by drift.
- 10-seed L6 1 Gyr cold-era check: **7/10** (main 8/10, re-run: identical to the pw449 ref). Seed 7
  goes to -745 m (main -362): shallow coasts are now cheaper than the old 5e4, so some cold eras keep
  more coastal ice. Seeds 3199, 5, 21 and 99 get milder.
- Earth time zoom: identical to main's PW-471 numbers (the zoom didn't change).
- Run time: +39% wall, +53% CPU (seed 11, L6, 400 Myr). The fix isn't optimised: `coast_cost` and the
  trim run in every pass. A merge needs that cut first.
- PW-460/459's run side on top of it: 0/10. The cold eras still freeze, so the marine budget alone
  doesn't unblock PW-460/459 (that needs PW-464 or B(3)).
- A fast test fails: `test_health.py::test_frame_rivers_end_in_its_own_hollows` (a river ends 5 m
  above a salt pan on the changed trajectory; draft-river-end-beside-salt-pan.md). Goldens pass.

Options:
- (A) Merge as is (meets the >= 7/10 bar, fixes the drift), after the salt-pan test fix.
- (B) Keep it parked under PW-470 until PW-464 (cycle mean) and PW-460/459 are re-applied together,
  then judge all three at once (the side-lane doc has the PW-460/459 result on top of this).
- (C) Drop it.

Lean: (B). It is the right physics and it does what PW-465 asked, but it moves the run's cold eras
(one seed to -745 m) during a v1 freeze where ice is parked, for a gain (run moments) that only
matters once the time zoom's run-moment bar is back on the table.

## Updates
- 2026-10-21: Owner 2026-10-21: option B. Work continues in a side worktree: PW-464 (cycle mean) with PW-465's coast_loss and PW-460/459 re-applied together, judged as one batch, merged together if it holds up.
- 2026-10-21: Created from inbox draft draft-pw465-merge-decision.md (found by pw465).
