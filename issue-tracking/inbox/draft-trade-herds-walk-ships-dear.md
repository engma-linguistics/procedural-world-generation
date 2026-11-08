---
title: "Trade: horses and herds go by ship as cheaply as cloth; they should walk, and be dear to ship"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 225
blocked_by: []
relates: [PW-1522]
refs: [docs/review/culture/trade/step4b.md, docs/review/culture/trade/step4a.md, docs/review/culture/trade/review1.md, "planet/lineages/trade_flow.py::_Frame.cost", "planet/lineages/trade_flow.py::FALL_KM", "planet/lineages/trade.py::GOODS", "run 0141d1", "run 3e0eb4", "run 07c755", "Yule, The Book of Ser Marco Polo vol. 2 p. 405 (Wassaf)"]
---

## Description
In plain words: after lane 225, horses still travel a median 1,600-2,800 km between cultures (far tenth ~4,200-4,700 km) and herd
animals 1,400-2,200 km, a third to a half of it by ship (step4b.md section 3). The sources say horses went mostly overland, driven on
their own feet: the Tea Horse Road (over 1,000 km), the Nogai's 20,000-80,000 horses a year to Russia (review1.md). The sea case is the
Gulf-to-India trade, ~10,000 horses a year at 220 dinars each (Wassaf, in Yule's notes to Marco Polo), ~3,000 km, a dear and special
trade. A reader sees horses shipped across oceans as a routine middling cargo.

Why: the model carries live animals like any middling good: a porter's or pack animal's freight on land (they walk themselves, so it
should be cheaper) and ORBIS's cargo freight at sea (a horse needs room, fodder and water, so it should be dearer).

What to try: a drove mode for livestock and horses on land (the herders' own pace and cost, as PW-1511 B's fetch uses pack-animal cost
for herders) and a sea cost per head from a source on horse transports (the cost or capacity of a horse ship), not a tuned factor.
Check horses' median and far tenth against step4b.md section 2 (mostly overland ~1,000 km; the sea case ~3,000 km) and the land-nudge
steadiness on the three runs.
