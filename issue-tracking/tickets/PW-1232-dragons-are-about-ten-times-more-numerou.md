---
id: PW-1232
title: Dragons are about ten times more numerous on main than lane 90 measured (D20 and the dragon food chain combined)
type: task
status: needs-decision
parent: null
milestone: null
subsystem: highlights
effort: m
impact: med
found_by: lane93
blocked_by: []
relates: []
refs: [docs/review/dragon-food-chain/report.md, docs/review/megafauna/probe.py, planet/lineages/history/megafauna.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
Lane 93 re-ran lane 90's probe (the "on" arm, six worlds, roll 7000) on main after lane 83 (D20) and lane 90 were both merged. Median
world total: 65,375 dragons, against 3,454 in lane 90's "after" column; Sword Coast-sized region mean 1,504 against 118; white, silver and
bronze medians 242, 534 and 5,096 against 26, 20 and 146. A control (the lane 90 tip, world 067778) gives lane 90's 2,946 exactly, while
main gives 22,001 on that world, so the change is in the merged code, not the probe. In 067778's cell fields the persecution field
(`kill`) is 3.4 times lower on main (281 against 81.6) and the stock of livestock 2.7 times lower, so lane 83's lower peoples densities
most likely weaken the persecution lane 90 calibrated (`KILL_Q`) against. Also, the deep-time peak is back at 286-400 kyr (1,200 on e71172)
instead of 8-16 Myr ago, so the planet-wide deep budget (ruling #11) no longer shapes it, perhaps because a megafauna people now founds
only where its own country lies.

In plain words: the two big lanes each worked on their own, and together the dragons are ten times what the dragon paper's sourced
numbers give. Options: (A) accept: the paper's numbers were measured with a denser peoples model, and the new peoples model is the one
that stays; (B) re-calibrate `KILL_Q` (and the persecution by techs) on the D20 peoples so dense farmers still keep 10% of their dragons;
(C) first find which of D20's changes does it (run main with the era density or the founding rule off in a scratch checkout). Lean: C
first, then B. Needs the owner because it moves the dragons' headline number.
- [ ] isolate the cause on 067778 (a run per D20 switch)
- [ ] re-measure all of H1 and H2 (pressure-off and persecution-off arms) once settled

## Updates
- 2026-10-31: Created from inbox draft draft-dragons-tenfold-after-d20.md (found by lane93).
