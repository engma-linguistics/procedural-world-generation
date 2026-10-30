---
id: PW-1107
title: "Settlements: a river really moving (per-frame drainage) instead of the seeded stand-in"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-60
blocked_by: []
relates: [PW-1011, PW-908]
refs: [planet/lineages/settlements.py, planet/lineages/history/model.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The owner asked for towns to be abandoned when "a river moves". The peoples history keeps the world's present-day rivers through all of time, so nothing in a peoples run says where a river ran 5,000 years ago. Settlements v0 (PW-1011) uses a stand-in: a site on a navigable river in the lowlands (below 300 m) is abandoned at a seeded chance of 3% per thousand years, logged as "the river moved away". On world 4360a3 this is the commonest reason towns are abandoned (see the PW-1011 Updates line). It is honest about being a stand-in, but it is a dice roll, not a river.

What to try: store a coarse drainage per recent frame, or at least a per-frame wetness of each river reach from the frame's rain over its catchment (the world's `downstream` and `flow`, scaled by the frame's precipitation). Then:
- a reach whose flow falls under the navigable threshold strands its towns ("the river dried up");
- a delta or floodplain cell where the sea level or sediment shifts the channel moves its site to the neighbouring cell. That could also be done in a regional zoom, at km scale.
- [ ] settlements read a per-frame river signal; RIVER_SHIFT goes, or is kept only for floodplain avulsion with a cited rate

## Updates
- 2026-10-30: Created from inbox draft draft-settlements-rivers-moving.md (found by fun-lane-60).
