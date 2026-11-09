---
title: "Trade: a few grain rows still come 5,000-11,000 km by sea; a further port call per season's leg needs a walk that counts legs"
type: task
status: todo
parent: PW-1498
subsystem: culture
effort: m
impact: low
found_by: lane 244
blocked_by: []
relates: [PW-1572, PW-1505]
refs: ["planet/lineages/trade_flow.py::SEASON", "planet/lineages/trade_flow.py::_seek", "planet/lineages/trade_flow.py::_walk", docs/review/culture/trade/bought_in_244.md, docs/review/culture/trade/bought_in_244/h.py, docs/review/culture/trade/bought_in_244/samp.py, "run 3e0eb4 culture 574", "run 07c755 culture 150", "run 1e97dd culture 741"]
---

## Description
In plain words: lane 244 (PW-1572) gave bulk cargoes a season's capital and risk per season's leg at sea. The far tenth of grain fell to
1,693-2,355 km on the four stored L7 runs, about Egypt to Rome. But a few rows still come very far by sea, at 1-7% of a culture's people:
- 3e0eb4: the tortles of the south of Simath (2) get 6.8% of their grain from the dragonborn of Simath, 11,252 km by sea;
- 07c755: the continental kobolds of the east of Hizam, 11,008 km;
- 1e97dd: the aarakocra of the north of Vazem (2), 9,746 km.

The share of grain weight beyond 5,000 km is still 0.4-4.0% at the present (main 0.4-5.1%).

A reader will trust a brief that says a culture eats grain shipped 11,000 km. No pre-modern grain fleet did that.

The sourced piece still missing is a further port call for each season's leg after the first. A cargo carried past one season's leg is
landed, wintered and reloaded. The walk's cost cannot count legs, because the cost would depend on the sea km already sailed on the path.
Lane 244 tried it in `_walk` and `_seek` (a stage cost when the path's sea km crosses a multiple of SEASON_KM). The shared walk then did
not finish one frame's grain walk in over 3 minutes. The likely cause is that the source-death re-walk assumes path-independent costs.
It was reverted (bought_in_244.md section 2).

Options:
- A: a walk state per leg (cells x legs);
- B: a post-pass that re-prices each delivery by its sea km (dkm per mode is kept) and drops what falls under FLOOR;
- C: accept the tail (it is small).

B looks cheapest.
- [ ] grain's maximum and the share beyond 5,000 km against main on the four runs; herders' grain met reported
