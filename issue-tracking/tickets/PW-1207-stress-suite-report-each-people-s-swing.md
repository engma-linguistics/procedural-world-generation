---
id: PW-1207
title: "Stress suite: report each people's swing per world and per family; the 40x+ 'brittle' flags mostly mix two worlds"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane84
blocked_by: []
relates: [PW-1180, PW-1181]
refs: [tools/peoples_robust.py, docs/review/peoples-robust/report.md, docs/review/peoples-why/report.md]
created: 2026-10-31
updated: 2026-10-31
---

## In plain words
The stress test called hobgoblins, tabaxi, bugbears, halflings and goblins "brittle" because their share swings 40x or more. Most of
that swing is the difference between the two test worlds, not luck within one world. On one world with fixed dates these peoples move
less than 2x between seeds; only the halflings flip (all or nothing). The suite should say which kind of swing it found.

## Description
Lane 77's own runs (range arm, scratch l77/suite), split by world and family (share min-max, swing):

| people | 4360a3 seeds | 4360a3 jitter | af2677 seeds | af2677 jitter | pooled |
|---|---|---|---|---|---|
| hobgoblin | 1.1-1.8% (1.7x) | 1.7-6.0% (3.6x) | 1.4-13.9% (9.8x) | 0.04-9.9% (265x) | 509x |
| tabaxi | 0.94-1.24% (1.3x) | 0.90-1.63% (1.8x) | 0.014-0.025% (1.7x) | 0.013-0.53% (41x) | 125x |
| bugbear | 0.01-0.017% (1.7x) | 0.01-0.09% (9x) | 0.01-0.45% (45x) | 0.01-0.64% (64x) | 64x |
| halfling | 0.39-5.5% (14x) | 0.40-8.4% (21x) | 11-17% (1.5x) | 5.2-8.9% (1.7x) | 54x |
| goblin | 0.09-0.16% (1.8x) | 0.11-0.25% (2.2x) | 0.48-0.85% (1.8x) | 0.44-3.5% (8x) | 49x |

(0.01% is the suite's share floor.) On today's main (lane 84, 4360a3, dnd, seeds 7 10 13 21 34 55) hobgoblins 1.1-1.9%, tabaxi
0.75-1.0%, bugbears 0.006-0.009% (always pinned at the 0.5 Mkm² refuge floor), goblins 0.15-0.23%, halflings 0.5-0.6% or 5.5-10%.

- [ ] `report` gives the swing per world and per family (seeds, jitter, knob, portal) beside the pooled one
- [ ] a people is "brittle" on a per-world, per-family swing; a world-to-world difference is reported apart (it is geography)

## Updates
- 2026-10-31: Created from inbox draft draft-robust-suite-brittleness-per-world.md (found by lane84).
