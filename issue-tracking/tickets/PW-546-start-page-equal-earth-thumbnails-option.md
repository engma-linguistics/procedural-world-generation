---
id: PW-546
title: "Start page: Equal Earth thumbnails, optional list, rotating-globe picker"
type: story
status: done
parent: null
milestone: v1
subsystem: viewer
effort: m
impact: med
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-21
updated: 2026-10-21
---

## Description
Owner (2026-10-21): the main page shows a flat list of 2D maps. 1) Use Equal Earth for those maps. 2) Make showing the planets that way optional. 3) If not costly, add a picker with left/right buttons or arrow keys to step to the next or previous planet, showing it as a rotating 3D globe.

## Updates
- 2026-10-21: Created.
- 2026-10-21: Done on branch worktree-agent-a82ae15568e35f0cb. Thumbnails are now drawn server-side in Equal Earth (planet/thumbs.py via planet/projection.py `pixel_grid`/`unproject`, transparent outside the outline) with a new cache name (`<kind>-<id>-ee192-<mtime>.png`) so old equirect thumbnails are never served. `/api/thumb` takes `proj=equal-earth|equirect` and `w=192|512|1024`. Start page (viewer/start.js, new viewer/globepick.js): "Globe" and "Map list" toggles (remembered in localStorage `planet.startViews`), a globe picker with prev/next buttons and left/right arrow keys, name, Open button; three.js and one texture loaded lazily, texture disposed on each step, whole WebGL context disposed when hidden. Works at 390 px. Screens docs/review/screens/pw546-*.png. Needs a server restart (thumbs.py/server.py changed). Follow-up draft: start-globe-polish.
