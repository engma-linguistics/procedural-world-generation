---
title: "A filled people now jumps, so a stem's range and its splits' birthplaces move: one dnd5 try has humans at 2.6% (elves 60%)"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: highlights
effort: s
impact: med
found_by: lane83b
blocked_by: []
relates: [PW-920, PW-1202, PW-1207]
refs: [planet/lineages/history/dispersal.py, docs/review/peoples-d20/report.md, docs/review/peoples-d20/suite-final.md, "world af2677"]
---

## Description
**In plain words:** lane 83b let a people that has filled its land send founders out, as a crowded people does. Before, only crowding
by rivals did. Without this the kobolds stay under 1% in two of three dnd seeds, so it stays in. But it moves everyone a little,
stems included. In one try of the five-people tree (humans, elves, dwarves, halflings, orcs; world af2677, seed 7) the archaic stem
jumped, the humans were born somewhere else, and they ended at 2.6% of all people, with elves at 60%. With the same code minus this rule,
that try has humans at 61%.

Measured (one try each):
- dnd5 af2677 s7: humans 2.6%, elves 60% (stage 3: 61% and 7.3%). The other three dnd5 tries: humans 57–72%.
- dnd on 4360a3, without the rule: kobolds 0.25/0.45/3.6% on seeds 7/10/13; with it 1.3/2.8/4.3%.

This is lane 84's "the tipping point is a race" again: where a dense broad people is born decides the world. The rule widens the
draw, which is what PW-1202 A wants (sister peoples born apart), but a single try can go far.

Options:
- A. Keep it, and judge brittleness on several re-rolled tries of the small trees (PW-1207's per-world swing) before calling it.
- B. Let only a people that has filled all of its reachable country push founders out (stricter: its free good country within one
  jump length is gone). Fewer stem jumps, kobolds still get out.
- C. Drop it, and get the kobolds out some other way (their draft's options B and C).

Lean: A, then B if the re-rolled small trees swing more than base.
