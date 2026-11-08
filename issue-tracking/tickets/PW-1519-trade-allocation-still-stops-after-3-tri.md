---
id: PW-1519
title: Trade allocation still stops after 3 tries for every good but grain, so their unmet shares are overstated
type: task
status: todo
parent: PW-1498
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lane 216b
blocked_by: []
relates: [PW-1503, PW-1515]
refs: ["planet/lineages/trade_flow.py::flows_at", "planet/lineages/trade_flow.py::SEEK_GOODS", "planet/lineages/trade_flow.py::ROUNDS", "planet/lineages/trade_flow.py::_rewalk", docs/review/culture/trade/step3b.md, docs/review/culture/trade/step3b/judge.py, "run 3e0eb4", "run 0141d1", "run 07c755"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: when a place short of some good finds its nearest source emptied, it looks for the next one. Grain now keeps looking
until it finds no more (lane 216b, `SEEK_GOODS`); every other good still gives up after 3 tries (`ROUNDS` = 3), a limit set to save
time, not a model number.

Measured on 3e0eb4 (last 8 frames, step3b.md pass 2), with every good allowed 200 rounds: 10 of the 16 goods still hit the 200, and
after 3 rounds the goods had met only 8-72% of what they met by the end (livestock 8%, spices 9%, salt 21%, gold 27%, iron 71%, furs
72%). That run took 305 s for 8 frames, about 6 times main's derive and far over the ~3-minute budget per run, even with the re-walk
limited to the emptied sources' land (`_rewalk`).

If it is never done: the trade panel's "unmet" shares for salt, metals, spices and livestock are overstated (a number a reader will
trust), and routes for those goods are drawn from too little volume.

What to try: a walk that keeps each cell's K best distinct sources (about K times one walk, no per-round re-walk), so a taker cut short
moves to its next source without walking again; re-walk only when its K are all empty.
- [ ] every good's allocation runs until a round finds no more, with only a safety cap
- [ ] derive within ~3 minutes per D&D run (judge: docs/review/culture/trade/step3b/judge.py --quick)

## Updates
- 2026-11-08: Created from inbox draft draft-trade-other-goods-cut-at-three-rounds.md (found by lane 216b).
- 2026-11-08: Lane 218 (docs/review/culture/trade/step3c.md): every good run to the end with the existing rounds: rounds hit the 400 cap (mean 220-240), 306 s for 8 frames of 3e0eb4, and 2,400-3,100 route stretches an era (fine goods 1,300-1,800). The 8-best-sources walk (single greedy pass, re-walk only when all 8 are dry): the walk is ~30x a plain walk (1.6-1.9 s vs 0.06 s) and goods still need up to 50 walks (cap), one frame 615 s. Neither kept; allocation unchanged. Not done. Next: one shared walk in which an emptied source stops spreading (a competitive Dijkstra), and a ruling on how far fine goods' routes should be drawn once they travel to the end.
