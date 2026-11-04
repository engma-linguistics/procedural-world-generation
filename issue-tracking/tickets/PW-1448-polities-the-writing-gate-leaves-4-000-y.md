---
id: PW-1448
title: "Polities: the writing gate leaves 4,000 years of cities with no rulers on the D&D run"
type: task
status: todo
parent: PW-661
milestone: v3
subsystem: culture
effort: xs
impact: high
found_by: lane-169
blocked_by: []
relates: [PW-1431, PW-1432]
refs: ["planet/lineages/polities.py::WRITING_TECHS", docs/review/culture/polities/round1.md, docs/review/cultures-proposal/owner-notes-r1.md, docs/review/cultures-proposal/proposal-r2.md, "run a2b637", "run 3c1caf"]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** You ruled that "a chiefdom needs writing" (P2, "nearly B"), and polities v0 keeps that rule. On the D&D run
a2b637, the humans have cities from 5,000 years ago and kingship from 4,500 years ago. But they get writing only 1,100 years ago.
So for 4,000 years the map shows cities and no rulers at all, only dragon realms. On the Seven Meals showcase (3c1caf) writing
comes earlier, and states appear from 7,000 years ago. If this is never decided, worlds like a2b637 show an empty Polities layer
for most of their history. Your Seven Meals empires "over the last few thousand years" may then not exist.

What we would like is for the need for records to pull writing in earlier. The proposal reads your "impetus" point that way. That
needs the history (polities v1); a read-out cannot change the tech tree.

Options (set in one constant, `polities.WRITING_TECHS`):
- **A: keep it.** A chiefdom needs writing, its own or a neighbour's. On a2b637 the first chiefdoms and states come 1,100 years
  ago.
- **B: forerunners count.** Proto-writing (pictograms) also counts as records. On a2b637 the first states come ~4,500 years ago.
  4,000 years ago there are 2,765 chiefdoms, 9 states and 97 empires; at the present 986 chiefdoms and 364 states and empires
  (A: 934 and 344).
- **C: only states need writing.** Chiefdoms need `chiefdoms` alone (round 1's lean A), and states still need writing. Earth's
  chiefdoms are older than writing.

**Lean: B for v0, then the feedback in v1.** It keeps the spirit of "records first" and gives states a deep past where the run
has cities.

## Updates
- 2026-11-04: Status needs-decision -> todo. Daniel 11-04 (D49): B plus C. Chiefdoms need only writing's forerunners (proto_writing counts); real states and empires need writing. He also wants a picture of how fast writing spreads; he suspects it is far too slow. Lane 184.
- 2026-11-04: D49 on the owner's desk; lean B (proto-writing counts), C close second.
- 2026-11-04: Created from inbox draft draft-polities-writing-gate.md (found by lane-169).
