---
id: PW-276
title: "Run ice: the Nye thickness is stacked on the bed, so caps on high ranges reach 9 km surfaces (cause of PW-226)"
type: task
status: done
parent: PW-245
subsystem: tectonics
effort: s
impact: med
found_by: audit-ice-veg
blocked_by: []
relates: [PW-226, PW-240]
refs: [planet/tectonics/earth.py, docs/review/audit/ice-veg.md, tests/test_invariants.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`earth.ice_sheets` (earth.py:275-288) gives each iced cell `sqrt(2 tau/(rho g) x distance from the edge)` of ice
on top of its own bed. Over a range that rises inward from the margin, the surface climbs by the bed's relief plus
the profile. A real sheet's surface rises from its margin's elevation, and the ice over high bed is thinner (it
drains to the sides).

Measured on L5, seed 2, 1000 Myr:
- ice surfaces up to 9.4 km;
- the 33 iced cells above 5 km had a bed of 4.8 km and 2.2 km of ice on average;
- coldest months down to -111 C (11-14 cells below -90 C).

At L4 a cell one hop inside the edge is ~450 km in and gets ~2.3 km of ice: PW-226's cap.

Fix (a simple, sound approximation): carry each sheet's edge-bed height through the BFS from the edge. Take the
surface as `max(bed + margin thickness, bed_edge + Nye(d) x snow x soft)` and the thickness as surface - bed.
Likely effect: high caps thinner, surfaces near 4-5 km, a bit less run ice volume (helps PW-240 a little).
Restore test_values_sane's -95 C bound if it now holds.
- [ ] no run ice surface far above ~5-6 km on L5/L6 seeds 2 and 11; the -95 C bound restored

## Updates
- 2026-10-15: Status in-progress -> done. Done in the ice fix branch (merged 20684ed); docs/review/audit/fixes-ice.md.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-ice-veg-nye-on-high-bed.md (found by audit-ice-veg).
