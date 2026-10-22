---
id: PW-513
title: "Run ice coast_loss (PW-465): fixed margin thickness, cheap shallow coasts, and newly exposed marine coast charged a climate update late"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: tectonics
effort: m
impact: med
found_by: pw465
blocked_by: []
relates: [PW-465, PW-464, PW-452]
refs: [planet/icemass.py, planet/tectonics/earth.py, docs/review/audit/PW-465-side-lane.md]
created: 2026-10-21
updated: 2026-10-21
---

## Description
The side lane's `earth.coast_cost` / `icemass.coast_loss` (only if PW-465's branch merges) makes three
approximations:
1. Every coastal cell's ice is a margin cell's Nye mean (~740 m at L6), so the flow across the coast
   (~h^8) ignores the sheet's real coastal thickness (the zoom started from 920-1040 m on the
   moments measured, and the snow and soft-ice factors).
2. Beside shallow water the charge is now the zoom's flow (~1e3-5e4 m2/yr per m), often below the old
   flat 5e4. That is the zoom's own rule, but on seed 7 the cold era deepens from -362 to -745 m
   (7/10 seeds pass instead of 8/10). Check whether seed 7's -745 m holds in a time zoom (the
   zoom-mean tool, PW-467) before tuning anything.
3. A trimmed coastal cell on a floored marine bed becomes sea only at the next climate update, so its
   inland neighbour pays its coast one update late.
- [ ] tz_mean on seed 7 @ ~320 Myr: the zoom's mean against the run's -745 m
- [ ] coastal thickness from the pass's own Nye surface (sheet_surface) if (1) matters

## Updates
- 2026-10-21: Created from inbox draft draft-coast-loss-approximations.md (found by pw465).
