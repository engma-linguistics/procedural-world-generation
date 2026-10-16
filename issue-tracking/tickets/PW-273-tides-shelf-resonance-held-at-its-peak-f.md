---
id: PW-273
title: "Tides: shelf resonance held at its peak for every shelf wider than a quarter wavelength"
type: task
status: done
parent: PW-245
subsystem: coast
effort: xs
impact: low
found_by: audit-coast-zoom
blocked_by: []
relates: [PW-076]
refs: [planet/coast.py, tools/coast_check.py, docs/review/audit/coast-zoom.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`coast.py:441` `amp = 1/sqrt(cos(min(kW, pi/2))^2 + r^2)`: past λ/4 the amplification stays at its peak 1/r = 3.3,
and only the friction exponential (L_SHELF_FRIC) brings it down. In the linear model it falls back toward 1
near λ/2. λ is computed from the coast cell's own depth (clipped 20-150 m, coast.py:376), not the shelf's
mean, so λ/4 is often only 150-300 km and many wide shelves are held at full resonance.

Fix: drop the `min` (the r term already bounds the peak) and use the shelf's mean depth along the
coast-to-break path for λ. Re-run coast_check (Patagonia, NW Australia, Yellow Sea, Siberian shelves).
- [ ] no clamp on kW; coast_check tide rows reported before and after

## Updates
- 2026-10-15: Status in-progress -> done. Done in the coast-zoom fix branch (merged d4e7c90); docs/review/audit/fixes-coast-zoom.md.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-coast-zoom-shelf-resonance.md (found by audit-coast-zoom).
