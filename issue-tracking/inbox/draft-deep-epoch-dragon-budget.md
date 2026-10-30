---
title: "Before 300 kyr the dragons' density is a flat rule at the land's median prey: ~2.2x the food budget at the hand-over, ignores peoples"
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
Where the two rules meet, 300,000 years ago, the flat rule has about twice as many dragons as the food rule even with no peoples
pressing them. So the "age of dragons" peak (about 1.8 million dragons some 10 million years ago) is high by about that factor.

Evidence (review round 2, section 4.5; `numbers.json` `steps.{on,off}.300_summary`): the count falls by ~x0.45 (pressure off) and ~x0.05
(pressure on) across the 300 kyr hand-over (medians over the runs).
Options: **A.** scale the flat rule to the food budget's planet mean at the hand-over; **B.** build a coarse prey field for deep epochs
from their climate. Lean: A (cheap, removes the step).
- [ ] decide A/B
