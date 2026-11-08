---
id: PW-1514
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
created: 2026-11-08
updated: 2026-11-08
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

## Updates
- 2026-11-08: Created from inbox draft draft-trade-routes-land-nudge.md (found by lane 214).
- 2026-11-08: Lane 216 (docs/review/culture/trade/step3b.md): hysteresis (last era's routes hold down to half the bar) and a span (stretches over half the bar that continue a route), with per-good shares. Land-nudge Jaccard 0.59/0.69/0.48 (main cb8374b0 with the same rebuilt judge: 0.45/0.55/0.47; lane 214's own judge said 0.68/0.73/0.57, the draws differ). Cost nudges 0.82, 0.75 / 0.81, 0.73 / 0.73, 0.68 (main 0.87, 0.85 / 0.78, 0.83 / 0.83, 0.73), so the cost numbers are not kept. Bar not met. Next: the carrier smoothed by the people's share (`_Frame.own`), which the hold does not touch. Stays open.
- 2026-11-08: Lane 218 (docs/review/culture/trade/step3c.md): market pools built and kept (`trade_flow.POOL`, `_Frame.pools`, `_exchange`): each town's hinterland (nearest town by cost, at most 1.5 spacings) meets its own wants first, and only the pool's net travels, from the town. Land nudge 0.64 / 0.60 / 0.50 (main c2e54f2b, same judge: 0.59 / 0.70 / 0.49); cost nudges 0.82, 0.77 / 0.68, 0.73 / 0.72, 0.65 (main 0.82, 0.74 / 0.81, 0.71 / 0.71, 0.68), worse on 3e0eb4 and 07c755. Worn ways (switch TRUNK) made it worse (0.65 / 0.51 / 0.48). Bar not met. Left: unpooled cells where towns are sparse (older eras), pool nets crossing zero, and the hard 5% route cut on hundreds of stretches (draft draft-trade-route-steadiness-measure.md). Stays open.
