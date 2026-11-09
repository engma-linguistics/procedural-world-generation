---
id: PW-1573
title: "Trade: nobody wants dried or salted fish, so salt fish never travels inland and the culinary brief can't show it"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 235
blocked_by: []
relates: [PW-1505, PW-692, PW-805, PW-1503]
refs: ["planet/lineages/trade.py::NEED", "planet/lineages/trade.py::GOODS", "planet/lineages/trade_flow.py::FOODS", planet/lineages/bought_in.py, docs/review/culture/trade/bought_in.md, docs/review/culture/trade/review1.md, docs/review/culture/trade/bought_in/stats.py, "runs 3e0eb4 a24559 1e97dd 07c755"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: the goods ledger makes dried and salted fish on fishing coasts once smoking or salting is known. But no way of life
wants it. trade.py says "dried fish, obsidian and sea-mammal oil: no need written yet". So it never leaves the coast. On all four
stored L7 runs (3e0eb4, a24559, 1e97dd, 07c755), no culture buys dried fish at the present or 5 kyr ago (lane 235,
docs/review/culture/trade/bought_in.md). The culinary brief's "Bought in" line (PW-1505) can therefore never say "salt fish from
the coast". That is one of the ticket's own examples, and a staple of real inland cuisines.

The epic's review already sources salt fish as a trade good: salt "swapped against herring in the Hanseatic" trade
(review1.md, around line 35; maritime row: "herring, salt, grain, furs"). What is missing is a need rule: who wants it, at what share.

If it is never done, every inland culture's brief keeps showing no preserved fish, however close the fishing coast and however old its
salt trade.

- [ ] a sourced NEED entry for dried_fish (e.g. towns and farmers within reach of a fishing coast, or fasting-rule faiths; source the
  share from the literature, not from memory)
- [ ] on the judge runs: dried fish flows exist, with the median km and the road reported; the other goods' flows are compared with
  main (the walk is shared)

## Updates
- 2026-11-09: Created from inbox draft draft-trade-dried-fish-no-want.md (found by lane 235).
