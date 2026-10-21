---
id: PW-390
title: Fine zoom gorges are D8 staircases with banded walls
type: task
status: done
parent: null
milestone: null
subsystem: zoom
effort: m
impact: med
found_by: pw129-fine-zoom
blocked_by: []
relates: [PW-129]
refs: [planet/zoom_fine.py, "zoom 3e74b0", "zoom b3c260", "zoom 97b3e7"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
In nested fine zooms (planet/zoom_fine.py) the gorge below a fall follows the
parent's fall chain (lip -> foot by the parent's D8 receivers). Its floor is
the chain's pixels and its walls are a 1-2 px band held near the lip's level,
so at 50 m and 25 m it renders as a stair-stepped canyon with parallel bands
on its walls (zoom 3e74b0 at 50 m and b3c260 at 25 m, round the 822 m fall at
16.385, 155.723; the parent 97b3e7 at 100 m shows it more mildly). Each level
inherits the parent's staircase, because the parent's own gorge (walls at lip
height along a D8 path) is in the 3x3-block means the child keeps.

What I'd try:
- lay the gorge along a smoothed polyline of the chain (Catmull-Rom like the
  other courses) with a distance-based cross-section (floor width, walls
  sloping to the plateau over a few px) instead of a fixed wall band;
- in a fine parent, mark gorge and wall pixels (or store the gorge polyline in
  stats.falls) so the child rebuilds the gorge rather than keeping it through the
  block means.
- [ ] at 50 m and 25 m the gorge below the 170672 fall reads as one winding
      canyon in the satellite preview, with no banding along its walls

## Updates
- 2026-10-16: Status todo -> done. Merged: smooth gorge path, distance cross-section, gorges out of the block means, needle cut; needles 98 -> 1 at 25 m.
- 2026-10-16: Created from inbox draft draft-fine-zoom-gorge-d8-banding.md (found by pw129-fine-zoom).
