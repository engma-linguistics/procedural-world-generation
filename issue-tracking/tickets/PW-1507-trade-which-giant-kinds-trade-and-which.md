---
id: PW-1507
title: "Trade: which giant kinds trade and which take tribute (the ledger uses a placeholder: a way of life of their own means trade)"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: xs
impact: low
found_by: lane 212
blocked_by: []
relates: []
refs: ["planet/lineages/trade.py::mode_of", docs/review/culture/trade/step1.md]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: Daniel ruled (D65, on the D-T3 ticket) that giants take tribute and/or trade "depending on the kind". The goods ledger needs a rule
now, so lane 212 used a placeholder. A giant kind with a way of life of its own trades; in the D&D tree only hill giants have one
(they herd). Every other giant kind takes tribute: stone, frost, fire, cloud, storm and sky giants.

Options:
- A. Keep the placeholder (a way of life means trade).
- B. Add a `trades` / `tribute` trait to each giant kind in the trees, set by hand per kind. For example: frost giants raid and take
  tribute; storm giants trade by sea; cloud giants trade luxury goods.
- C. Decide it from what each kind knows: a kind that knows `markets` or `trade` trades.

Trade-offs:
- A needs no work, but it is crude.
- B is the most controllable, and it is a tree edit.
- C follows the tech tree, but giants rarely learn techs.

**My lean: B, as a trait on each giant kind**, because the ruling says "depending on the kind". It matters only for step 2.

## Updates
- 2026-11-08: Status needs-decision -> todo. Coordinator: Daniel's D65 said giants tribute and/or trade 'depending on the type'; take the lane's lean (a hand-set trait per giant kind) in step 2.
- 2026-11-08: Created from inbox draft draft-trade-giant-kinds-trade-or-tribute.md (found by lane 212).
- 2026-11-07: Drafted by lane 212.
