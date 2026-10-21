---
id: PW-357
title: Zoom glacier tongues fed along their zone's margin run to GL_MAX_KM at the flux cap, discarding the excess
type: task
status: done
parent: null
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: zoom-batch4
blocked_by: []
relates: [PW-350, PW-127, PW-159]
refs: [planet/zoom_kernels.py, planet/zoom.py, tests/test_zoom_ice.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Seen while fixing PW-350 on the synthetic massif of `tests/test_zoom_ice.py` (`_zoom(1800.0)`, 900 km at 3 km).
Its biggest tongues all end by the run cap (GL_MAX_KM = 100 km, `run` 97-99 km), still carrying 1.3-2.8
km^3/yr against a bare-ice balance of -20..-30 m w.e./yr at the snout, on ground with 16 C summers (0.3% of
the ice on > 12 C ground; the test allows 0.5%). Following the biggest one up: for its first ~70 km it runs
along the accumulation zone's margin, which drains into it pixel after pixel (1-4 zone donors per pixel),
and `glacier_flow` clips the sum back to GL_F_MAX at every pixel: ~4 km^3/yr of inflow is discarded along
this one tongue, and its flux stays at ~2.8 km^3/yr whatever it melts. Its `run` counts from where its
biggest feeder left the zone, so the margin-hugging stretch uses up the 100 km before it descends the
last ~20 km into the valley.

Questions: should `run` restart (or not count) while a tongue is still fed by zone pixels (it's the zone's
edge, not a tongue below it)? Should the cap apply only where flux leaves the zone (a sheet's margin
losing the rest), not re-clip at every confluence (then merged tongues carry their sum and need to melt
it)? Either changes where big tongues end; check the massif's 12 C share and the 592f2a plateau zoom
(-48.48, 60.12, 2000 km @ 4 km) before/after. Real outlets do end low (Franz Josef ~300 m in rainforest),
so some ice on > 12 C ground is right; the point is that the end is set by melt, not by the cap.
- [ ] the massif's big tongues end by melt (flux to ~0), not at GL_MAX_KM with the cap's flux

## Updates
- 2026-10-16: Done: tongue run counts from the last pixel its accumulation zone drains into; tongues melt out (longest 82 km). Warm-summer ice share 0.28 -> 0.47% (test limit 0.5%, unchanged).
- 2026-10-16: Status in-progress -> done. Done: tongue run counts from the last pixel its accumulation zone drains into; tongues melt out (longest 82 km). Warm-summer ice share 0.28 -> 0.47% (test limit 0.5%, unchanged).
- 2026-10-16: Status todo -> in-progress. Zoom batch 5 agent started.
- 2026-10-16: Created from inbox draft draft-zoom-tongue-run-along-margin.md (found by zoom-batch4).
