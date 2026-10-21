---
id: PW-540
title: "Family breadcrumb stops at the regional zoom: fine zooms nested in a zoom (e.g. 50 m in 500 km) don't show in the top Family view"
type: task
status: todo
parent: null
milestone: v1
subsystem: viewer
effort: s
impact: med
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-21
updated: 2026-10-21
---

## Description
Owner 2026-10-21: the top Family/navigator bar (viewer/navigator.js, planet/family.py, /api highlight/family endpoints) shows Planets > Run > Time zoom > Finished world > Zoom 500 km, but a fine zoom nested in that zoom (and fine-in-fine) never appears. Show the whole chain to the deepest level, with the selected fine zoom highlighted and its siblings reachable, the same way the other levels work.

## Updates
- 2026-10-21: Created.
