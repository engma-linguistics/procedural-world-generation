---
id: PW-341
title: A multi-pixel fall's plunge pool sits one pixel below its lip, above most of the drop
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: med
found_by: zoom3d
blocked_by: []
relates: [PW-072, PW-129]
refs: [planet/zoom.py, "zoom e33c3d", "zoom 3ac681", "zoom b16fb7"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`waterfalls()` records `_foot` as `rec[i]`, the pixel right below the lip, and the plunge
pool is dug there (zoom.py, "a plunge pool at the foot"). For a fall that drops over one
pixel that is the foot, but a scarp or drop fall spread over several pixels (`length_km`
3-4 km at 1 km/px) keeps nearly all of its drop below the pool, so the pool hangs at the
top of the fall with the water surface ~ at the lip's level.

Seen in the 3D view (PW-072), following each fall's river down from the lip in zoom
e33c3d (500 km at 1 km/px): the pool is always the first pixel; for the 588 m fall only
12 m of the drop is above the pool, for the 469 m fall 1 m, for the 437 m fall 6 m
(the rest of the 634 / 693 / 751 m of drop over 12 px is below it). Single-pixel lip falls
(b16fb7, 4 km/px: 358 m and 329 m with all of it above the pool) are right. The 3D view
now caps a pool's surface at its lowest dry neighbour so it doesn't float, but the pool
is still in the wrong place.

What I'd try: put the pool at the end of the drop (`best_j`, the pixel the drop is
measured to, which `waterfalls()` already has as `jj`) rather than `rec[i]`, and keep its
surface at the river's level there.
- [ ] the pool of a multi-pixel fall lies below most of its drop (check e33c3d's top falls)
- [ ] goldens regenerated if zoom outputs change

## Updates
- 2026-10-16: Status in-progress -> done. Done: plunge pool at the fall's foot.
- 2026-10-16: Status todo -> in-progress. Zoom batch 4 agent started.
- 2026-10-16: Created from inbox draft draft-zoom-plunge-pool-above-drop.md (found by zoom3d).
