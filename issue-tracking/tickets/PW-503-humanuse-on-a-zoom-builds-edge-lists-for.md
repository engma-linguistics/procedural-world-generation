---
id: PW-503
title: "humanuse on a zoom builds edge lists for every pixel: memory and time at 4096 x 4096"
type: task
status: todo
parent: PW-099
milestone: v1
subsystem: zoom
effort: s
impact: low
found_by: humanuse
blocked_by: []
relates: [PW-099, PW-649]
refs: [planet/humanuse.py, planet/zoom.py]
created: 2026-10-21
updated: 2026-10-23
---

## Description
`humanuse.analyse_zoom` runs on a graph of 4 edges per pixel (int32 indices, float32 lengths) and relaxes it with `np.minimum.at` (distance transforms, valley-floor minima, spring windows). A 500 x 500 zoom takes about 1.3 s; the cost grows with the pixel count, so the allowed maximum (4096 x 4096, 16.7 M pixels, 67 M edges) will be tens of seconds and a few GB at the end of every `zoom.build`. Not measured at that size. Options: tile the relaxation, use a numba distance transform for the raster case, or skip the layers above some pixel count (and say so in `zoom.json`).
- [ ] time a 2000 x 2000 and a 4096 x 4096 zoom build with and without the layers

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: Milestone null -> v1 (PW-597 triage, coordinator, 2026-10-23): a real bug in a v1 feature (humanuse on a zoom builds edge lists for every pixel).
- 2026-10-21: Created from inbox draft draft-humanuse-large-zoom-cost.md (found by humanuse).
