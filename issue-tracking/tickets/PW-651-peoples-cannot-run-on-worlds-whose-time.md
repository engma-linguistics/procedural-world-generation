---
id: PW-651
title: Peoples cannot run on worlds whose time zoom was deleted (most L6 worlds)
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: viewer
effort: m
impact: med
found_by: viewerux
blocked_by: []
relates: []
refs: [planet/lineages/recent.py, planet/api.py, viewer/navigator.js]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`recent.resolve` takes a finished world's `meta.timezoom` and the peoples job reads that time zoom run, so a world whose
time zoom was deleted (e.g. 119973 and the other L6 worlds in the store) cannot get peoples; the viewer's Peoples panel
now says so and the API answers 400 up front. Decide: keep time zooms of worlds you want peoples on, or let a world carry
the few time-zoom frames the recent pass needs (a small copy in the world file).

## Updates
- 2026-10-23: Status needs-decision -> todo. Coordinator: keep the time zoom with every kept world (cleanup_outputs should treat a world's time zoom as needed, like its parents); the nine reference worlds lost theirs in the 2026-10-24 cleanup, so peoples can't run on them until re-made.
- 2026-10-23: Created from inbox draft draft-viewer-peoples-needs-timezoom-copy.md (found by viewerux).
