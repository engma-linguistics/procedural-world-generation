---
title: "Coast classes on Earth: 6 of 32 anchor places miss (Cornwall, Bunda Cliffs, Korea flats, Mississippi, Belize, Namibia seals)"
type: task
status: todo
parent: PW-097
milestone: v2
subsystem: coast
effort: s
impact: low
found_by: coast-detail
blocked_by: []
relates: [PW-097, PW-074, PW-323]
refs: [planet/coastform.py, tools/coast_check.py, "world 577526"]
---

## Description
`uv run python tools/coast_check.py 577526` (Earth, L6): 26/32 named places right. Misses and their causes:
- Cornwall -> tidal flats (Bristol Channel's big tides on a low 110 km cell); cliffs need relief the cell
  averages away.
- Bunda Cliffs -> beach: Southern Ocean waves too weak on that coast (PW-074).
- Korea west coast -> beach/cliff: relief too high for the low-coast rule, mud not quite >= 0.5.
- Mississippi -> salt marsh/barrier: salt marsh comes before delta in the class order; its mouth cell's load
  is under 300 kg/s at L6.
- Belize -> 0.7% reef next to the coast, under REEF_PCT 0.75 (Earth rock map's shale shelves, see PW-323).
- Namibia seals 0.32: warmest-month SST at the edge of the 25 -> 18 C ramp.
An anchor, not a target: only fix where a cause is physical (PW-074 waves), not by moving thresholds.
