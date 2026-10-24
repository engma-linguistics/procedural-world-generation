---
id: PW-782
title: Animal-taming test relies on a lucky fixture seed (horse taming happens in ~4 of 8 seeds on the fake world); make it robust across seeds
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-10-24
---

## Description
fun18 moved _animal_tree's seed 3 -> 1 after per-line RNG streams; assertions unchanged. Per the re-rolled-draws rule, assert a rate over several seeds (or a forced case) instead of one draw.

## Updates
- 2026-10-24: Created.
