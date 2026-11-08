---
title: "Trade: a sourced port-call cost does not thin the long-haul network (1,805-2,310 stretches an era); which lever, if any?"
type: task
status: needs-decision
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 224
blocked_by: []
relates: [PW-1522, PW-1515]
refs: [docs/review/culture/trade/step4a.md, docs/review/culture/trade/step4a/judge.py, "planet/lineages/trade_flow.py::HANDLE", "planet/lineages/trade_flow.py::SEA", "planet/lineages/trade_flow.py::FALL_KM", "planet/lineages/trade_flow.py::FLOOR", "planet/lineages/trade_routes.py::ROUTE_SHARE", "run 3e0eb4", "run 0141d1", "run 07c755", "Page 2026 J. Maritime Archaeology 21", "ORBIS v1 paper (Scheidel, Meeks & Weiland 2012)"]
---

## Description
In plain words: lane 224 added a sourced cost for every port call (2 ship-days to load, 4 to unload, a 2.5% harbour due; step4a.md
section 2). It changed almost nothing: on 3e0eb4 the long-haul layer is 1,808 stretches an era without it and 1,805 with it; spices
still travel a median ~11,500 km, nearly all by sea. A port call costs ~21 pack-animal km plus the due, while a precious good may be
carried ~5,500 pack-km (by ship ~150,000 km) before the 1% cut-off. With the new craft goods the long-haul layer is 1,840 / 1,810 /
2,310 stretches an era on average (3,600-5,000 at the present) on 0141d1 / 3e0eb4 / 07c755, so the default overlay is crowded.

If nothing is done, the "Trade routes" overlay keeps drawing a dense sea web of fine goods, and a reader cannot see the few trunk routes
the Silk Road picture asks for.

Options:
- A: leave it (Indian Ocean and Mediterranean luxury trade did reach most coasts).
- B: a fall-off length for sea hauls of its own (precious goods' 1,200 pack-km is set from Kanesh's donkeys; sea voyages had other
  limits: season, risk). Needs a source for sea losses or voyage risk.
- C: a display bar only: draw the long-haul stretches above a higher share (e.g. 15%) in full and the rest faint, as the local layer is.
  No model change; steadiness is judged on the drawn set.
Lean: C now (cheap, honest about what the model says), B only with a source.

## Acceptance
- [ ] A ruling; if B or C, long-haul stretches per era and land-nudge steadiness on the three runs, before and after.
