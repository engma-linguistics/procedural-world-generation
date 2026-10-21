---
id: PW-528
title: Loess only comes from outwash plains, wet or dry, not from deserts
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: pw497
blocked_by: []
relates: [PW-497, PW-096]
refs: ["planet/timezoom/sim.py (drop)", planet/timezoom/deposit.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-497's loess is a fixed share (`silt_share`, 0.5) of the outwash laid down on ice-free land each step,
carried along the cold half-year's wind (`wind_w`). It does not look at how dry or bare the plain is,
and desert loess (dune and playa sources, PW-096) is not done. The wind is only the cold-season mean,
not the glacial anticyclone's katabatic winds, which the grid does not resolve.
What to try: scale the lift by a dryness term from the frame's precipitation and vegetation; add a
source from the world's desert/dune cells; keep the volume bookkeeping (loess layer, rock_isostasy).
- [ ] loess also downwind of the Sahara / Gobi analogue

## Updates
- 2026-10-21: Created from inbox draft draft-loess-from-deserts-and-dryness.md (found by pw497).
