---
id: PW-101
title: "Microclimate in the zoom: lapse rate, cold pools, local rain shadow, snow line"
type: story
status: todo
parent: PW-090
milestone: null
subsystem: zoom
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: [planet/zoom/regional.py, planet/climate.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
At 1 km pixels, recompute temperature with the lapse rate on the fine elevation, valley cold pools
(inversions), local rain shadows behind ridges, and the snow line. Feeds the zoom's land cover and ice.

## Updates
- 2026-10-14: Created from the owner's world-finishing epic (2026-10-14).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
