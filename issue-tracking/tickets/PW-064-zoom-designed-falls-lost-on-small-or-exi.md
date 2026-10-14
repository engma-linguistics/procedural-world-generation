---
id: PW-064
title: "Zoom: designed falls lost on small or exiting rivers; close cascades unlisted"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: falls
blocked_by: []
relates: []
refs: [planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
A designed step is lost if the zoom's river carries under 30% of the coarse discharge or the reach leaves
the region (e.g. a 256 m step on a 1,215 m³/s stream). `waterfalls()` keeps falls ≥15 km apart, so close
cascades go unlisted.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Highlights (falls).
