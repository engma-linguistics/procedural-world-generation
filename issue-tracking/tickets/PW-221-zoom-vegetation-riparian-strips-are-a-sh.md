---
id: PW-221
title: "Zoom vegetation: riparian strips are a share of the pixel's water, not a sub-pixel habitat; gallery forest fades at 2-4 km/px"
type: task
status: todo
parent: PW-184
subsystem: zoom
effort: m
impact: low
found_by: vegzoom
blocked_by: []
relates: [PW-214]
refs: [planet/zoom_vegetation.py, "zoom:64f0b6", "zoom:58c0ac"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
zoom_vegetation gives a river's water to a strip RIP_W0 + RIP_W1 x log10(Q) km wide (0.15 km at 1 m3/s, 1.35 km at 1000 m3/s) as that share of the pixel's water supply (extra_pet = 0.9 x share x PET). At 0.5-1 km/px gallery forest and oasis woodland show clearly (zoom 58c0ac, 64f0b6 tree cover); at 2-4 km/px the strip is a small share of the pixel, so the whole pixel gets a little more water and only big rivers show a woody line. A real 2 km pixel along a desert river is ~10% riparian woodland and ~90% desert: the bucket mixes the two into one mediocre plant cover. The fix would treat the strip as a habitat of its own inside the pixel (like the flooded share: K split between a riparian and a dryland part, each with its own water), and name the pixel by the strip where it is a big enough share or where it is the only woody vegetation for kilometres (an oasis matters to a traveller at any scale).
- [ ] a riparian habitat share per pixel with its own water supply in the competition
- [ ] oasis / gallery forest named where the strip holds most of the pixel's trees

## Updates
- 2026-10-15: Created from inbox draft draft-zoom-veg-subpixel-riparian.md (found by vegzoom).
