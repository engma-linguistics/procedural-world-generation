---
title: Peoples cannot run on worlds whose time zoom was deleted (most L6 worlds)
type: task
status: needs-decision
parent: null
subsystem: viewer
effort: m
impact: med
found_by: viewerux
blocked_by: []
relates: []
refs: [planet/lineages/recent.py, planet/api.py, viewer/navigator.js]
---

## Description
`recent.resolve` takes a finished world's `meta.timezoom` and the peoples job reads that time zoom run, so a world whose
time zoom was deleted (e.g. 119973 and the other L6 worlds in the store) cannot get peoples; the viewer's Peoples panel
now says so and the API answers 400 up front. Decide: keep time zooms of worlds you want peoples on, or let a world carry
the few time-zoom frames the recent pass needs (a small copy in the world file).
