---
id: PW-1371
title: "Dwarven holds buy food with a placeholder trade share (ladder.TRADE_CAP 0.5): replace when trade exists"
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: m
impact: low
found_by: lane 136 / lane 137 (density ladder build)
blocked_by: []
relates: [PW-1275, PW-1350]
refs: ["planet/lineages/ladder.py::TRADE_CAP", "planet/lineages/ladder.py::TRADE_FULL", "planet/lineages/ladder.py::MUSHROOM_X", "planet/lineages/ladder.py::Ladder.line", "planet/lineages/ladder.py::is_hold", docs/review/peoples/density-ladder/ladder.md, docs/review/peoples/density-ladder/build.md, "Clark 1999 UC Davis notes ch. 4", "Ramos et al. 2010 NPT 4(3)"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
Q6 A (PW-1350): a hold's density is its valleys' farming rung plus food bought with ore and craft, up to a cap, plus a small mushroom
bonus. There is no trade model yet, so `ladder.py` uses a placeholder: the hold buys `TRADE_CAP` (0.5) of its food where the best metal
good reaches `TRADE_FULL` (0.6), so density = farming / (1 - trade) x 1.1. Neither number is sourced: they stand in for a market that
does not exist. In the lane 137 dnd runs the dwarves' hold rung is the densest rung after irrigation (see build.md's results).

When trade exists: the food a hold buys should come from a neighbour's surplus within reach, priced by its ore and craft, and the cap
should fall out of that. Until then the placeholder stays, labelled as one in the ladder's table and the workbench.

## Updates
- 2026-11-02: Created from inbox draft draft-hold-trade-placeholder.md (found by lane 136 / lane 137 (density ladder build)).
