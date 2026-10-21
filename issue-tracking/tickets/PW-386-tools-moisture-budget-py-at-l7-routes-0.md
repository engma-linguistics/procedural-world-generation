---
id: PW-386
title: tools/moisture_budget.py at L7 routes ~0.5 Sv of the Atlantic's rivers into 'Med+inland'
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: xs
impact: low
found_by: pw015-rain
blocked_by: []
relates: [PW-016, PW-014]
refs: [tools/moisture_budget.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
On the PW-015 branch, Earth: the Atlantic's E and P are the same at L6 and L7 (3.31 / 1.71 Sv vs 3.34 /
1.71) but its river input is 1.40 Sv at L6 and 0.92 at L7, while 'Med+inland' gets 0.34 vs 0.81 Sv. So the
headline Atlantic E-P-R (PW-016's criterion) reads +0.20 Sv at L6 and +0.71 at L7. Main shows it too
(+0.06 / +0.19). Probably `drainage()` (priority flood on the ice surface) ends a big Atlantic river (the
Amazon or the Congo's ~0.2-0.5 Sv) in a sea cell cut off from the world ocean at L7, which `basins()` calls
inland. Check which rivers, and route cut-off sea cells to the basin of the ocean they lie in.
- [ ] Atlantic river input within ~10% between L6 and L7

## Updates
- 2026-10-16: Created from inbox draft draft-moisture-budget-l7-drainage.md (found by pw015-rain).
