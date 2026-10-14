---
id: PW-105
title: Easy references to a world/run, time and place (viewer copy text, deep links, ref convention)
type: task
status: done
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
- 2026-10-14: Status in-progress -> done. Viewer: clicking a cell now copies 'run:<id>@<t>Myr(lat,lon) <name>: <description> <deep link>' (world:<id>(lat,lon) for worlds); the link is the viewer URL with run+t or world, lat, lon (keeping mode/layer), and ?lat=&lon= on load turns to the place and picks the nearest cell (checked with headless-Chrome screenshots for run 01b0f7@384 and world 63f57e). issue-tracking/README.md documents the forms (run:/world:/zoom:, lat/lon not cell ids). board.py check prints a one-line warning (exit 0) when open tickets' refs name run/world/zoom ids missing from runs/, worlds/, zooms/; check --refs lists them for all tickets, refs and Descriptions (none dangling right now). Test in test_board. Also fixed the PW-044 wind-season select overflowing the panel.
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Created.
