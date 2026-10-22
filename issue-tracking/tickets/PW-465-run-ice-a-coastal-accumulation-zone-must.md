---
id: PW-465
title: "Run ice: a coastal accumulation zone must pay the zoom's calving and shelf losses (the run keeps ~100 m of marine ice the time zoom loses at once)"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: tectonics
effort: m
impact: high
found_by: pw462
blocked_by: []
relates: [PW-461, PW-460, PW-459, PW-436, PW-462]
refs: [planet/tectonics/earth.py, planet/timezoom/ice.py, planet/timezoom/sim.py, docs/review/audit/ice-framing-deep-dive.md]
created: 2026-10-20
updated: 2026-10-21
---

## Description
PW-461 option B(2). The run's `ablation_zone` charges calving (`ICE_CALVE` 5e4 m2/yr per m of coast) only on
the *ablation ring* it adds; the accumulation zone found by `_ice_pass` (every iced cell with smb > 0 connected
to a seed) pays nothing for the coast it touches, and nothing stands for the time zoom's ice shelves, their
sub-shelf melt (`melt_k` 10 m/yr per C) or grounded ice in deep water (`calve_depth`). When margins are
honest (PW-460's ramp) the run's cold moments ice their coasts and the zoom then sheds that ice at once.

Measured (PW-462, scratchpad `pw462/states.py`), the consistency fixture L5 seed 1 @ 300 Myr, -4 C, on the
PW-460/459 branch code (246ef40): the run's rule gives -362 m (10.4% of the planet iced). Each of the 8
orbital states' own equilibria gives -340 to -371 m (fresh from no ice: -340 to -360), so neither the cycle
average nor hysteresis is the issue there. The default forced zoom from it rises +78 m in 20 kyr and sits at
+101..+115 m for 300 kyr with no endings (PW-461 a2: calving 12,400 km3/yr against +11,100 of surface balance;
shelf melt 72 M km3 over 20 kyr). On main the same moment is -19 m and its zoom *gains* ice. Main has the same gap on deep moments:
L6 seed 11 @ 400 (in memory, -252 m) has a zoom time mean of +94 m. With the orbit, CO2, albedo and cycle
all off it is still +38 m (a plateau at +41 from 40 kyr), so ~40 m is the rule/budget gap alone. Find which
flux it is (calving, shelf melt, flow onto shelves; `res["flows"]`, `res["budget"]`) before building, since it
may be the shelves rather than calving.

What to try: give each accumulation zone the calving of every coastal cell it holds (the same per-m-of-coast
rate, scaled by the water depth as the zoom's `calving` 1/yr x depth, at the cell's coast), and drop grounded
cells whose bed is below `calve_depth` or whose ice would float, and charge a sheet whose ice meets sea warmer
than freezing the zoom's sub-shelf melt along that coast. Then the run's sheet is the zoom's equilibrium at
its coasts too. Measure with the tz_mean tool (draft-tz-mean-matches-run-check.md) on main and on the
PW-460/459 code, and the 10-seed cold-era check.
- [ ] on the branch code, the L5 fixture's forced zoom mean within 25 m of the run's (today +101 m)
- [ ] main's 10-seed cold-era check does not get worse

## Updates
- 2026-10-21: coast_loss with the cost cut is ready on branch worktree-agent-a9ef586c8f7c30585 (PW-514 option A, docs/review/audit/PW-514-option-a.md). Cold eras 8/10, drift 5/10 on fresh moments (main 4/10; the side lane's 9/10 doesn't reproduce on the new trajectory: draft-coast-loss-iced-moment-drift.md).
- 2026-10-21: Side lane done (branch worktree-agent-af748cc6ffa533997 (c720d92), kept unmerged; write-up docs/review/audit/PW-465-side-lane.md). The loss is ice flowing off the coast into deep water and leaving as shelves (70-85%), not calving. Fix icemass.coast_loss: drift at I=0 within 25 m on 9/10 moments (main 4/10); cold-era check 8 -> 7/10 (seed 7 -362 -> -745 m); Earth unchanged; run +39% wall time; one health test fails. Parked; decision PW-514.
- 2026-10-20: Created from inbox draft draft-run-ice-marine-budget.md (found by pw462).
