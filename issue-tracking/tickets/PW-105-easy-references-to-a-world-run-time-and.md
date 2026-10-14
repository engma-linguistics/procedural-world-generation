---
id: PW-105
title: Easy references to a world/run, time and place (viewer copy text, deep links, ref convention)
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner wants specific worlds, times and locations to be referenceable in tickets. Today the viewer's click-to-copy text is like 'Current code L7 Earth-like (seed 21): t = 624 Myr, cell 44522, lat 7.8, lon 156.6, elevation 3743 m, ice ~1000 m thick' - it has no run/world id, and cell ids differ by level.
- Include the id in the copied text (run 428083 / world f724bd) and a deep-link URL that reopens the viewer at that run/world, time and lat/lon (and picked cell).
- Ref convention in issue-tracking/README.md: run:<id>@<t>Myr(lat,lon), world:<id>(lat,lon), zoom:<id>.
- board.py check (or a separate --refs flag) warns when a referenced run/world/zoom id no longer exists, so deletions don't leave dangling refs.

## Updates
- 2026-10-14: Created.
