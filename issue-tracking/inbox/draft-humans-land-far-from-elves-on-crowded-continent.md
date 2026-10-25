---
title: Half-elves can still fail on some tries on the owner's world: humans land 4,800+ km from the elves on a continent 86% held by other peoples
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-24
blocked_by: []
relates: [PW-852]
refs: [planet/lineages/history.py, planet/lineages/crossing.py, "world 2a7385", "time zoom f778ab"]
---

## Description
Final runs on 2a7385 (best of 4 tries) did produce half-elves (dnd 62341d, seven_meals bbfba8); a single-try probe (seed 7000000) did not, so this is the residual risk, not the common case.
PW-852 fixed the mechanisms (contact is a frontier, an arrival comes down by its hybrid partner only on free land) but a probe of the dnd tree on world 2a7385 shows the remaining cause. Continent 0 (41.7k cells) is 86% held by kobolds, dragonborn (25k), kenku, lizardfolk, gnomes; the elves hold ~4k cells, and the humans who sail in ~5.9 kyr ago hold only ~500 cells (they are squeezed by the crowd, not "a gas"), more than 80 cells (~4,800 km) from the nearest elf at every frame, so there is no frontier to make half-elves from.
Options: (A) sea landings of a people whose contact hybrid is wanted favour coasts near the partner (crossing.hop); (B) lower the other peoples' squeeze on the newly landed humans (a newcomer's pioneer advantage); (C) accept it and let the owner pick another seed. Lean A, small and in the spirit of the arrival rule.
- [ ] a half-elf origin in the dnd run on 2a7385
