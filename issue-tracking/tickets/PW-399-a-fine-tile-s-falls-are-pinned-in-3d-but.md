---
id: PW-399
title: A fine tile's falls are pinned in 3D but not in the panel's waterfall list
type: task
status: todo
parent: PW-649
milestone: later
subsystem: viewer
effort: s
impact: low
found_by: fine-zoom-3d
blocked_by: []
relates: [PW-129, PW-072]
refs: [viewer/zoom.html, viewer/zoom3d.js]
created: 2026-10-16
updated: 2026-10-23
---

## Description
In the zoom 3D view, a fine tile's falls and volcanoes get pins and labels
(ids "<zoom>:<index>"; click flies there, hover shows the card), and the
parent's falls under the tile give way to them. The 3D panel's "Waterfalls"
list and `&fall=N` still list only the opened zoom's falls (clicking one under
a fine tile flies to the right place, but with the parent's coarse fall data in
the card). List the fine tiles' falls too (grouped under their zoom), and let
`&fall=` take "<zoom>:<index>".

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-16: Created from inbox draft draft-fine-tile-falls-list.md (found by fine-zoom-3d).
