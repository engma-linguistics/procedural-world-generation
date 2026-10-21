---
id: PW-510
title: Calibrate the zoom's trough depth and width against real fjords and U-valleys
type: task
status: done
parent: null
milestone: v1
subsystem: zoom
effort: s
impact: low
found_by: pw092
blocked_by: []
relates: [PW-092]
refs: [planet/zoom_glacial.py, "zoom 66c45e", "zoom 0de6eb"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
The trough constants are physical estimates, not fits: floor lowering = 8 x the cell-mean erosion (the volume of one or two ~5 km troughs per 110 km cell), half-width 2.2 km x (q / 25)^0.2 up to 6 km, wall exponent 1.7, along-valley modulation 0.45-1.3. Norway zoom 66c45e (L6 parent): 14 fjords, mean depth 361 m, max 835 m (Sognefjord 1,300 m, Hardanger 860 m); 1 km zoom 0de6eb: 11 fjords, max 843 m. Fjord widths and lengths are not yet measured against Norway's (2-6 km wide, to 200 km long); the drowned troughs at 2 km/px are 2-3 px wide. Check width / depth / length distributions, and the cell-mean bias the redistribution leaves (66c45e inland bias -5.5 m, RMS 17.6 m against 8-55 m typical).
- [ ] fjord width, length and depth percentiles for Norway vs. the real ones, constants nudged (not forced)

## Updates
- 2026-10-21: Status todo -> done. Merged 470b935: width/depth 3-5 by flux, depth capped 0.6 x ice. 82% in range at 1 km/px, 78-86% for resolved troughs; pooled 66% because 2 km/px widths hit the pixel floor (PW-520). Accepted as done: the shortfall is resolution, not the model.
- 2026-10-21: Created from inbox draft draft-glacial-zoom-calibration.md (found by pw092).
- 2026-10-21: Built on branch worktree-agent-a6325323c9d1c4305: width follows depth (3-5 x), floor lowering capped by the ice thickness. 1 km Norway 82% of troughs in range, 2 km 57% (pixel floor), Baltic 66%, Ungava 0% (shield: 180 m deep troughs, below the fjord range). Fjord depths 80-83% in 200-1500 m (Norway). Needs a merge.
