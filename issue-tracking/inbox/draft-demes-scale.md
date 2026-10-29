---
title: "How big is a regional population (deme)? The distance-split threshold sets ~50-60 human demes"
type: task
status: needs-decision
parent: PW-981
milestone: v2
subsystem: timezoom
effort: xs
impact: med
found_by: fun46-demes
blocked_by: []
relates: [PW-981, PW-856, PW-767]
refs: [planet/lineages/demes.py, "run b69f51", "run ac4c06"]
---

## Description
In plain words: the demes pass cuts a long range into a chain of regional populations once it is wider than a set travel
distance. That distance decides how many "cultures in waiting" each people gets: a few big ones per continent, or many
small ones. It is a taste call, not physics.

Now: SPLIT_KM = 7,000 "easy km" (coast-equivalent travel; ~5,500 km of open lowland, fewer through forest, desert or
mountains). Result: humans 60 living demes on b69f51 (~47,000 cells seen, ~780 cells or ~2.4 Mkm² per deme), 51 on ac4c06;
most peoples 1-25 (2cb509: humans 16).

Options:
- A: keep 7,000;
- B: 10,000-12,000 (untested: perhaps half as many demes; a cleaner tree, coarser cultures);
- C: two levels: big demes (B) with sub-demes inside (A), the tree drawing the big ones and the sub-demes on demand.
Lean: C later (languages want both levels), B now if the tree reads too busy in the workbench.
