---
title: "PW-284 lean B not landed: full two-sided flexure lifts grid-scale crust spikes to 14-40 km"
type: task
status: needs-decision
parent: PW-245
subsystem: tectonics
effort: m
impact: med
found_by: audit-fix-tectonics
blocked_by: []
relates: [PW-284, PW-054, PW-172, PW-243]
refs: [planet/tectonics/isostasy.py, planet/tectonics/crust.py, planet/tectonics/plate_kernels.py, "run:a1d3b9@900Myr"]
---

## Description
PW-284's approved lean (share 1, both halves of the flexure, volume kept,
FLEX_KM the only knob) was implemented as `dyn += root - smooth(root, km)`
(smooth rescaled so the sum is exactly zero, no MOAT_MAX cap) and tested.
It is not viable on today's crust field, so the code still has the 0.15
moat-only share.

Why: collision belts carry single-cell crust spikes (80 km cells next to
40-48 km ones, at the plate boundary where stacking lands). An elastic
plate holds a load narrower than its flexural width up almost in full, so
the bulge half lifts each spike by nearly its whole Airy root (up to 38 km).
- Static, on a1d3b9's 900 Myr state (L7): uplift max 36 km (FLEX_KM 150),
  34 (75), 31 (50); 33-156 cells above 9.5 km; moats to -26..-28 km in
  oceanic holes inside belts. Land 33.3% -> 27.5% (150), 31.2% (75).
- Dynamic replays (L7, 900-930 Myr): max elevation 14 km (150 and 75 km),
  10.4 km at 50 km (dyn +2-3 km on belt cells).
- L6 seed 1, 0-300 Myr with FLEX_KM 150: mean max elevation 40 km, dyn
  -19..+32 km, land 34.2% -> 28.7%.
So the physics is right but the load field isn't: nature never makes a
55-110 km wide, 45 km thick excess column, because the crust flows or
collapses first. In the model, crust_flow (thickness-driven, flux-limited
at 0.15, and only inside one plate's continent) doesn't remove spikes that
stacking rebuilds every step at the boundary.

Options:
- (A) Fix the load first: make collision stacking and crust flow keep the
  belt smooth at the grid scale (spread stacked crust across the boundary
  to both plates' belts; let flow cross the suture-to-be; or drive flow by
  the flexed elevation). Then land full flexure as approved.
- (B) Keep the moat-only form but call it what it is: a calibrated
  basin-making share (the audit's option A).
- (C) Two-sided flexure on a load smoothed at the flexural width (the
  plate responds only to belt-scale loads; grid-scale relief is carried
  locally). Spike-safe, volume-kept, but the extra smoothing has no
  physical derivation.
Lean A (effort m), then B's honest docstring until it lands.
