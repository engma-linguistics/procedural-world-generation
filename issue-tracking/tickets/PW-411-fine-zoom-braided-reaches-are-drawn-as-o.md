---
id: PW-411
title: Fine zoom braided reaches are drawn as one smoothed thread
type: task
status: todo
parent: PW-649
milestone: later
subsystem: zoom
effort: m
impact: low
found_by: pw405
blocked_by: []
relates: [PW-405]
refs: [planet/zoom/fine.py, _courses]
created: 2026-10-16
updated: 2026-10-23
---

## Description
PW-405 classifies each fine-zoom river reach. A reach is braided when it is alluvial and its slope is above ~1.5-3x the Leopold-Wolman threshold 0.013 Q^-0.44. A braided reach gets no meanders, but it is still drawn as one smoothed channel of hydraulic-geometry width.

Example: the 8,000 m^3/s river of 3ac681 at 0.09% runs as a single straight band in fine zoom 2b1dab (deleted). Its zoom.json `river_planform.classes_km` has 75 km of braided reach.

Approach: in braided reaches, widen the active belt to ~3-5 w and draw 2-4 threads. Each thread is a low-amplitude, short-wavelength wander inside the belt (planet-fixed phase like the meanders), with gravel bars between them. The threads have to merge back at the reach's ends. The drainage stays on the main thread so the receiver network stays a tree.
- [ ] Braided reaches show several threads and bars in plan view and in 3D.
- [ ] zoom_fine.planform stays switchback-free on the main thread.

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-16: Created from inbox draft draft-fine-zoom-braided-rivers.md (found by pw405).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
