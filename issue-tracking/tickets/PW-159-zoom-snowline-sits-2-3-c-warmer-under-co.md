---
id: PW-159
title: Zoom snowline sits ~2-3 C warmer under coarse ice than beside it (ice feedback by the coarse footprint)
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomice
blocked_by: []
relates: [PW-127, PW-102]
refs: [planet/zoom.py, tests/test_zoom_ice.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
The zoom's glacier rule (PW-127) copies earth.ice_sheets: a pixel accumulates ice where its summer is below ice_summer_temp (1 C), with the ice's own feedback (ICE_FEEDBACK x lapse x thickness, plus the white-top cooling) and the melting cap (a positive summer on ice halved) applied wherever the interpolated coarse ice is > 1 m. On a 400 m tropical cap that moves the snowline to a bare-ground summer of ~+4 C (the synthetic test's), while next to it, in a coarse ice-free cell, it stays at +1 C: two snowlines ~400 m apart in height, set by where the coarse cells happen to be. Physically real snowlines (ELA) sit at summer air temperatures from below 0 C (dry, continental) to +5..8 C (maritime, snowy), i.e. they depend on the snowfall, not on the coarse footprint.

Options: (a) keep (consistent with the main run's hysteresis); (b) apply the feedback only to pixels inside the coarse sheet's own zone (no cap/feedback at the coarse ice's fringe); (c) make the threshold depend on snowfall in both the main run and the zoom (a degree-day mass balance only, no fixed summer threshold). (c) touches the main run's ice (PW-102) and its calibration.

## Updates
- 2026-10-15: Status in-progress -> done. Merged (icemb).
- 2026-10-15: Status todo -> in-progress. Worktree icemb (decision C).
- 2026-10-15: Not done in vegzoom: the agreed fix is in earth.ice_sheets (ice agent's file tonight). Pick up after the ice merge.
- 2026-10-14: Status needs-decision -> todo. Coordinator decision (owner's north star): no half measure; make the snowline depend on snowfall and summer warmth consistently in both the run (earth.ice_sheets) and the zoom, with the height feedback applied only on the sheet itself.
- 2026-10-14: Created from inbox draft draft-zoom-snowline-feedback.md (found by zoomice).
