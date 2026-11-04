---
id: PW-685
title: Viewer repaint writes 1.15 M vertices of position and colour per frame; a per-cell colour texture would cut the upload
type: task
status: todo
parent: PW-103
milestone: later
subsystem: viewer
effort: m
impact: med
found_by: perf679
blocked_by: []
relates: [PW-679]
refs: [viewer/index.html, paint(), docs/review/lineages/perf-679.md]
created: 2026-10-23
updated: 2026-11-03
---

## Description
After PW-679 a frame step costs ~16-20 ms of JS at L7 on the peoples views, mostly `paint()`: it builds per-cell and
per-corner colours, converts them to 16-bit, then copies them to each of ~1.15 M vertices (7 per cell), and rewrites
all vertex positions (the land radius changes between frames: 190 k of 491 k radii differ from frame 1 to 2), then
uploads about 21 MB (positions 13.8 MB + colours 6.9 MB). The corner-averaged "smooth" colours are the main reason for
the per-vertex copy.
Options: (A) a per-cell colour in a float texture sampled in the vertex shader by an index attribute written once
(upload 164 k x 3 floats = 2 MB a frame, no per-vertex copy); the corner averaging moves to the shader or a second small
texture; (B) the same for the radius, so positions need no rewrite either; (C) leave it, since 16-20 ms is a replay of
~50 fps before drawing. Do (A)+(B) only if the owner still feels the replay is heavy after PW-679; it touches paint, the
overlays that sit on `V.R`, and picking (`topo.triStart`, `pickGlobeCell` read the position array).

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: viewer nicety, not needed for the culinary goal
- 2026-10-23: Created from inbox draft draft-viewer-paint-cell-colour-texture.md (found by perf679).
