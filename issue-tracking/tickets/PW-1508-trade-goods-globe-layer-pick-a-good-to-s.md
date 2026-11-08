---
id: PW-1508
title: "Trade goods globe layer: pick a good to see where it is spare and where it is lacking"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: viewer
effort: s
impact: med
found_by: lane 212
blocked_by: []
relates: []
refs: [docs/review/culture/trade/step1.md, "planet/lineages/trade.py::cells_at", "planet/lineages/trade.py::ledger_at", "planet/server.py::trade"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: the goods ledger (step 1) is shown per culture in the workbench, but not yet on the globe. The design
(design1.md step 1) also asks for a globe layer: pick a good, and the map shows surplus in green and lack in red, with the time slider.

Lane 212 built the ledger and left this out to keep the step small. The per-cell surplus and lack are already worked out inside
`trade.ledger_at`, before it sums them to cultures. Expose them per frame (a PNG like faithmap, or a layer the viewer loads), and add
a picker under Overlays.

- [ ] /api/trade?run=&good=&frame= gives the per-cell surplus/lack map
- [ ] Overlays > Trade goods: a good picker, green for surplus and red for lack, following the time slider

## Updates
- 2026-11-08: Created from inbox draft draft-trade-goods-globe-layer.md (found by lane 212).
- 2026-11-07: Drafted by lane 212.
