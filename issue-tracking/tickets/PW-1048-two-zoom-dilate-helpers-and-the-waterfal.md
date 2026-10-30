---
id: PW-1048
title: Two zoom dilate helpers (and the waterfall wall roughness) use np.roll, so masks at one edge of a zoom leak onto the opposite edge
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: xs
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: []
refs: [planet/zoom/regional.py, planet/zoom/landforms.py, planet/zoom/falls.py, planet/zoom/coast.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. When the zoom "grows" a shape outward by a few pixels (ice, rivers on the preview, protected areas), two of its helpers wrap around the map: something touching the left edge also grows on the right edge, top onto bottom. Mostly this lands in the margin that gets cropped off, but the preview image is drawn after cropping, so its river edges can wrap visibly.

Verified on main b36c9581: `zoom.py:3447 _dilate` and `zoom_landforms.py:1415 _dilate` both use `np.roll(np.roll(m, dy, 0), dx, 1)`. `zoom_coast.py:89` has a non-wrapping version. `zoom_falls.py:183-190` smooths gorge-wall noise with `np.roll` too. Also `zoom.py:710 _shift` and `zoom_coast.py:81 _shift` use opposite sign conventions (harmless only while every caller is symmetric).

Fix: one non-wrapping `dilate(m, r, disk=True|False)` and one `shift` (pad, then slice) used everywhere; add a test that a mask on the west edge leaves the east edge untouched. (Merging the other raster copies into one module is a separate refactor awaiting the owner's yes.)

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-zoom-dilate-wraps-at-edges.md (found by code-audit-2026-10).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
