---
id: PW-036
title: "Time zoom: accumulation jumps at climate refreshes; one-cell ablation zone"
type: task
status: done
parent: null
subsystem: timezoom
effort: s
impact: low
found_by: timezoom
blocked_by: []
relates: []
refs: [planet/timezoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Small accumulation jumps happen at each 10 kyr full-climate refresh (blend between refreshes). The
ablation zone (where ice melts) is only about one 110 km cell wide (sub-cell melt or a wider margin).

## Updates
- 2026-10-14: Status todo -> done. Jumps fixed in 8816c11 (climfix): fields blend from the previous to the newest full climate between refreshes; mean accumulation change at a refresh 84 -> 29 Gt/yr (other steps ~25). The one-cell ablation zone (94% of ablating cells on the margin) is split off as an inbox draft.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Glacial time zoom ('Smaller issues').
