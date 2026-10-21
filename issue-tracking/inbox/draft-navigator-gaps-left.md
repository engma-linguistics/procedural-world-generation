---
title: Navigator: what is still missing after zoom, fine zoom and top-N highlight zooms
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: viewer-batch
blocked_by: []
relates: [PW-482, PW-473]
refs: [viewer/navigator.js, viewer/index.html]
---

## Description
PW-482 added "Zoom a region" (typed or picked lat/lon, size), "Fine zoom" on every zoom node and "Zoom the top N highlights" to the family tree, plus a 100/300/1000 kyr choice and Cancel. Left over from the ticket:
- Run nodes other than the one on screen still offer nothing (they need a moment): a "Time zoom at a typical moment" action could use `highlights.representative_time`, like `planet make`.
- Fine zoom outlines are not drawn on the globe (only first-level zooms are); they are tiles in zoom.html.
- The navigator over zoom.html's tab covers the top of its own header on a narrow screen.
- The time slider's ticks (drawMarks) and the navigator list what was made from a run separately; they could share one source.
- "Zoom a region" on a world that is not on screen reads the lat/lon only from the typed fields (no picker); a small "pick on a map" for it would be the 2D map mode's click.
- The fine zoom form's size field is free text; the server's check (`zoom_fine.check`) only answers after the POST. The allowed range could come from `GET /api/...` or be computed in JS.
