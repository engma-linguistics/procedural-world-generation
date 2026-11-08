---
title: "Trade routes shift under the land nudge: route stretches keep only 0.57-0.73 of themselves (bar ~0.7)"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 214
blocked_by: []
relates: [PW-1504, PW-1503]
refs: [docs/review/culture/trade/step3.md, "planet/lineages/trade_routes.py::Loads.finish", "planet/lineages/trade_routes.py::ROUTE_SHARE", "planet/lineages/trade_flow.py::_Frame", "run 0141d1", "run 3e0eb4", "run 07c755"]
---

## Description
In plain words: trade step 3 draws routes where at least 2% of the world's trade in a kind of goods passes. When every land value and
every cell's people are nudged by up to 10% (the judge's land nudge), the set of route stretches keeps only 0.68 / 0.73 / 0.57 of itself on
0141d1, 3e0eb4 and 07c755 (Jaccard, every third era; minimum per era 0.08-0.21). The bar was ~0.7. The trading towns hold better (0.71-0.89),
and the routes hold under a ±10% nudge to the costs (0.78-0.89). Baseline: before step 3 there were no routes.

Why (likely, not proven): the nudge changes which culture is the biggest on a cell (`_Frame.own`, the carrier), so borders, tolls and the
ways move, and the hard 2% cut then drops or adds whole stretches.

If it is never done, the globe's Trade routes overlay will show a route in one world and not in an almost identical one, which reads as a
real difference.

What to try: draw strength continuously and judge with the load-weighted Jaccard; or keep a route whose share is between 1% and 2% if it was a
route the era before (hysteresis); or pick a cell's carrier by the smoothed share of its people rather than the single biggest culture.
- [ ] route stretches Jaccard ≥ ~0.7 under the land nudge on the three judge runs, with the cost-nudge numbers kept
