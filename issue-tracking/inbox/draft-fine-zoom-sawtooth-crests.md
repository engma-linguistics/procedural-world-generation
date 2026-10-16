---
title: Fine zoom crests stay sawtoothed where the means' corrections step a parent pixel apart
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: med
found_by: pw390-fine-zoom-gorge
blocked_by: []
relates: [PW-129, PW-390]
refs: [planet/zoom_fine.py, "zoom 3e74b0", "zoom b3c260", docs/review/fine-zoom-gorge/]
---

## Description
After PW-390 no pixel in the showcase chain stands more than 1.5x a 35 degree slope above all
its neighbours (but one at 25 m, 1.2x), yet some crests away from the gorge still read as jagged
teeth in 3D at 1x (3e74b0 at 50 m, b3c260 at 25 m: `after_*_gorge.png`, two horns left of the
headwall in `after_b3c260_face.png`). Steepest drop to a neighbour > 1.5 x tan 35: 3.8% of px at
50 and 25 m (1.4% at 100 m); ~1000 / ~3000 such px are away from the gorge, streams and the edge,
with drops of 100-370 m per pixel.

What I found: the stream-power pass caps slopes only along the flow; zoom_fine now cuts active
pixels to 1.25x their threshold slope (min-plus, `_relax`) before the 3x3-block mean passes, but
the corrections afterwards (bicubic of per-parent-pixel gaps, 2-4 fine px apart) re-steepen. A
second min-plus cut after them at 2x the threshold took block-mean rms from 12/17 m to 27/42 m
(50/25 m) for only ~30% fewer steep px, so it isn't in. Suspects: the `max(hw + corr, lb + 0.1 *
(hw - lb))` clamp, whose local base jumps across divides (steps along crests), and gaps of
neighbouring parent pixels that differ by 100+ m.

What I'd try: smooth the correction field at the block scale (per_block then a second box) or
apply it in proportion to each pixel's height above its local base; measure steep px and block
rms on the chain 97b3e7 -> 3e74b0 / b3c260.
- [ ] steepest drop > 1.5 x tan 35 on < 1% of px at 50 and 25 m, away from held features
- [ ] block means kept to <= 20 m rms
