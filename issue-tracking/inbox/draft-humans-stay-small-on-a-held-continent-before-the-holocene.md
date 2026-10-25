---
title: Humans stay at 1.8-3k cells on a held continent until the Holocene on 3 of 8 dnd tries (2a7385); pressing harder did not move them
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-27
blocked_by: []
relates: [PW-869, PW-861]
refs: [planet/lineages/history.py, planet/lineages/crossing.py, "world 2a7385", "dnd tries 7000, 7005, 7006"]
---

## Description
PW-869 (fun lane 27) added a newcomer's founding window and an expansive people's press (`history.pioneer_factors`) and a raft/dugout rung (`spec.RAFT_KYR`, 100 kyr ago, 120 km, sea share 0.1). Elves now hold 850-2980 cells on 8 of 8 tries (3 of 8 before) with the half-elves on 8 of 8. What it did not fix: when the humans' origin falls on the small continent (landmass 1, 36 Mkm2; tries 7000, 7005, 7006) they hold 1.1-2.9k cells from 200 kyr ago to the Holocene and only grow with the farmers (to 4-12k at the present), while on the big one (tries 7001-7004, 7007) they reach 13-20k cells within 100 kyr of their origin. Measured with a diagnostic probe (seed 7005/7006, one try each):
- The sea is not the limiter there. The first big crossing between the two continents is ~1000-2300 km of open sea; the raft (L = 120 km) and canoe (L = 300 km) rungs make that unlikely in tens of kyr, and the planked boat (6 kyr ago, 1500 km) makes it happen at 2.5-5.9 kyr ago. That is plausible for this geography (the real crossings to Sahul were ~100 km hops through islands, which the rafts now make from 100 kyr and the canoes from 60 kyr: Munin, 662 km, at 58-64 kyr).
- The rivals are not the whole limiter either. With the expansive press (`history.EXPANSE_PRESS`, which is what lets the elves hold their ground) raised from 0.6 to 0.95 the humans ended at 4.6k and 7.2k cells on 7005 and 7006, against 6.5k and 4.9k at 0.6 (in a1: 6.5k, 4.9k), with the same flat range from 100 to 20 kyr ago. So it presses newcomers (elves) into country but does not free the humans.
- Suspects: the human niche (`temp_c [6, 26]`, `prefers temperate/subtropical/lowland`, K) on that continent before farming; `spread()` speed (`speed_kmyr`) against the 1-kyr steps; the MVP fade of small separate patches; or the closed-country exclusion by dragonborn, lizardfolk and kenku (25k, 12k and 14k cells) which have the same niche overlap. A per-cell dump of K, the competition `q` and `room` for the humans on 7005 at 100 kyr ago would say which.
- [ ] humans on the small continent reach 8k+ cells within 30 kyr of their origin on 3 of 3 tries, or the cause is written down as the niche (then it is a tree question, not a mechanism)
