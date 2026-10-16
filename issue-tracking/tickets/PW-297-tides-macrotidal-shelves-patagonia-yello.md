---
id: PW-297
title: "Tides: macrotidal shelves (Patagonia, Yellow Sea, Khambhat, Channel) low once resonance falls off past lambda/4"
type: task
status: in-progress
parent: null
subsystem: coast
effort: s
impact: low
found_by: fix-coast-zoom
blocked_by: []
relates: [PW-273, PW-076]
refs: [planet/coast.py, tools/coast_check.py, docs/review/audit/fixes-coast-zoom.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-273 replaced the clamp cos(min(kW, pi/2)) with the linear standing-wave response, the shelf's mean
depth for lambda and an interpolated shelf-break position for W. coast_check (L6) tides went from 16 to
12 of 26 in range (24 -> 22 within 2x): Patagonia 5.2 -> 2.2 m (6-11), Yellow Sea 2.3 -> 1.4 (4-9),
Khambhat 7.8 -> 4.2 (6-11), St Malo 6.5 -> 3.3 (5-12), Amazon 5.2 -> 2.1 (3-6). These sat at the clamp's
peak before. At L6 a shelf is 2-5 cells (110 km each) wide, W and the path-mean depth are coarse, and the
real resonances (Patagonia ~lambda/4 on a 100 m, 500 km shelf) land off the peak: at W = 517 km and
h ~100 m the model gives kW ~2.3 rad, amplification 1.2.

To check: the same rows at L7 (shelf widths better resolved); the mean depth along the path vs the
deepest-water route; whether the friction exponential exp(-(W - lambda/4)/L_SHELF_FRIC) double-counts
the friction r already in the response. Don't bring back the clamp.

## Updates
- 2026-10-15: Status todo -> in-progress. Coast batch agent started.
- 2026-10-15: Created from inbox draft draft-tides-macrotidal-shelves-off-resonance.md (found by fix-coast-zoom).
