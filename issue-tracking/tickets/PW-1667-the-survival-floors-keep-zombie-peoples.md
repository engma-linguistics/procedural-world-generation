---
id: PW-1667
title: The survival floors keep "zombie" peoples (11 green dragons) on the books as living, and hide stillborn splits
type: task
status: needs-decision
parent: null
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: lane 277 (worktree-agent-a7c46b5a720cb2320)
blocked_by: []
relates: []
refs: [planet/lineages/history/params.py, planet/lineages/history/competition.py, planet/lineages/history/dispersal.py, docs/review/peoples/everyone-experiment.md]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words

On main, no people can die out. Several floors (the refuge move, the 0.5 Mkm2 refuge gate on displacement, BRAKE_HOLD, and the viable-population
fade sparing the largest patch) keep any line given as living at the present alive, however small. In the lane 277 control run (everyone tree,
world 4360a3, run fe887b), that left 11 green dragons, 142 silver dragons, 822 white dragons and 1,512 frost giants. Each is listed as a living
people with its own culture, gods and brief. With the floors off (run efe61b), those kinds and 10 other peoples die out. Two splits (mouse-folk
and river halflings) are stillborn: they are founded smaller than 0.5 Mkm2 and are displaced on their first step, because only the refuge gate
had protected them.

## Description

**What breaks if never done:** a reader of the brief, the cultures or the viewer will trust that a people with 11 members is a living
culture. Nothing flags it. The refuge gate also hides a fact: a split is founded on less land than the gate's own size, so every newborn
people is immune to displacement until it grows past 0.5 Mkm2.

**Decision needed:** keep the floors, but flag a line below its viable number (`line_mvp`) at the present as "relict: a few hundred left"
in the outputs; or let lines under it die out in a normal run, as lane 277's `HOLD_OUT_REFUGE=false` does. That needs a story for the tree's
"given as living" peoples, for example "a tree asks for a people; the world may not keep it".

## Updates
- 2026-11-10: Created from inbox draft draft-zombie-peoples-under-the-floors.md (found by lane 277 (worktree-agent-a7c46b5a720cb2320)).
