---
id: PW-679
title: Viewer chugs on the peoples workbench and the globe's peoples panel
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-23
updated: 2026-10-23
---

## Description
Owner (2026-10-24): the viewer chugs mightily on the peoples tab (possibly partly the background runs: the machine was at load ~60 on 48 cores from the merge lane's multi-seed checks). Profile the peoples pages' own cost (layer loads, per-frame recolouring, re-renders) on an idle machine and fix what's theirs.

## Updates
- 2026-10-23: Created.
- 2026-10-23: perf679 lane. Measured and fixed in viewer/index.html (timings: docs/review/lineages/perf-679.md, harness tools/viewer_perf.py): hover 36 -> 0.07 ms (the globe pick no longer tests ~1 M triangles), frame step 23-30 -> 16-20 ms (colour parsing and track-point lookups cached), slider bursts coalesced to one repaint per display frame, peoples layers no longer refetched on a layer switch (19 refetches / 45 MB per 12 switches -> 0), overlay-legend crash fixed. The workbench (lineages.html) was already cheap (tabs 2-18 ms). Left as drafts: run layers hold all frames (216 MB resident), the per-vertex paint upload, a self-lerp bug in peoplesColor. Status stays todo until the owner confirms it no longer chugs on an idle machine.
