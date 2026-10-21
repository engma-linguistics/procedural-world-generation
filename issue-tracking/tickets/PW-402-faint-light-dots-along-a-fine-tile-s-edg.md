---
id: PW-402
title: Faint light dots along a fine tile's edge in the zoom 3D view
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: fine-zoom-3d
blocked_by: []
relates: [PW-129]
refs: [viewer/zoom3d.js, viewer/zoom3d_look.js, "zoom 170672", docs/review/fine-zoom-3d/waterfall_chain_50m_1x.png]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Where a fine tile meets its parent (e.g. 97b3e7 in 170672, seen from ~50 km
away), a faint dotted light line can show along the seam. The heights match
(the fine tile's outer 8 px blend into the parent: 0.4 m mean, 6 m max), and the
parent's hole is shrunk by 0.1 fine px; what's left is likely the shader
discard being per fragment while the edge is antialiased per sample (MSAA), so
some edge samples get neither surface and show the sky or haze. Try: shrink the
hole by ~0.5 fine px (the parent then overlaps the blended rim, where both are
at the same height), or draw the fine tiles first with the parent depth-tested
behind them. Check from far and close with the Height layer (each tile
coloured by its own range, so the seam is easy to find).

## Updates
- 2026-10-16: Created from inbox draft draft-fine-tile-seam-dots.md (found by fine-zoom-3d).
