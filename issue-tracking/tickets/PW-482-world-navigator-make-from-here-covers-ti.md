---
id: PW-482
title: "World navigator: 'make from here' covers time zoom, finish and highlights only; zoom, fine zoom and highlight zooms still need the old flows"
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: viewer
effort: m
impact: med
found_by: agent-make-ui
blocked_by: []
relates: [PW-473, PW-472]
refs: [viewer/navigator.js, viewer/index.html, viewer/zoom.html]
created: 2026-10-20
updated: 2026-10-20
---

## Description
What the navigator (PW-473) does today: provenance chain with thumbnails, a Family tree, "Time zoom from here" (fixed 300 kyr), "Finish world here / at its end", "Find highlights" on a world; zoom outlines on the globe with a clickable edge. Gaps:
- "Zoom this region" and "Fine zoom here" are not buttons in the tree: they still need picking a cell on the globe (existing zoom box) or the Fine zoom control in zoom.html. A tree-level "Zoom the top N highlights" (what `planet highlights --zoom N` does, `highlights.pick_zooms`) needs a small server route; nothing makes it from the viewer today.
- The time zoom length is fixed at 300 kyr in the navigator (the run summary's own button has a 100/300/1000 choice).
- Run nodes other than the one on screen offer no actions (they need a moment); a "Time zoom at a typical moment" action could use `highlights.representative_time`, like `planet make`.
- Fine zoom outlines are not drawn on the globe (they are tiles in zoom.html); only first-level zooms are.
- The navigator inside zoom.html's tab is the same bar over the page; on a narrow screen it covers the top of zoom.html's own header.
- The time slider's own ticks (drawMarks) and the navigator both list what was made from a run; they could share one source.
- [ ] tree actions: zoom region (needs a picker), top N highlight zooms, kyr choice

## Updates
- 2026-10-20: Created from inbox draft draft-navigator-from-here-gaps.md (found by agent-make-ui).
