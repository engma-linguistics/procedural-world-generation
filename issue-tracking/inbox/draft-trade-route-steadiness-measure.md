---
title: "Trade routes: the hard 5% route cut on hundreds of stretches keeps the land-nudge steadiness near 0.5-0.65 whatever the source side does"
type: task
status: needs-decision
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 218
blocked_by: []
relates: [PW-1514, PW-1515]
refs: [docs/review/culture/trade/step3c.md, docs/review/culture/trade/step3b.md, docs/review/culture/trade/step3b/judge.py, "planet/lineages/trade_routes.py::Loads.finish", "planet/lineages/trade_routes.py::ROUTE_SHARE", "planet/lineages/trade_flow.py::_Frame.pools", "planet/lineages/trade_flow.py::TRUNK", "run 0141d1", "run 3e0eb4", "run 07c755"]
---

## Description
In plain words: when the land and its people are nudged by up to 10%, the globe's trade routes keep only about half to two thirds of
their stretches (land-nudge Jaccard 0.64 / 0.60 / 0.50 on 0141d1 / 3e0eb4 / 07c755 with lane 218's market pools; main c2e54f2b 0.59 /
0.70 / 0.49; the bar is ~0.7). Three source-side fixes are now measured (lane 216's hold and span, lane 216b's carrier check, lane 218's
market pools), and worn ways made it worse (0.65 / 0.51 / 0.48). None reaches the bar on all three runs.

What is left is the drawing rule itself: a stretch is a route when it carries 5% of one good's carried volume, over 327-536 stretches an
era. Any small change in volume moves the stretches near the cut in or out, and Jaccard counts a stretch at 4.9% as fully gone. The
load-weighted Jaccard is no better (0.63 / 0.54 / 0.50), because most stretches sit near the cut.

If it is never decided, PW-1514 stays open forever. Every trade lane will keep trying source-side mechanisms against a bar that the
drawing rule, not the trade model, holds down. Meanwhile the overlay keeps showing differences between near-identical worlds that a
reader will take as real.

Options for Daniel:
- A: judge steadiness on the strongest routes only (for example the top 50 stretches by strength an era, or stretches over twice the
  cut). These are the trunks a reader looks at.
- B: draw routes by a continuous strength (line width and fade by strength, no cut) and judge with the load-weighted Jaccard.
- C: keep the cut and the bar, and keep looking on the source side (pool every settled cell, not only those within 1.5 spacings of a
  town).
- [ ] a ruling on how route steadiness is drawn and judged
