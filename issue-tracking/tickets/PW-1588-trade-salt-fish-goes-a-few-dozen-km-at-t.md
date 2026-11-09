---
id: PW-1588
title: "Trade: salt fish goes a few dozen km at the median; stockfish went ~2,000 km, so dried fish may belong with the middling goods"
type: task
status: todo
parent: PW-1498
milestone: null
subsystem: culture
effort: s
impact: low
found_by: lane 244
blocked_by: []
relates: [PW-1573, PW-1505]
refs: ["planet/lineages/trade.py::GOODS", "planet/lineages/trade_flow.py::FALL_CLASS", "planet/lineages/trade_flow.py::FALL_KM", docs/review/culture/trade/bought_in_244.md, docs/review/culture/trade/bought_in_244/cmp.py, "Orton et al. 2016 (Fish for London)", "runs 3e0eb4 a24559 1e97dd 07c755"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: since lane 244 (PW-1573), 43-74 cultures buy salt fish on the four stored L7 runs. But it goes only 27-58 km at the
median, and 126-373 km for the far tenth at the present. It mostly goes overland, by river or as tribute, and seldom by sea (4-21%).
Dried fish is a bulk good (trade.GOODS), so it falls off as fast as grain.

The sources point further:
- London's processed cod came from Arctic Norway from the 13th century (Orton et al. 2016), ~2,000 km [est.];
- the Hanse carried Bergen stockfish and Scania herring across the Baltic and North Sea (review1.md section 4).

Stockfish keeps for years (Wikipedia, Stockfish). It has also lost most of its weight in drying (needs a fetched figure), so its value
per kg is above grain's.

If it is never done, briefs show salt fish only from the next coast, never the long stockfish and herring trade that fed inland towns.
- [ ] fetch a dried-to-fresh weight ratio and a price per kg against grain; if it holds, set FALL_CLASS["dried_fish"] = "middling"
- [ ] the fish median and far tenth, and its roads, against lane 244's numbers

## Updates
- 2026-11-09: Created from inbox draft draft-trade-dried-fish-class.md (found by lane 244).
