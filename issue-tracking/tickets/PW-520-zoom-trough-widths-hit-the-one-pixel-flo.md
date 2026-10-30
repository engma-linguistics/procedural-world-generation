---
id: PW-520
title: Zoom trough widths hit the one-pixel floor at 2 km/px, so width/depth can't follow the depth
type: task
status: todo
parent: PW-649
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: pw512
blocked_by: []
relates: [PW-510, PW-092]
refs: [planet/zoom/glacial.py, "zoom b6d6d7", "zoom aa113a"]
created: 2026-10-21
updated: 2026-10-23
---

## Description
PW-510 made a glacial trough open until its rim-to-rim width is 3-5 x its depth (zoom_glacial `_open_width`), at least one pixel across. At 2 km/px (Norway b6d6d7) 73% of the troughs sit on that floor (a 400 m trough would want 1.6 km), so only 57% land in the literature ranges (depth 200-1500 m, W/D 2.5-6); at 1 km/px (aa113a) 19% are on the floor and 82% are in range. Fine zooms (zoom_fine, PW-129) should draw the real widths; check the trough stats `tr_*` on a fine zoom of Norway at 0.25-0.5 km/px and whether the cell-mean redistribution stays neutral with the narrower troughs.
- [ ] fine zoom of Norway: >= 70% of troughs in range, tr_at_pixel_floor_pct < 30

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-21: Created from inbox draft draft-glacial-trough-pixel-floor.md (found by pw512).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
