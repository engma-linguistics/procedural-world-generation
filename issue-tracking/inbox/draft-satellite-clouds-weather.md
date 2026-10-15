---
title: Satellite clouds are a fixed noise pattern; give them weather-like shapes
type: task
status: todo
parent: null
subsystem: viewer
effort: m
impact: low
found_by: satview
blocked_by: []
relates: [PW-083, PW-156]
refs: [viewer/index.html, viewer/zoom.html]
---

## Description
The Clouds overlay (PW-083) thresholds fractal noise at each place's seasonal cloud share
(`cloud_jul`/`_jan`), so the cover matches the climate but the shapes are generic blobs: no ITCZ band
structure, no frontal spirals in the westerlies, no marine stratocumulus sheets off cold coasts, no
cumulus fields over tropical land. Ideas: stretch and warp the noise along the July/January winds
(the world stores them), use flatter, brighter sheets where low cloud dominates (cold SST, subsidence)
and smaller cells over warm land; or wait for day-scale weather (PW-156) and draw its clouds.
The zoom's clouds use separate noise from the globe's (they don't line up with the globe's patches).
