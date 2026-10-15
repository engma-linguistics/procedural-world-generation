---
id: PW-168
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
refs: [planet/zoom_landforms.py, "zoom 23fe61", docs/review/landforms/zoom_shield_23fe61.png, "world:a08983(-16.75,-28.53)"]
created: 2026-10-14
updated: 2026-10-15
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

## Updates
- 2026-10-15: Merged inbox draft draft-shield-dome-apron-tried.md ("Shield dome moats (PW-168): a pediment apron in the target doesn't help; domes also get striped by gullies", found by smalls2).
  For PW-168 (merge into it). Tried on branch smalls2: `Shield.target` = 0.8 x max(dome, apron), the apron the same dome sites at 2x the radius with a lower, gentle profile (so the foot streams would run round a pediment). Compared hillshade crops of a 250 km, 0.5 km/px zoom at -16.75, -28.53 (world a08983) before and after: no visible change to the rings, and more domes came out striped by parallel gullies across their faces (the landscape pass incising the target's dome). Not taken. The stripes are a second artefact worth fixing with the moat: both suggest the landscape pass should not see the domes at all (mask the dome footprints out of the channel network and add the domes only in `shape`), and the drainage be deflected by a separate rule (route the streams round the footprints) instead of by the target.
- 2026-10-14: Created from inbox draft draft-shield-dome-moats.md (found by zoomland2).
