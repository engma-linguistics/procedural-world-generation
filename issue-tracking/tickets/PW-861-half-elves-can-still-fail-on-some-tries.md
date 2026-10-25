---
id: PW-861
title: "Half-elves can still fail on some tries on the owner's world: humans land 4,800+ km from the elves on a continent 86% held by other peoples"
type: task
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-24
blocked_by: []
relates: [PW-852]
refs: [planet/lineages/history.py, planet/lineages/crossing.py, "world 2a7385", "time zoom f778ab"]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Final runs on 2a7385 (best of 4 tries) did produce half-elves (dnd 62341d, seven_meals bbfba8); a single-try probe (seed 7000000) did not, so this is the residual risk, not the common case.
PW-852 fixed the mechanisms (contact is a frontier, an arrival comes down by its hybrid partner only on free land) but a probe of the dnd tree on world 2a7385 shows the remaining cause. Continent 0 (41.7k cells) is 86% held by kobolds, dragonborn (25k), kenku, lizardfolk, gnomes; the elves hold ~4k cells, and the humans who sail in ~5.9 kyr ago hold only ~500 cells (they are squeezed by the crowd, not "a gas"), more than 80 cells (~4,800 km) from the nearest elf at every frame, so there is no frontier to make half-elves from.
Options: (A) sea landings of a people whose contact hybrid is wanted favour coasts near the partner (crossing.hop); (B) lower the other peoples' squeeze on the newly landed humans (a newcomer's pioneer advantage); (C) accept it and let the owner pick another seed. Lean A, small and in the spirit of the arrival rule.
- [ ] a half-elf origin in the dnd run on 2a7385

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 26 (80c1df3).
- 2026-10-25: Created from inbox draft draft-humans-land-far-from-elves-on-crowded-continent.md (found by fun-lane-24).
- 2026-10-25: fun lane 26. Cause: in closed country a newcomer has no room (niche overlap + ALPHA_CLOSED), so ranges are static until the Holocene farmers' push and late mixing relax them, and an ocean crossing needs boats (~6-10 kyr ago). On 2a7385 the elves (arrival, 25 kyr ago) fell back to their best habitat when no land near the humans was 'free' enough (half their best habitat), landing on a continent the humans reach only after the boats; the humans were never a gas there. Fix by mechanism, both in the spirit of PW-852: (1) `history.ARRIVAL_ROOM` = (0.5, 0.2, 0.0): the arrival near its partner takes the first tier of free room that has some, in the roomier half (`ARRIVAL_POCKET_RINGS`); (2) `PARTNER_PULL` = 4: a sea landing of a people whose contact hybrid is wanted is likelier (x1..x5) and placed on the partner's coast (crossing.hop `pull`). Measured, dnd tree on 2a7385, one try each (seeds 7000-7007, ~9 min each at L7): before (old tree and code, 4 tries) half-elves in 3 of 4 (7000 failed: humans on a 2.4k-cell continent, elves on the big one, 57 hops apart at the present); after, 8 of 8, born at 20 kyr ago in 7 and at 4.9 kyr ago in 1 (7002). Cost: the elves end at 43-120 cells in 5 of 8 tries (1000-1700 in 3; 1138, 1352, 4148 and 2 before): draft newcomers-stay-small-on-crowded-countries. Tests: test_a_sea_landing_follows_the_pull_toward_the_partner, test_an_arrival_near_its_partner_takes_the_freest_country_when_none_is_free (fails with ARRIVAL_ROOM = (0.5,)).
