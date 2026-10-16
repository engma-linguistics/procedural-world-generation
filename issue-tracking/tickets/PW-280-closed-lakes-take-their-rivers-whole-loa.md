---
id: PW-280
title: Closed lakes take their rivers' whole load even when full, piling sediment up to 1 km above the lake surface
type: task
status: done
parent: PW-245
subsystem: surface
effort: s
impact: med
found_by: audit-surface-hydro
blocked_by: []
relates: [PW-054]
refs: [planet/surface.py, docs/review/audit/surface-hydro.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Rivers end at closed-lake cells (route makes them outlets), so `_route` leaves all their load there. The
closed-lake spread (surface.py:276-281, dep proportional to depth + 1) has no cap at the lake's room. L5 run,
seed 1, 300 Myr: in 26% of closed-lake cell-steps the floor ends > 1 m above the lake surface (worst 1213 m), 2.0%
of all deposition. Open lakes are capped (`pool_room`). A full basin should spill: once its hollow is full, the
rest goes over its outlet. Instead it becomes a sediment mound that can dam the land next to it.
Fix: cap the closed-lake share at the lake's summed `pit_room`. Put the excess on the lowest rim cell, or route it
from the spill cell, so the basin opens next step. Mass stays conserved.
- [ ] no closed-lake cell raised above its lake level by deposition; budget still closes

## Updates
- 2026-10-15: Status in-progress -> done. Done in the surface-hydro fix branch (merged 4d3b46f); docs/review/audit/fixes-surface-hydro.md.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-surface-hydro-closed-lake-overfill.md (found by audit-surface-hydro).
