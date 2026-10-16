---
id: PW-295
title: "Time zoom from a run's moment: drift median smaller after PW-274..277, but a heavy tail (-286, -312 m in 150 kyr)"
type: task
status: in-progress
parent: null
subsystem: timezoom
effort: m
impact: med
found_by: ice-fix
blocked_by: []
relates: [PW-241, PW-240, PW-276, PW-275]
refs: [planet/timezoom.py, planet/tectonics/earth.py, docs/review/audit/fixes-ice.md]
created: 2026-10-15
updated: 2026-10-16
---

## Description
150 kyr time zooms (step 0.5 kyr) from keyframes 200/400/600/800/1000 Myr of L5 seeds 2 and 11 (1000 Myr runs),
sea-level change at the end (run's moment = 0):

| | seed 2 | seed 11 | median of 10 |
|---|---|---|---|
| main | -61 -23 -195 -16 -166 | -152 -127 -16 -133 -5 | -94 |
| ice branch (PW-274..277) | -52 -286 -147 -54 -65 | -312 -11 -25 -20 -9 | -53 |

Typical drift is smaller, but two moments now fall ~300 m: seed 2 at 400 Myr (dT +0.7, ice 1.1% -> 9.6% of the
surface) and seed 11 at 200 Myr (dT -7.3, 10.3% -> 17%). Likely cause to check first: PW-276 makes the run's ice
on high ground margin-thin (its surface follows the lowest margin), while the time zoom's shallow-ice flow lets
that ice thicken in place, which raises and cools it and spreads it (height-mass-balance feedback the run's
steady profile doesn't have). The run's ice is meant to be the time zoom's balance (PW-190); PW-241 is the same
family (sheets thickening and grounding onto shelves at first).
Probe: tools-style script in the fix report (tzmulti.py: T.simulate then TZ.simulate from several keyframes).
- [ ] the 150 kyr drift from any moment of L5/L6 seeds 2 and 11 within ~-150 m, or the cause named

## Updates
- 2026-10-16: Re-measured and cause named (tzbatch; no fix merged: the cause is in the run's ice rule, planet/tectonics/earth.py, another lane; draft draft-run-ice-profile-thin.md, needs-decision). Current code, 150 kyr from 200..1000 Myr of L5 seeds 2 and 11 (in-memory sims): median end -147 m, worst -275, 5 of 10 below -150 (before this batch -137 / -284; the polar fixes made the run's cold moments icier). Pure consistency (orbit, CO2, ice albedo off) from seed 11 @ 200 Myr (dT -8): -72 m in 2 kyr, -282 in 20 kyr, then flat. Causes: (1) the run's Nye profile at 50 kPa, sampled at each cell's inner edge, is ~20% thinner than Earth's real sheets on their own extent (Antarctica 19.8 vs 25.1 Mkm3 at L6; 75 kPa gives 25.4) and than the time zoom's shallow-ice flow; the old ice thickens +53 Mkm3; (2) the thickened sheets spread up to 8 cells (427 land cells) by height-mass-balance feedback the run's edge test (330 m) leaves out. Scratch test of the run's last update: 100 kPa: -176 m; 100 kPa + cell-mean rise: -94 m. Capping the ablation zone did nothing. Mild moments drift slowly instead (seed 3199 L6 @ 736 Myr, dT -1.8: -35 m unforced, -114 m with the cycles in 150 kyr): extent growth, not the profile.
- 2026-10-16: Status todo -> in-progress. Time zoom batch agent started.
- 2026-10-15: Created from inbox draft draft-timezoom-drift-tail.md (found by ice-fix).
