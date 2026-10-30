---
title: "Before 300 kyr the dragons' density is a flat rule at the land's median prey: right on the median but off by up to 2.7x per world at the hand-over, ignores peoples"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: low
found_by: dragon-density-r2
blocked_by: []
relates: [PW-977, PW-990]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/index.html]
---

## Description
**In plain words.** For the deep past, before today's continents, the model has no map of grazers, so it gives dragons a flat density.
Where the two rules meet, 300,000 years ago, the flat rule agrees with the food rule on the median world (with no peoples pressing),
but in a given world it is off by up to about 2.7 times either way, and it leaves the peoples out. So the "age of dragons" peak
(about 1.3 million dragons at the median, some 10 million years ago) is about right on average and wrong per world.

Evidence (review round 2, section 5.5; `numbers.json` `steps.{on,off}.300_summary`, after/before): pressure off x1.2 median
(x0.37 to x2.6 by run); pressure on x0.81 median (x0.049 to x1.1).
Options: **A.** scale the flat rule to the food budget's planet mean at the hand-over; **B.** build a coarse prey field for deep epochs
from their climate. Lean: A (cheap, removes the per-world step); impact low because the median already agrees.
- [ ] decide A/B
