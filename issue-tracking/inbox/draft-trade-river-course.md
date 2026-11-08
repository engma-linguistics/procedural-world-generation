---
title: "Trade: river boats jump between neighbouring rivers and over watersheds; following the course costs herders' grain"
type: task
status: needs-decision
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 226
blocked_by: []
relates: []
refs: [docs/review/culture/trade/step4c.md, "planet/lineages/trade_flow.py::RIVER_COURSE", "planet/lineages/trade_flow.py::_Frame", "run 3e0eb4", "run 0141d1", "run 07c755"]
---

## Description
In plain words: the trade model lets a river boat go between any two neighbouring cells that both have a navigable river. Two thirds of
those links do not follow a river: they jump between parallel tributaries or across a watershed. That joins whole river basins into
meshes as big as continents (on 3e0eb4 the biggest has 4,658 cells; following the rivers' own courses the biggest basin has 1,797).
Lane 226 built the fix, `RIVER_COURSE`: a boat goes only down its river's course or up it, using the world's `downstream` links. It is
left off because it costs herders their grain. Herders' grain met falls from 0.0302 to 0.0267, from 0.1264 to 0.0957 and from 0.1227 to
0.1035 on 0141d1, 3e0eb4 and 07c755. Grain had been reaching them through those jumps. Steadiness is fine with it on (0.795 / 0.785 /
0.768). Spices are bounded either way, by the river hands.

Options:
- A: leave it off. It is a known geometry flaw, and grain keeps cheap water carriage between neighbouring rivers. It reads as short
  portages, at boat cost.
- B: turn it on and charge a portage between neighbouring rivers. A land edge between two navigable cells of different rivers would cost
  porter or pack freight, as the ground does now, plus a sourced transshipment (Page 2026's loading and unloading days, step4a.md). This
  is the honest geometry, but herders' grain falls unless something else feeds it.
- C: turn it on and accept the grain loss, then look at why herders depend on river crossings for their grain.

Lean: B. Measure herders' grain with the portage cost, and take C only if B still falls short. The grain bar is the brief's
(not worse than main); that is the judgement call.

- [ ] owner's choice A/B/C
- [ ] if B: a sourced portage cost; herders' grain and the land-nudge steadiness on the three runs
