---
id: PW-1617
title: War refugees never fire, and war does not keep slow breeders up or the commonest people down
type: task
status: todo
parent: PW-917
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane259b
blocked_by: []
relates: [PW-1172, PW-1243, PW-1241, PW-1108]
refs: [planet/lineages/history/dispersal.py, "planet/lineages/history/counter.py::CounterMixin._brake", planet/lineages/history/params.py, docs/review/peoples-counterpressures/design.md]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** The stress suite for war (lane 259b, world 4360a3, 12 runs per arm) found that the "refugees from war-torn
land found new country" event never happened in any of the 36 war runs (default, x2, main), although 'times of troubles' fired
4 to 105 times a run. The share of land war takes in one step is too small, against the jump push, to be at least half of it. And at
x2 war the long-lived peoples (elves, dwarves, gnomes and kin) fall to 77% of their no-war share in the dnd tree and 66% in
seven_meals, while the commonest people does not fall at all (it rises 28% to 30%). So war does not yet do what the design hoped
for the two things it was built to do; the owner's D31 limits (commonest under 50% usually, under 70% with 5+ peoples) hold either way.

What misleads if never done: the viewer's war dials promise displacement and a brake on the biggest people; they give neither.
What to try: log `_refugees(k)` against the push at jump time to see by how much it misses; either drop REFUGEE_Q's 0.5 gate or
count refugees as the share of the pushed-out people that move, and look at why the war-torn cut lands on thin, long-lived
peoples rather than on the crowded commonest (the crowd term N/N0 may saturate; check G and the state term first).
- [ ] a default run shows refugee events on some people (or the refugee path is removed, no stopgap)
- [ ] x2 war leaves the slow breeders' share at or above no-war, or the design drops that bar with the owner's say

## Updates
- 2026-11-09: Created from inbox draft draft-refugees-never-fire.md (found by lane259b).
