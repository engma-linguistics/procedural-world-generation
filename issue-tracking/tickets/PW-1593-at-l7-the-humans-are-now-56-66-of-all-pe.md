---
id: PW-1593
title: At L7 the humans are now 56-66% of all people, after the stem-refuge change (PW-1558), with polities on or off
type: task
status: todo
parent: null
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane245
blocked_by: []
relates: [PW-1558, PW-1587]
refs: [planet/lineages/history/dispersal.py, planet/lineages/history/origins.py, "planet/lineages/history/params.py::LAST_LAND_REACH", docs/review/culture/polities/round17.md, docs/review/culture/polities/round17/shares.py, "world 899985", "time zoom fc5311", "scratch l245 data7 runs 7bf29c b08650 (off, main ad780a26)", "scratch l234 runs 0a1c30 7de58b (off, code 5723d08c)"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** On world 899985 (L7, dnd tree), the humans make up 66% of all people now on seed 7 and 56% on seed 10, with
polities in the history switched off, on today's main. Before PW-1558 (lane 233, commit 12f38974: an empty stem holds out within
reach of its last land) the same seeds gave 40% and 61%. On seed 7 the change shows 38,000 years ago, long before any polity
(humans 9% before, 26% after), so it is the deep history's draws, not the polities. Lane 245 measured this while checking PW-1587;
nobody has looked at whether one people holding two-thirds of the world is what PW-1558 meant, or chance on two seeds.

**What misleads if never done.** Round 16 and the coordinator read the 65% as the polities' doing; anyone comparing runs across
that commit will again blame whatever lane they are testing. And a world where one people is two-thirds of everyone is the kind
of brittle outcome the peoples model should not give often (robust, not brittle).

- [ ] the humans' share at L7 over 3+ seeds (and the lane 77 stress suite if cheap), before and after 12f38974
- [ ] if the share is high on most seeds: which part of PW-1558 (founding near the last land, or holding out) feeds the humans

## Updates
- 2026-11-09: Created from inbox draft draft-l7-humans-over-half-after-pw1558.md (found by lane245).
