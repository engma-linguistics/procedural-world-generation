---
id: PW-1670
title: The world's writing date hinges on one people's first one or two town cells, read at 260-year tree steps
type: task
status: todo
parent: PW-661
milestone: later
subsystem: peoples
effort: m
impact: med
found_by: lane278
blocked_by: []
relates: [PW-1597, PW-1596, PW-1464]
refs: [docs/review/culture/polities/round23.md, docs/review/culture/polities/round23/split.py, docs/review/culture/polities/round23/trace_tech.py, docs/review/culture/polities/round23/foot_when.py, "planet/lineages/techtree.py::Calendar.settled", "planet/lineages/techtree.py::town_cells_within", "planet/lineages/techtree.py::Calendar.advance", "planet/lineages/settlements.py::_tier_turns", "world 899985", "world 4360a3"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
**In plain words.** A state tech such as writing can only be invented by a people with towns of its own (arm S, Daniel's D60 B):
the tree asks whether the people has at least one town cell, and it asks once per tree step, which is about 260 years apart around
7,000 years ago. On L7 world 899985 seed 10 (main 3bd4bd28, scratch runs 77ef27 / 2e818e, gone after lane 278) the hobgoblins'
first town cells came one century apart in two read-outs of the same history (2 cells at 7,400 years ago against none). That one
century crossed a tree step, so the hobgoblins started their waiting hazard one step (260 years) sooner, invented writing 443
years sooner (6,391 against 5,948 years ago), and the 12 largest peoples' writing median moved 297 years (5,637 against 5,340),
because the world's writing spread from them. Lane 278 fixed the read-out that made the two differ (round23.md), but the
sensitivity is the model's: any nudge that moves one leading people's first town by a century can move the world's writing by a
tree step or two.

Try (cheap first): let arm S's "settled" ramp with the town cells (e.g. the hazard scaled by min(1, cells / a few)) instead of
a one-cell switch, or let the ready ramp read the time the people became settled to the century (the footprint's own sample),
not the tree step; then measure the 5 PW-1597 pairs' writing spread under re-rolled draws (techtree.rebuild(seed=...)) before
and after.

**What misleads if never done.** The writing date, and every state founded from it, jumps by centuries for a reason a reader
cannot see (one or two places crossing 1,000 people a century apart), so steadiness under the nudge (PW-1596) reads worse than the
history is, and the on/off and before/after checks keep finding one-to-two-step gaps that are this threshold, not a change in
history.
- [ ] the 12 largest peoples' writing median moves less than one tree step when one people's first town cell moves one century
  (measured by shifting the footprint on one of the five PW-1597 pairs)

## Updates
- 2026-11-10: Created from inbox draft draft-writing-hinges-on-one-peoples-first-town.md (found by lane278).
