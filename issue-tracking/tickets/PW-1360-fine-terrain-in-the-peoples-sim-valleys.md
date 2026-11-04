---
id: PW-1360
title: "Fine terrain in the peoples sim: valleys, passes and mountains from the land zoom used inside the history, not only drawn after"
type: epic
status: todo
parent: null
milestone: later
subsystem: zoom
effort: xl
impact: high
found_by: owner
blocked_by: []
relates: [PW-1299, PW-1296]
refs: [planet/zoom/tiling.py, planet/zoom/match.py, docs/review/land-zoom/cost.md, planet/lineages/history/model.py]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: owner 2026-11-02 (v3): let the peoples sim use real local geography (village valleys, the dwarves' actual mountains, passes) rather than only coarse cells. Feasible as sub-cell summaries: a land sweep (4 km/px is far cheaper than 1 km) writes per-cell numbers (arable valley-floor area, flat land near water, pass connectivity, defensible sites, mineral outcrops) that the history reads; settlements then pick real sites. A full 1 km history is out on time and RAM. A super-detailed slow mode is a later possibility.

## Updates
- 2026-11-03: Milestones 11-03: v3 -> later: v3 is now states and war v0; this waits for after v1.0
- 2026-11-02: Created.
