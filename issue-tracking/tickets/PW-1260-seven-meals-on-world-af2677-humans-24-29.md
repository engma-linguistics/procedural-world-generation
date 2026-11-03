---
id: PW-1260
title: "Seven Meals on world af2677: humans 24% -> 29% after the inland pits (a real shift, not a re-rolled draw); the rest of PW-1239 was chance"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: peoples
effort: s
impact: low
found_by: lane101
blocked_by: []
relates: [PW-1239, PW-1229]
refs: [docs/review/peoples-leader/data.json, tools/peoples_robust.py]
created: 2026-11-01
updated: 2026-11-01
---

## Description
**In plain words.** Lane 97 saw the peoples shift after lane 98 turned the inland pits into land (PW-1239). Lane 101 re-ran the
draws on the code before and after the pits: dnd and Seven Meals at 6 seeds (7-22) and dnd at 10 date jitters, on both worlds (48
tries a side). Almost all of the shift is chance:
- The humans' tenfold swing in dnd comes from one or two jitters where the humans are born badly on af2677 (1.8% and 1.6% of all
  people). The code before the pits has one too; with 10 jitters both codes flag the humans as brittle in the same share of 3-try
  sets (30%). Lane 97's "humans no longer brittle after D27" was the luck of 4 jitters.
- Seven Meals on 4360a3, humans 35% -> 43%: over 6 seeds it is 37% -> 40% (ranges 29-43 and 35-48); a permutation test gives p 0.37.
- Brittle peoples: dnd 16 before, 15 after; Seven Meals 5 before, 7 after.

One shift is real: **Seven Meals on af2677**. The humans go from 24% to 29% (median of 6 seeds; every try after the pits is above 5
of the 6 before; p 0.01), and the half-orcs fall from 24% to 21% (p 0.11). It is the new land on that world, not the peoples model.
Worth a look only if the Seven Meals half-orcs (who already die out now and then in a jitter) get rarer.

- [ ] if wanted: the inland-pit cells of af2677 that are land now, and who holds them in Seven Meals

## Updates
- 2026-11-01: Created from inbox draft draft-seven-meals-af2677-humans-up-after-pits.md (found by lane101).
- 2026-10-31: Created by lane 101 (PW-1239's check; PW-1239 can close on it).
