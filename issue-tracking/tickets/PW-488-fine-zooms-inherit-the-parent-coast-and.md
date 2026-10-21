---
id: PW-488
title: Fine zooms inherit the parent coast and islands as 1 km pixel staircases
type: task
status: done
parent: null
milestone: v1
subsystem: zoom
effort: m
impact: med
found_by: pw392-fine-forms
blocked_by: []
relates: [PW-392, PW-129]
refs: [planet/zoom_fine.py, "zoom a0097b in 3ac681"]
created: 2026-10-20
updated: 2026-10-21
---

## Description
Seen on a0097b (100 m in 3ac681, 1 km): the large ring of islands round the lagoon (land 143-265 m, ~2 km wide) has its outer edge as steps of parent pixels, 10 fine pixels a tread, because the coast comes from the parent's land/sea (bicubic height, categorical water nearest after a warp) and the parent's ring is itself the world's coarse coast at 1 km. The reefs and the atoll rim are now drawn at the fine scale (PW-392) but not this coast. Idea: a shoreline pass at the fine scale (the regional zoom's coast noise: zoom.build's land/sea indicator and detail at the fine pixel) held to the parent's land fraction per parent pixel, then the shoreface (zoom_coastal.shoreface) at the fine scale, as the parent has it.
- [ ] a fine zoom's coast without the parent's pixel staircase; each parent pixel's land share kept

## Updates
- 2026-10-20: Created from inbox draft draft-fine-zoom-parent-coast-steps.md (found by pw392-fine-forms).
- 2026-10-21: Done. Fine zoom shore = parent ground sampled through a fractal displacement near the coast (zoom_fine.COAST_PX 0.38 parent px). Straight-run share of coast 0.13 to 0.02 (Norway, 100 m), 0.21 to 0.015 (tropical, 50 m); land area within 0.5 percent. Zooms 24584e, 1b331e. tools/coast_steps.py measures it.
