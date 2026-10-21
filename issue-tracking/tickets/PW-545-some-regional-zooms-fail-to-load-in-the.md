---
id: PW-545
title: Some regional zooms fail to load in the viewer
type: task
status: done
parent: null
milestone: v1
subsystem: viewer
effort: s
impact: high
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-21
updated: 2026-10-21
---

## Description
Owner (2026-10-21): zooms fa7d30 and f0251b on world 3e0b0a, and 360551 on world c00ebf, don't load (e.g. /viewer/?world=3e0b0a.json&tab=zoom&zoom=fa7d30). Files on disk look complete; fa7d30's satellite.png is only 1840 bytes. Find the cause and fix it.

## Updates
- 2026-10-21: Status todo -> done. Cause: planet/humanuse.py left the harbour class map out of a zoom with no coast (or sea), and viewer/zoom.html huMarkers/hover index L.harbour[i] unconditionally, so the load died with 'Cannot read properties of undefined (reading 0)' at zoom.html:574. fa7d30, f0251b and 360551 are all coastless (no harbour layer in zoom.json); fa7d30's 1840 byte satellite.png is just a uniform white (ice) image, not corruption. Fix: harbour map always emitted (all 0) in zoom and world analyses; regression test test_inland_zoom_still_has_the_harbour_map. Existing zooms need 'planet humanuse zoom:<id>' (in place, no rebuild).
- 2026-10-21: Created.
