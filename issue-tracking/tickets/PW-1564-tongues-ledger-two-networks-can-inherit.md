---
id: PW-1564
title: "Tongues ledger: two networks can inherit the same trade-language id in one era (a split network shows the same id twice)"
type: task
status: done
parent: null
milestone: v4
subsystem: peoples
effort: xs
impact: low
found_by: lane-231
blocked_by: []
relates: [PW-1526]
refs: ["planet/lineages/tongues.py::era_rows", docs/review/peoples/trade-languages.md]
created: 2026-11-08
updated: 2026-11-09
---

## Description
In plain words: when a long-haul network splits in two between eras, both halves look for the earlier network they share most trading towns
with, and both can pick the same one, so both keep its id and its `since_kyr`. On the stored run a24559 (GET /api/tongues?run=a24559 at 4.5
kyr ago) `lingua-5.5-1`, `lingua-5-19` and `lingua-5-0` each appear twice in one era. The viewer's trade-language legend then lists the same
id twice, and anything that counts distinct ids per era (lifetimes in the doc's results table) undercounts a little.

What to do:
- [ ] in `era_rows`, let an earlier network hand its id on to one successor only (the one sharing most towns); the other gets a new id (its
  `since` starts now) but may still inherit the tongue record from the same predecessor;
- [ ] a test with a network that splits in two;
- [ ] re-measure the six stored runs (lifetime numbers will move slightly) and note the change in docs/review/peoples/trade-languages.md.

## Updates
- 2026-11-09: Status todo -> done. Lane 233 (12f38974): a split network hands its id and since_kyr to the successor sharing most trading towns; duplicate ids per era 46-101 -> 0 on six stored runs; test added.
- 2026-11-08: Created from inbox draft draft-tongues-network-ids-duplicate.md (found by lane-231).
