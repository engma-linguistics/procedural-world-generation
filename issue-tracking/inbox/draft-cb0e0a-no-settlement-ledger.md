---
title: "The new D&D showcase cb0e0a has no settlement ledger (meta.eraq is null), so no towns, cities or Polities layer"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: lane-175
blocked_by: []
relates: [PW-1431]
refs: ["planet/lineages/settlements.py::derive", "planet/lineages/history/frame.py", "planet/lineages/output.py", "run cb0e0a", "run a2b637", docs/review/culture/polities/round2.md]
---

## Description
**In plain words.** Run cb0e0a was made 2026-11-03 23:52 on current code: D&D peoples (preset), on time zoom fc5311 of a19366. It
has cultures.json, gods.json and taboos.json, but no settlements.json. On a scratch copy, `planet settlements cb0e0a` refuses it:
"run cb0e0a: no land-use inputs per frame (meta.eraq): not a peoples run on a world". Its `meta.eraq` is null. a2b637 (a D&D run on
time zoom 56dee1) has it.

If this is never fixed, the showcase Daniel is meant to use shows no towns or cities. It also has no Polities layer, so no states,
empires, wars or falls, and no brief rows from the ledger. A fresh D&D showcase on current code then cannot show v3's states at
all.

The history writes the land-use inputs only when `self.goods is not None` (`history/frame.py`, the `eraq = LU.frame_inputs(...)`
line). `output.py` then keeps meta.eraq only for frames that have them. So either cb0e0a's run had no goods (crops, animals,
fuels), or that condition has gone wrong on current code. Find out which, fix it if it is a bug, and re-make the showcase (or its
ledger).
- [ ] `planet settlements cb0e0a` (or its re-made successor) succeeds, and `/api/polities?run=...` returns states
