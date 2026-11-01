---
id: PW-1241
title: "Owner question: how big should the commonest people be? (today: humans about 60% in the full dnd tree on one world, 30% on the other, 90%+ with three peoples)"
type: task
status: needs-decision
parent: PW-917
milestone: v2
subsystem: timezoom
effort: xs
impact: high
found_by: lane97
blocked_by: []
relates: [PW-1172]
refs: [docs/review/peoples-brakes/report.md, docs/review/peoples-brakes/charts.py, docs/review/peoples-brakes/maps.py, tools/peoples_robust.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** Every change to the peoples so far has been judged against "no single people above 85% in a tree of three or
more". That rule catches the worst cases but says nothing about the ordinary ones. Today, in the full dnd tree, the humans are about
60% of all people on one test world and about 30% on the other; with only humans, kobolds and goblins they are 90% or more. (Earth
for scale: one species is 100%, so Earth is no guide here.) Lane 97's charts (docs/review/peoples-brakes/report.md) show how the
number moves with each change and each brake setting.

What number would you like? For example:
- A. "The largest people should usually be under half, and never over 70% when there are five or more peoples."
- B. "Humans can be most of the world; I only want the other peoples to keep real countries (each above some share of land)."
- C. "It should depend on the tree: a human-centred tree may be 60-70% human, an even tree should stay under 40%."
- D. Something else.

Whatever you pick becomes a check in the stress suite, so later changes are measured against it.

## Updates
- 2026-10-31: Daniel picked A (usually under half, never over 70% with 5+ peoples). Lane 101 added it to the stress suite as a reported check (not a failure): all 82 tries 53% median, 48% under half, 86% of 5+ trees at or under 70% (main: 52/49/94). Further work on the share is parked for war and polities.
- 2026-10-31: Created from inbox draft draft-peoples-commonest-share-target.md (found by lane97).
