---
title: Fine zoom braided reaches are drawn as one smoothed thread
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: low
found_by: pw405
blocked_by: []
relates: [PW-405]
refs: [planet/zoom_fine.py, "_courses", "zoom 2b1dab (3ac681 -> 50 km @ 100 m at 1.99, -69.30, scratch)"]
---

## Description
PW-405 classifies each fine-zoom river reach. A reach is braided when it is alluvial and its slope is above ~1.5-3x the Leopold-Wolman threshold 0.013 Q^-0.44. A braided reach gets no meanders, but it is still drawn as one smoothed channel of hydraulic-geometry width.

Example: the 8,000 m^3/s river of 3ac681 at 0.09% runs as a single straight band in fine zoom 2b1dab. Its zoom.json `river_planform.classes_km` has 75 km of braided reach.

Approach: in braided reaches, widen the active belt to ~3-5 w and draw 2-4 threads. Each thread is a low-amplitude, short-wavelength wander inside the belt (planet-fixed phase like the meanders), with gravel bars between them. The threads have to merge back at the reach's ends. The drainage stays on the main thread so the receiver network stays a tree.
- [ ] Braided reaches show several threads and bars in plan view and in 3D.
- [ ] zoom_fine.planform stays switchback-free on the main thread.
