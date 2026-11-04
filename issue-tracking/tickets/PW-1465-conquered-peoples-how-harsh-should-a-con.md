---
id: PW-1465
title: "Conquered peoples: how harsh should a conqueror be, and where do the expelled go? (kept / thinned / expelled thresholds)"
type: task
status: needs-decision
parent: PW-661
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lane183
blocked_by: []
relates: [PW-1434, PW-1172]
refs: ["planet/lineages/history/polity_live.py::FATE_AT", "planet/lineages/history/polity_live.py::FATE_CUT", "planet/lineages/history/polity_live.py::FATE_MAX", docs/review/culture/polities/round7.md, docs/review/cultures-proposal/proposal-r2.md]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** With polities in the history (PW-1434, behind a switch), when a state takes land, each people living there fares by
how the winner regards it. Attitudes (proposal-r2 3.4) are not built yet, so lane 183 reads the tree's old enmities (the "apart"
wishes, 0..1) and set three judgement numbers:
- hostility under 0.25: **kept** (nothing happens); under 0.6: **thinned** (a quarter of their presence on the taken land is lost
  once); else **expelled** (80% lost there, so most of that land empties);
- no people loses more than 10% of its heads to conquest in one century (the guard against a chain of conquests ending a people);
- the expelled are simply lost. They do not flee to their own remaining land, and the history's spread refills the empty land.

None of these is sourced. Proposal-r2 3.3 records your ruling (P3 B): war is mostly a change of owner; intolerant winners "expel,
enslave or exterminate a share". The round 7 runs give the counts (round7.md section 6).

**What misleads if never decided.** The v4 card ("which peoples it kept, expelled or thinned") will show these numbers as if they were
the model, and the peoples' shares under the switch depend on them.

**Options.**
- A. Keep as is (hostility thresholds 0.25 / 0.6, cuts 0 / 0.25 / 0.8, cap 10% a century).
- B. Milder: thinned 0.1, expelled 0.5, and the expelled move. Their heads are added to their own nearest unconquered land, so
  expulsion moves a people instead of killing it.
- C. Wait for attitudes (3.4) and read tolerance from them; keep A until then.
Lean: B's "the expelled move" is a mechanism, not a tuning, and it makes expulsion read as history (refugees) rather than slaughter.

## Updates
- 2026-11-04: Created from inbox draft draft-conquered-peoples-tolerance.md (found by lane183).
