---
title: Shield domes are ringed by streams in the viewer's relief (a moat look)
type: task
status: todo
parent: PW-005
subsystem: zoom
effort: s
impact: low
found_by: zoomland2
blocked_by: []
relates: [PW-011]
refs: [planet/zoom_landforms.py, "zoom 23fe61", docs/review/landforms/zoom_shield_23fe61.png]
---

## Description
zoom_landforms.Shield adds the domes to the target (so the drainage goes
round them) and again after the landscape pass. The landscape pass rings
each dome with small streams, so in the viewer's relief shading each
inselberg shows a dark outline like a moat or a crater rim (zoom 23fe61).
Without the target the streams cross the domes instead (worse: domes cut
into pieces, tried). Domes are also small next to the 0.5-1 km pixels
(R 0.8-4.5 km).
Try: a pediment apron (a gentle concave skirt, 1-2 R) around each dome in
the target only, so the foot streams sit farther out and the dome rises
from a smooth pediment; or exclude dome footprints from the channel mask
used in the landscape pass.
