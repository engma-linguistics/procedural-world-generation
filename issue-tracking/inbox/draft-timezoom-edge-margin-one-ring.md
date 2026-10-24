---
title: "Time zoom's 'edge' margins are one ring of cells at any level, as the run's were before PW-725: at L7 the band melting as the sheet's edge is half as wide as at L6"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: v1-finish-3
blocked_by: []
relates: [PW-725, PW-460, PW-555]
refs: [planet/timezoom/sim.py, planet/tectonics/earth.py, docs/review/base-climate/v1-finish-3/]
---

## Description
PW-725 found the run's ice resolution-dependent: the margin band whose snow and melt are the sheet's edge's
(edge_h, ~400 m) was the ring of iced cells next to bare land, so ~120 km wide at L6 and ~60 km at L7. The same
planet at the same dT grew ~2x the iced land and ~3x the ice at L7 from its first climate update (89c2ab @ 700 Myr,
dT 0: -100 m against L6's -28 m). The run now takes the band in km (`earth.margin_band`, MARGIN_KM = 120: one ring
at L6 and coarser, two at L7), which brings the two levels within ~15% across dT -3..+2.

The time zoom's `margin="edge"` mode (`planet/timezoom/sim.py` prepare_surface, the default, "the run's rule")
still takes one ring: an L7 time zoom's margins melt as the edge over 60 km where an L6 one's do over 120 km, so its
sheets should run bigger at L7 the same way. Not changed in PW-725 (the time zoom's ice is the v1 glacial-index
draw, PW-471, and has its own checks); left for whoever owns the time zoom.

- [ ] Measure: the same run's time zoom at L6 and L7 (or the eqcurve.py approach on the zoom), sheet area and
  sea level at the glacial and interglacial.
- [ ] If it differs, use `earth.margin_band` for the 'edge' mode so it stays the run's rule; or take the ramp
  (PW-460) in both, which retires the band.
