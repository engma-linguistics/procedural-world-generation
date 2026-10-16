---
id: PW-321
title: "Zoom edge band: relief doubles within 8 px of the region's edge"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: pw125
blocked_by: []
relates: [PW-125, PW-129]
refs: [planet/zoom.py, docs/review/zoom-polish/pw125.md, docs/review/zoom-polish/pw125_seam_interior.png]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Each zoom holds its edge pixels at the coarse target surface (outlets, `WF_EDGE_PX` = 8 keeps falls off
them), and the landscape inside steps into them. Measured on 3x3 tiles of 1 km zooms of world 592f2a
(docs/review/zoom-polish/pw125.md): the mean 3x3 relief within 8 px of a zoom's edge is about twice the
inside (405 vs 207 m on a mountain range at 49.32,37.38; 505 vs 293 on an arc; 89 vs 47 m on a plain at
26.74,-49.92). Every zoom has a rough rim, and tiles side by side show it as a seam (adjacent tiles also
differ by a median 53-212 m where they overlap, because the drainage is solved per zoom). PW-125's
description already noted steps into the edge (afdaf5 cols 4-10, 270-320 m); they're unlisted, not gone.
To try: let the outermost pixels drain out at the landscape's own grade (an outlet level from the
neighbouring inside pixels rather than the target), or taper the landscape toward the target across a band
a few pixels wide.
- [ ] edge-band 3x3 relief within ~20% of the inside on the three test sites

## Updates
- 2026-10-15: Created from inbox draft draft-zoom-edge-band-relief.md (found by pw125).
