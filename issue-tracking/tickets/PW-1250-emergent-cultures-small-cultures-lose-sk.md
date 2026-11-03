---
id: PW-1250
title: "Emergent cultures: small cultures lose skills faster (Henrich pool size), and the brief should show a culture as it was at the era"
type: task
status: todo
parent: null
milestone: null
subsystem: culture
effort: s
impact: low
found_by: lane107
blocked_by: []
relates: [PW-670, PW-675]
refs: [planet/lineages/cultures.py, planet/lineages/brief.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
In plain words: two refinements to the first cut of cultures.
1. Henrich 2004 (Tasmania) argues that a small, cut-off group loses skills because it has too few people to learn from,
   and that a big one keeps or improves them. Today every culture loses a skill at the same pace (TAU_LOSE 1 kyr). Scale
   TAU_LOSE by the culture's head count, using the same ln N pool the tech tree uses (techtree, Henrich log form).
2. The brief's "Cultures here" names the cultures that held the land at the era, but "what changed" describes each
   culture's whole life up to the present. For an early era, take the skills and way of life from the culture's series at
   that time. A brief for one people should also list that people's own cultures first.
- [ ] TAU_LOSE scaled by pool size; the effect checked on cc22df
- [ ] the brief at 5 kyr shows the skills as they were then

## Updates
- 2026-10-31: Created from inbox draft draft-cultures-pool-size-and-era.md (found by lane107).
