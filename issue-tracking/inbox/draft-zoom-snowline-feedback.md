---
title: "Zoom snowline sits ~2-3 C warmer under coarse ice than beside it (ice feedback by the coarse footprint)"
type: task
status: needs-decision
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomice
blocked_by: []
relates: [PW-127, PW-102]
refs: [planet/zoom.py, tests/test_zoom_ice.py]
---

## Description
The zoom's glacier rule (PW-127) copies earth.ice_sheets: a pixel accumulates ice where its summer is below ice_summer_temp (1 C), with the ice's own feedback (ICE_FEEDBACK x lapse x thickness, plus the white-top cooling) and the melting cap (a positive summer on ice halved) applied wherever the interpolated coarse ice is > 1 m. On a 400 m tropical cap that moves the snowline to a bare-ground summer of ~+4 C (the synthetic test's), while next to it, in a coarse ice-free cell, it stays at +1 C: two snowlines ~400 m apart in height, set by where the coarse cells happen to be. Physically real snowlines (ELA) sit at summer air temperatures from below 0 C (dry, continental) to +5..8 C (maritime, snowy), i.e. they depend on the snowfall, not on the coarse footprint.

Options: (a) keep (consistent with the main run's hysteresis); (b) apply the feedback only to pixels inside the coarse sheet's own zone (no cap/feedback at the coarse ice's fringe); (c) make the threshold depend on snowfall in both the main run and the zoom (a degree-day mass balance only, no fixed summer threshold). (c) touches the main run's ice (PW-102) and its calibration.
