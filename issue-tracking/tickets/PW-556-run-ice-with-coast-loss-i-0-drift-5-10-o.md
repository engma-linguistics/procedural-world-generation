---
id: PW-556
title: "Run ice with coast_loss: I = 0 drift 5/10 on the merged code's run moments (side lane 9/10); heavily iced moments miss by 40-90 m both ways"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: tectonics
effort: m
impact: med
found_by: pw514a
blocked_by: []
relates: [PW-465, PW-514, PW-492, PW-513]
refs: [docs/review/audit/PW-514-option-a.md, planet/tectonics/earth.py, planet/icemass.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-514 option A (coast_loss + the cost cut + the carve fix for PW-515) gives 5/10 PW-471 run moments within
25 m at I = 0 in 50 kyr (main 4/10, median |drift| 23 m against main's 38). The side lane's code got 9/10 on its
own runs. The cost cut is not the cause: on 24 fixed states the cut, exact repeats, and cost/start every
pass agree within 2.5 m of sea level. The same times fall on different ice on the new trajectory.
The misses are heavily iced moments (25-61% of land iced): s11 @ 200 +89.5 m, s3 @ 500 -91.1 (the zoom
grows ice, so the run under-ices), s2 @ 500 +41.3, s3 @ 620 +44.6, and s5 @ 260 +27.0. Runs are in the
session scratchpad `pw514a/store_br` (seeds 5/3/2/11, L6 800 Myr), harness `pw514a/phase2.sh`.
Ten moments is a noisy sample (about ±2-4 moments). Next: split the s11 @ 200 and s3 @ 500 zooms' budgets as
the side lane's `diag.py` does (flow into the sea, shelf melt, calving against the run's coast_cost) to see
which side of the rule is off on big sheets (PW-513's fixed margin thickness is a candidate), and use 20
moments for the bar.
- [ ] the flux split for the two worst moments
- [ ] the drift bar measured on 20 moments

## Updates
- 2026-10-21: Created from inbox draft draft-coast-loss-iced-moment-drift.md (found by pw514a).
