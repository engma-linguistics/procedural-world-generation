---
id: PW-1485
title: "Tech tree: D55's own-invention floor, now never faster than the anchor, still brings the dnd world's writing ~1.5 kyr early (off); keep it off?"
type: task
status: needs-decision
parent: PW-661
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane-200
blocked_by: []
relates: [PW-1471]
refs: ["planet/lineages/techtree.py::own_floor", planet/lineages/samples/techtree.toml, docs/review/culture/techtree/round2.md]
created: 2026-11-05
updated: 2026-11-05
---

## Description
**In plain words.** D55 asked that climbing the tech tree happen "no slower than a given rate". Lane 200b built that floor: a region
that could invent a tech (and has any specialists) invents it no slower than the "anchor" learner. The anchor learner is the
10-million-strong people whose rate is set from Earth's dates. So the floor never speeds up a people as big as the anchor or bigger.
But it does two things nobody asked for:
- **The humans alone do not need it.** They are bigger than the anchor, so on the humans-only world the floor changes nothing
  (8 draws, identical with it on or off). Region learners already make them climb: chiefdoms in 8 of 8 draws, cities and kingship
  in 6 of 8, writing in 3 of 8 (main's tree on the same history: 1, 3, 1 and 0 of 8).
- **It speeds up the dnd world.** Most dnd regions are smaller than the anchor, so the floor lifts nearly all of them. With it on,
  the world's first writing comes ~1.5 kyr earlier than with it off. Run 0141d1: 6,166 years ago, against 4,716 with it off and
  main's 4,153 (main's 12-draw range 2,797-4,795). Run a2b637: 5,637, against 4,006 off and main's 3,796. In both cases this is the
  median of 12 draws.

So it ships off (`[defaults] own_floor = false`).

**Options.**
- **A: keep it off.** Region learners do D55's job for the humans alone. The floor stays in the code for a tree that wants it.
- **B: a weaker floor**, a share of the anchor learner's rate (say a quarter). That is a new judgement number with no source.
- **C: floor on, anchor re-set to slow everyone back down.** That needs anchor_peers above 32, beyond the sourced range of 11 to
  "more than 20" independent centres.

**Lean: A.** The floor lifts the small and leaves the big alone. On these worlds that is the opposite of what is needed: the slow one
is the big lone people, and regions already fix it.

## Updates
- 2026-11-05: Created from inbox draft draft-own-floor-faster-than-anchor.md (found by lane-200).
