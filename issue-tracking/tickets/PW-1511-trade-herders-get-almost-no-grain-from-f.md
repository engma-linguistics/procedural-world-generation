---
id: PW-1511
title: "Trade: herders get almost no grain from farmers (0.5-5% of their need), because the herders live far from farmland"
type: task
status: needs-decision
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 213
blocked_by: []
relates: [PW-1503, PW-1504, PW-1505]
refs: [docs/review/culture/trade/step2.md, docs/review/culture/trade/review1.md, "planet/lineages/trade_flow.py::FALL_KM", "planet/lineages/trade_flow.py::flows_at", "planet/lineages/trade.py::NEED", "run 0141d1", "run 3e0eb4", "run 07c755"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: the review says herders cannot live on their herds alone and always get grain from farmers (Khazanov 2019,
review1.md section 2). Trade step 2 now moves goods, but on the three judge runs, herder cultures meet only 0.5%, 3% and 5% of their
grain need on average (0141d1, 3e0eb4 and 07c755; baseline: before step 2 nothing moved at all). Where some grain does reach them, it
covers 6-19% of the need.

Why: grain is bulk. Its supply fades as exp(-cost / 290 pack-km): Cato's mill lost 39% of its value in 75 miles (review1.md
section 6). And the herders in these worlds live hundreds to thousands of km from farmland. In 0141d1's present frame, four of the
six biggest goliath herder cultures have no farm grain within reach at all, and the biggest one's grain comes from a median 4,000 km.
The world has twice as much grain to spare as it lacks, so the shortfall is distance, not supply.

If this is never decided, step 4a's culinary brief will say steppe herders eat almost no bought grain, and step 4d would starve
herders that the history now feeds.

Options:
- A. Keep it. Herders far from farmers really do go without; only the herders on the steppe edge trade.
- B. Herders fetch it themselves. The review says nomads drove their own herds to frontier markets (Khazanov), and Tuareg caravans
  took millet out and salt back (Bradshaw). So a herder taker's walk uses its own animals: pack-animal cost on any land it or its
  neighbours hold, even without the `pack_animals` tech. This is one mode rule, with no new number.
- C. Wait for step 3 (PW-1504). Frontier towns where steppe meets farmland become market hubs, and herders buy there.

**My lean: B, then check it against C once step 3 has hubs.** B is a mechanism the source names. It costs nothing at runtime.

## Updates
- 2026-11-08: Created from inbox draft draft-trade-herders-grain-far.md (found by lane 213).
