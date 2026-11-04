---
title: "Polities: the giants' size rests on four stacked judgement multipliers; ±20% on riding and roads swings them 1 to 10 a century"
type: task
status: todo
parent: PW-661
milestone: later
subsystem: culture
effort: s
impact: med
found_by: lane179
blocked_by: []
relates: [PW-1449]
refs: ["planet/lineages/polities.py::_reach", "planet/lineages/polities.py::LAW_X", "planet/lineages/polities.py::DISTANCE_X", "planet/lineages/polities.py::RIDE_X", "planet/lineages/polities.py::WIDE_BY", docs/review/culture/polities/round4.md, docs/review/culture/polities/round1.md, "docs/review/cultures-proposal/proposal.md#212-formation-growth-and-reach", "run 3c1caf"]
---

## Description
**In plain words.** After lane 179 (PW-1449), an ordinary city-state reaches at most 250 km (Spencer 2010). Only conquerors of
states and confederations keep the old reach: 150 km x 4/3 (law) x 2 (distance) / (2/3 x 2/3) (riding, roads) = 900 km. All four
multipliers are judgement calls from round 1. They now set the size of every giant, and they are touchy (3c1caf, round4.md):

| nudge | over 1 Mkm² at the present | per century, last 3,000 years (median, max) | largest ever |
|---|---|---|---|
| none | 8 | 3, 10 | 2.60 Mkm² |
| DISTANCE_X 1.6 / 2.4 | 0 / 6 | 1, 5 / 5, 12 | 2.16 / 4.05 |
| RIDE_X and ROAD_X 1.2 / 1.8 | 1 / 8 | 0, 1 / 10, 17 | 1.59 / 7.12 |

**What breaks if this is never done:** the polities are not "stable when nudged" (Daniel's north star). Anyone retuning riding or
roads for another reason gets either no empires or empires past the Achaemenid record (5.5 Mkm², Taagepera 1997), and the cap's
own ±20% check (stable) hides it.

What I would try: give the wide reach one sourced or checked number instead of a product of four, for example a single
"government at a distance" reach checked against Taagepera's sizes, with riding and roads not stacking on it. Do it together with
(or after) the war-chaining draft, since that changes how big conquerors get.
- [ ] ±20% on each reach constant moves the count over 1 Mkm² per century by under ~2x on 3c1caf
