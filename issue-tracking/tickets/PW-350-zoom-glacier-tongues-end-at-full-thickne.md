---
id: PW-350
title: Zoom glacier tongues end at full thickness (a 360 m ice cliff at the snout)
type: task
status: in-progress
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoom-batch3
blocked_by: []
relates: [PW-127, PW-159, PW-298]
refs: [planet/zoom.py, planet/zoom_kernels.py, tests/test_zoom_ice.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`zoom.glaciers` gives a tongue's thickness from its flux alone (GL_H0 x (flux / GL_F0)^GL_H_EXP, at least
20 m), so where the tongue's drawing stops (flux used up, width under GL_DRAW px, or GL_MAX_KM) its last
pixel can still be hundreds of metres thick. Seen on the synthetic massif of `tests/test_zoom_ice.py`
(`_zoom(1800.0)`, 900 km at 3 km) after PW-298 put the massif at its cells' mean heights (the old slope
fit left it 1450 m low): a 3 km^3/yr tongue runs down a deep valley to 873 m, where the bare ground's
summer is 16 C, and its last pixels are 364-549 m thick (ice on ground with summers above 12 C: 103 px,
0.3% of the ice; the test now allows 0.5%). A real snout thins to nothing over the last km or so, and a
tongue reaching 16 C summers would be melting ~10 m w.e. a year.

To try: thin the tongue towards its end (thickness from the flux still to come, which falls to 0 at
the snout, rather than the flux at the pixel), and check whether this tongue stops by melting or by
GL_MAX_KM; if by the cap, the melt along it may be too small at low elevations (the bare-ice balance at
the air's summer).
- [ ] tongues thin to < ~50 m at their snout; test_zoom_ice's 12 C check back to (nearly) none

## Updates
- 2026-10-16: Status todo -> in-progress. Zoom batch 4 agent started.
- 2026-10-16: Created from inbox draft draft-zoom-glacier-tongue-snout.md (found by zoom-batch3).
