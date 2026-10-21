---
title: Calibrate the zoom's trough depth and width against real fjords and U-valleys
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: pw092
blocked_by: []
relates: [PW-092]
refs: [planet/zoom_glacial.py, "zoom 66c45e", "zoom 0de6eb"]
---

## Description
The trough constants are physical estimates, not fits: floor lowering = 8 x the cell-mean erosion (the volume of one or two ~5 km troughs per 110 km cell), half-width 2.2 km x (q / 25)^0.2 up to 6 km, wall exponent 1.7, along-valley modulation 0.45-1.3. Norway zoom 66c45e (L6 parent): 14 fjords, mean depth 361 m, max 835 m (Sognefjord 1,300 m, Hardanger 860 m); 1 km zoom 0de6eb: 11 fjords, max 843 m. Fjord widths and lengths are not yet measured against Norway's (2-6 km wide, to 200 km long); the drowned troughs at 2 km/px are 2-3 px wide. Check width / depth / length distributions, and the cell-mean bias the redistribution leaves (66c45e inland bias -5.5 m, RMS 17.6 m against 8-55 m typical).
- [ ] fjord width, length and depth percentiles for Norway vs. the real ones, constants nudged (not forced)
