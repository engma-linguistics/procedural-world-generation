---
title: "Trade: nobody wants seal or whale oil, so the brief's 'Bought in' line can never show it"
type: task
status: todo
parent: PW-1498
subsystem: culture
effort: s
impact: low
found_by: lane 244
blocked_by: []
relates: [PW-1573, PW-1505]
refs: ["planet/lineages/trade.py::NEED", "planet/lineages/trade.py::GOODS", "planet/lineages/bought_in.py::FOOD_GOODS", docs/review/culture/trade/bought_in_244.md, docs/review/culture/trade/review1.md]
---

## Description
In plain words: the goods ledger makes seal and whale oil (`seal_oil`) on coasts with sea mammals. The culinary brief counts it as a
bought-in food (bought_in.FOOD_GOODS). But no way of life wants it (trade.py: "obsidian and sea-mammal oil: no need written yet"), so
it never leaves the coast.

Lane 244 wrote the dried-fish need (PW-1573). No cheap source was at hand for a seal-oil want, so it left this one out. The likely
want is lamp oil and fat for northern peoples away from the coast. A need needs a fetched source for who wanted it and how far it
went: Arctic lamp oil traded inland, or whale oil in towns.

If it is never done, no northern inland culture's brief can say "seal oil from the coast", however close the sealing coast is.
- [ ] a sourced NEED for seal_oil (who, gated by their own coast), with flows and their km reported on the four stored L7 runs
