---
id: PW-145
title: Coal measures nearly vanish from surface_rock now that it reads the top stratum
type: task
status: needs-decision
parent: PW-005
subsystem: surface
effort: s
impact: low
found_by: stratarock
blocked_by: []
relates: [PW-136]
refs: [planet/surface.py, planet/tectonics/record.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The old mix rule showed coal measures wherever coal made up more than 3% of
the cover (coal seams are thin; a coal-measures sequence is mostly shale and
sandstone). With PW-136 option B, `surface_rock` is the top stratum, and the
record (record.add_top) folds thin coal deposits into the thicker
sandstone/shale layer they land on, so coal only shows where a coal stratum
is on top. On f59dd6 @ 408 Myr coal went from 7.9% of the land to 0.3%
(most became shale or sandstone).

Options:
- **A.** Accept it (7.9% was high for Earth-like coal-bearing outcrop).
- **B.** Track a coal fraction per stratum (or a flag on layers that grew
  in coal swamps) and show "coal measures" for a top stratum with > 3% coal.
  Needs a record field; touches record.add_top.
Lean: A unless the viewer or highlights miss coal basins.

## Updates
- 2026-10-14: Created from inbox draft draft-coal-measures-display.md (found by stratarock).
