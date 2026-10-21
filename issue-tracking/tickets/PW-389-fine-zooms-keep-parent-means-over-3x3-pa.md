---
id: PW-389
title: Fine zooms keep parent means over 3x3 parent pixels, not per pixel
type: task
status: done
parent: null
milestone: null
subsystem: zoom
effort: xs
impact: med
found_by: pw129-fine-zoom
blocked_by: []
relates: [PW-129]
refs: [planet/zoom_fine.py, "zoom 97b3e7", "zoom 170672"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
The proposal (docs/proposals/nested_fine_zoom.md, step 2) says each parent
pixel's mean is pulled back to the parent's height. Built that way, a
parent's 1-px features came back as blocks. Zoom 170672 at 1 km has its
canyon as a diagonal staircase of single pixels, 1300 m deep. Kept pixel by
pixel, the 100 m child redrew it as a staircase of 1 km boxes (rms error
15 m).

planet/zoom_fine.py now keeps the mean of every 3x3 block of parent pixels,
with bicubic corrections. The canyon follows its smooth river course. The
block means are kept to 7-20 m rms (97b3e7: 17 m; 3e74b0: 7 m), but single
parent pixels can be off by 30-120 m rms (97b3e7: 119 m, in a canyon
1300 m deep; the volcano zoom 6ea4c1: 36 m).

Options:
- A. Keep 3x3 blocks (now): no blocks, smooth forms; a single pixel's mean is
  not exact.
- B. Per pixel, exact: faithful, but every parent's pixel-scale feature comes
  back as a block.
- C. 3x3 blocks first, then a weak per-pixel pass limited to slopes below
  ~20 degrees: closer means on gentle ground, no blocks in canyons.

Lean: A. The parent's pixels are its rendering of the place, not ground truth
at 1 km.

## Updates
- 2026-10-16: Status needs-decision -> done. Coordinator decision: accept 3x3-block means. The parent's single pixel is itself an interpolated 1 km estimate; per-pixel means rebuilt the parent's pixel staircase. The features the owner asked to keep exact (fall drops, volcano summits) are held exactly regardless.
- 2026-10-16: Created from inbox draft draft-fine-zoom-block-means.md (found by pw129-fine-zoom).
