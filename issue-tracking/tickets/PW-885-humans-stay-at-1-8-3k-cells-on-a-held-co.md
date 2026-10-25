---
id: PW-885
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
created: 2026-10-25
updated: 2026-10-25
---

## Description
PW-869 (fun lane 27) added a newcomer's founding window and an expansive people's press (`history.pioneer_factors`) and a raft/dugout rung (`spec.RAFT_KYR`, 100 kyr ago, 120 km, sea share 0.1). Elves now hold 850-2980 cells on 8 of 8 tries (3 of 8 before) with the half-elves on 8 of 8. What it did not fix: when the humans' origin falls on the small continent (landmass 1, 36 Mkm2; tries 7000, 7005, 7006) they hold 1.1-2.9k cells from 200 kyr ago to the Holocene and only grow with the farmers (to 4-12k at the present), while on the big one (tries 7001-7004, 7007) they reach 13-20k cells within 100 kyr of their origin. Measured with a diagnostic probe (seed 7005/7006, one try each):
- The sea is not the limiter there. The first big crossing between the two continents is ~1000-2300 km of open sea; the raft (L = 120 km) and canoe (L = 300 km) rungs make that unlikely in tens of kyr, and the planked boat (6 kyr ago, 1500 km) makes it happen at 2.5-5.9 kyr ago. That is plausible for this geography (the real crossings to Sahul were ~100 km hops through islands, which the rafts now make from 100 kyr and the canoes from 60 kyr: Munin, 662 km, at 58-64 kyr).
- The rivals are not the whole limiter either. With the expansive press (`history.EXPANSE_PRESS`, which is what lets the elves hold their ground) raised from 0.6 to 0.95 the humans ended at 4.6k and 7.2k cells on 7005 and 7006, against 6.5k and 4.9k at 0.6 (in a1: 6.5k, 4.9k), with the same flat range from 100 to 20 kyr ago. So it presses newcomers (elves) into country but does not free the humans.
- Suspects: the human niche (`temp_c [6, 26]`, `prefers temperate/subtropical/lowland`, K) on that continent before farming; `spread()` speed (`speed_kmyr`) against the 1-kyr steps; the MVP fade of small separate patches; or the closed-country exclusion by dragonborn, lizardfolk and kenku (25k, 12k and 14k cells) which have the same niche overlap. A per-cell dump of K, the competition `q` and `room` for the humans on 7005 at 100 kyr ago would say which.
- [ ] humans on the small continent reach 8k+ cells within 30 kyr of their origin on 3 of 3 tries, or the cause is written down as the niche (then it is a tree question, not a mechanism)

## Updates
- 2026-10-25: Created from inbox draft draft-humans-stay-small-on-a-held-continent-before-the-holocene.md (found by fun-lane-27).
- 2026-10-25: fun-lane-28: limiter found, nothing merged (no stopgap). Instrumented 7005/7006/7000 at 150/100/60/30 kyr ago: humans hold ~1.8k of landmass 1's 11.5k land cells; only ~4.2k of them have K >= EST for humans (K >= 0.3: 3.5k), the rest is niche. Every unheld frontier cell with K >= EST (538 of 568) is held by other peoples (orc 1.3k, hobgoblin 1.35k, leonin 0.6k, bugbear, lizardfolk, tabaxi, halfling... 13-15 peoples); none is empty (0), and cells with K < EST are only 19-50 of the frontier. At the frontier the rivals' load is q ~1.07 (median; 0.66-1.35) against K ~0.81, so room = K - q x qm is ~0.01 (90th pct 0.1 < EST 0.12) even after the expansive press (qm 0.73 at explore 0.55); inside their range q is 0.47. That is the closed-country exclusion (alpha_eff > 1 summed over many rivals, bistable: the incumbent holds). Ruled out: sea (all of it is one landmass until the boats), empty-but-unreached country (0 cells), MVP fade, speed (frontier is blocked, not slow), the niche edge, the press's fill switch (EXPANSE_FILL 1.0 with the press at 0.6: 7000/7005/7006 at 1.7-2.0k at 100 kyr, 3.1-3.2k at 20 kyr, same as before; the potential count is global so the switch was never off). The 8k target cannot be met on that continent alone (4.2k suitable cells); it needs the sea, which opens only at 58 kyr (to the 1.7 Mkm2 landmass, 551 cells) and the planked boat. Baseline now (L6, 8 tries, human cells @200/100/60/40/20/0 kyr ago): 7000 849/1861/1919/2335/3180/9345; 7005 1141/1847/1855/2276/3142/12267; 7006 740/1848/1812/2291/3107/10584; the big-continent tries 7001-7004, 7007 reach 13-21k by 100 kyr and 36-43k at the present. Elves 854-2980 cells on 8 of 8 (PW-869 holds), half-elves on 8 of 8. Open question for the owner (draft draft-incumbent-exclusion-vs-denser-newcomer): whether denser, expansive newcomers should displace thinner incumbents (the tree) or whether this is the niche; levers that move it (density push) cost the elves/orcs earlier. Status left.
