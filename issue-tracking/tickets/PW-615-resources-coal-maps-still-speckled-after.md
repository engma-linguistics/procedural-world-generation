---
id: PW-615
title: "Resources: coal maps still speckled after smoothing the traced cover (cell-to-cell trace noise)"
type: task
status: todo
parent: PW-155
milestone: v2
subsystem: surface
effort: m
impact: low
found_by: resources2
blocked_by: []
relates: [PW-134, PW-155]
refs: [planet/resources.py, docs/review/resources/stage2.md, docs/review/resources/stage2/coal_1144ce_before_after.jpg]
created: 2026-10-23
updated: 2026-10-23
---

## Description
resources.history() now smooths each traced cell's cover (a 5-keyframe running mean) and its peat-swamp flag
(the majority over the same window) before it rebuilds the column (PW-610 lane). On four worlds this cuts the
isolated coal cells (>= 0.5 with no neighbour >= 0.5) from 24-36% to 16-23% of the coal cells, and patches
merge. The map is still speckled, though. Neighbouring cells trace back to different keyframe cells: their
paths split at plate boundaries and in the nearest-cell lookup, so their columns differ frame by frame.
Options:
- Smooth the column summaries over neighbours that stayed on the same plate (cheap, a post-pass).
- Trace a small stencil per cell and average it.
The keyframe flicker itself is PW-134.
- [ ] isolated coal cells are under 10% of the coal cells on 1144ce and 119973, and coal's share of land does
      not grow

## Updates
- 2026-10-23: Created from inbox draft draft-resources-coal-speckle-residual.md (found by resources2).
