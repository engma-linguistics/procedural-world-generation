---
id: PW-857
title: Peoples track lines are range centroids, so a multi-patch people's line wanders at sea and looks like a migration
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner saw a meandering pink line (likely the tabaxi, #ff69b4, 44 patches round the equator) in b69f51. viewer/index.html:1680-1726 draws meta.lineages[].track, the presence-weighted centroid per frame (history.py:1202-1209). Show a largest-patch or per-patch track, snap to land, or label it 'range centre'.

## Updates
- 2026-10-25: Owner: don't draw the range-centre track at all unless it's useful to us; remove the overlay.
- 2026-10-25: Created.
