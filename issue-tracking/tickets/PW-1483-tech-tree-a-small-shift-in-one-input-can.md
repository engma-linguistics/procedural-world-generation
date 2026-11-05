---
id: PW-1483
title: "Tech tree: a small shift in one input can move a rare invention by thousands of years (one draw per step, not one waiting time)"
type: task
status: done
parent: PW-661
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lane-196
blocked_by: []
relates: [PW-1473, PW-1459, PW-1471]
refs: ["planet/lineages/techtree.py::Calendar.advance", docs/review/culture/polities/round9.md, docs/review/culture/polities/round9/fronts.txt, docs/review/culture/polities/round9/replay_7000.txt]
created: 2026-11-05
updated: 2026-11-05
---

## Description
**In plain words.** The tech tree decides each invention step by step: at every step a people that could invent a tech gets a
fixed random number, and invents if the number is under its chance for that step. If anything shifts when the people could first
start on the tech (a neighbour's know-how arriving a little later), the chances at every step change a little, and an invention
that just made it at one step can miss and then wait thousands of years for another lucky step. On 899985 seed 7 (round9.md,
section 1), clay tokens reached the gnomes 250 years later than in the after-run tree. Because of that the gnomes, the world's
first writers in that draw, invented writing 665 years ago instead of 4,305, and every people that took writing from them was
late too. That is the opposite of "stable when nudged": a nudge to one border moves the whole world's writing.

**What breaks if never done.** Any small change upstream (a border, a population, a newcomer, D55's own-invention rates) can flip
a world's writing, states and empires by thousands of years. The flips look like a model change in review and on the owner's
desk, but they are luck. The pass rates over seeds hide it; single worlds show it.

**Candidate (a mechanism, not a fudge).** Draw one keyed waiting time per (seed, people, tech), as an exponential with mean 1, and
invent when the hazard summed since the people could start reaches it (the inverse method). The front delays already work this
way (one keyed draw per pair). A small shift in the ramp then moves the date by a small amount, not by a re-roll. It changes every
date of every tree, so it needs the golden runs updated, and it should go after D55's lane (PW-1471), which edits the same code.
Check: over 12 draws the median dates stay within the round 6 spread; a one-step nudge to one front moves no date by more than
a few steps.

## Updates
- 2026-11-05: Status -> done. Lanes 200/200b merged (docs/review/culture/techtree/round2.md).
- 2026-11-05: Created from inbox draft draft-tech-tree-dates-jump-on-small-nudges.md (found by lane-196).
