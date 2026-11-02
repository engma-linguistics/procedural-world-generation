---
id: PW-1289
title: Sea-floor sediment creep - which K and depth law to keep
type: task
status: needs-decision
parent: null
milestone: null
subsystem: surface
effort: s
impact: med
found_by: lane-100c
blocked_by: []
relates: [PW-950]
refs: [planet/surface.py, planet/tectonics/params.py, docs/review/tectonics/margin/diagnosis-foreset.md]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: lane 100c made the sediment on the sea floor creep slowly downhill (`slope_k`, off by default). This
turns the one-cell cliff at the continent's edge into a slope and puts sediment on the lower slope and the rise. How
fast it creeps (K) is only known to within a factor of about ten from the sources, and how fast it slows with depth
is extrapolated. Someone has to pick the value we keep.

What the sources give (read in lane 100c, see the addendum in diagnosis-foreset.md):
- Jordan & Flemings 1991 (as the Strata tutorial reports it): marine K of 100-1000 m2/yr, i.e. 100-1000 km2/Myr.
- Simon et al. (EGU 2018 and 2019 abstracts, Ogooue and Zambezi deltas): 0.01-10 km2/kyr measured, and strongly
  dependent on slope.
- Mitchell & Huthnance 2008: K ~ 1/depth on the sandy uppermost slope (above ~400 m), with no absolute value given.
  Below 400 m the 1/depth law is our extrapolation.

Options:
- A. K0 = 300 km2/Myr (the log-middle of Jordan & Flemings), with `K = K0 200/(d + 200)`.
- B. K0 = 1000 km2/Myr (the top of that range): a smoother margin, but the shelf loses more of its sediment to the slope.
- C. Keep it off until a slope-dependent (non-linear) K, as Simon et al. measured, is built.

Lean: A, or whichever arm the lane 100c screens and judge favour. The numbers are in the lane 100c report.

## Updates
- 2026-11-01: Created from inbox draft draft-marine-diffusivity-k-and-depth-law.md (found by lane-100c).
