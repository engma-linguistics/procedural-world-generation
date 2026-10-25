---
id: PW-884
title: A zoom's stored loess layer is the soils' interpolated world loess, not the glacial loess the zoom drew
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: xs
impact: low
found_by: coupling-audit
blocked_by: []
relates: []
refs: [planet/zoom.py, planet/zoom_vegetation.py, docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Coupling audit finding C12 (severity low for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/zoom.py:3320: layers {"glacial_form", "loess": glac_loess} (zoom_glacial's own, which softens and classes the terrain).

**Other side:** planet/zoom.py:3325 **veg_l afterwards, whose soils part carries "loess" (zoom_vegetation.py:265, from the world's soils), and wins the key.

**Why they disagree:** Two producers write one key; the later one silently replaces what the terrain was built with, and the soils never see the zoom's loess.

**Measured:** Code read: both keys confirmed. Not measured.

**What to try:** Name the glacial one glacial_loess (or feed it to the soils as their loess).

## Updates
- 2026-10-25: Created from inbox draft draft-zoom-loess-layer-overwritten-by-soils.md (found by coupling-audit).
