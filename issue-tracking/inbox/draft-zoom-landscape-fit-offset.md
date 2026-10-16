---
title: "Zoom landscape pass settles 100-200 m off the coarse cell means (C fit to box means)"
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: med
found_by: fix-coast-zoom
blocked_by: []
relates: [PW-268]
refs: [planet/zoom.py, docs/review/audit/fixes-coast-zoom.md, "world 592f2a", "world 9970c1 (fix branch, deleted)"]
---

## Description
After PW-268 the target surface keeps each coarse cell's mean (land interior -0/26 m bias/RMS on 592f2a)
and the valleys are cut mass-neutrally, but the stream-power pass itself settles off it: land cells away
from the coast after the pass are -14/159 m on 592f2a (-9.35/-161.39, 2000 km at 4 km), +8/206 on a
tropical mountain zoom and +129/228 on a glaciated high plateau (seed 3199 L7, -48.48/60.12), even with
30 iterations instead of 15 (so it is a fixed point, not slow convergence). C is updated per pixel by
(tmean / hmean)^0.8, but a pixel's height depends on the slopes all along its way to the outlet, and the
soft cap / cap (tmean + 0.7 / 1.8 amp), MAX_SLOPE and the floors bind in places.

Tried on the fix branch and dropped: scaling the relief above the drainage (each pixel's height above
the channel, lake or outlet its water reaches) per cell to hit the mean. It keeps the drainage intact and
brought the RMS to 37-115 m, but it fought the landform classes' styles (karst towers, escarpment cliffs,
coastal plain slopes in test_zoom_landforms changed character) and is a forced fix.

To try: find which constraint binds where the error is (caps on plateaus? floors?), or fit C against
cell means of the relief above the outlet rather than box means of absolute height.
Also: some trench cells next to arcs/coasts still come out up to ~2 km shallow on 592f2a (p95 +2100 m;
bias +309, was +4323), where the coast taper damps the mean correction.
- [ ] land-interior cell-mean RMS < ~120 m on 592f2a-type zooms, bias within +-20 m on a glaciated plateau
