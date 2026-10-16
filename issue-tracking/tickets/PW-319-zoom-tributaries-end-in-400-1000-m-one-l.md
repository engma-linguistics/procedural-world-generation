---
id: PW-319
title: "Zoom: tributaries end in 400-1000 m one-link walls beside pinned rivers (C fit peaks there)"
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: low
found_by: pw125
blocked_by: []
relates: [PW-125, PW-298]
refs: [planet/zoom.py, docs/review/zoom-polish/pw125.md, "world:592f2a(-9.35,-161.39)"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After PW-125, 28 undesigned drops >= 100 m are left on the arc zoom world:592f2a(-9.35,-161.39) (2000 km
@ 4 km; up to 803 m), 1 on 49.32,37.38 (582 m) and 1-2 on each 1 km zoom. They are real concentrated
steps: the stream's last 4 km link is >= 3x as steep as the stream above it (e.g. 55 m/km above, 200 m/km
for one link, 0.2 m/km on the river it joins). All form in the landscape pass.

Mechanism (traced with `debug.stages` and the pass's internals): the pinned coarse river courses hold
their floor at `z_course`, low against the rugged arc's cell means. The slope-fit field C is updated
per pixel by (tmean / hmean)^0.8 of ~20 km box means, and over 15 iterations it piles up next to the
pinned courses: C = 1172-2546 at the lip and the river beside it, 235-443 three pixels upstream. So a
47 m^3/s tributary's slope C Q^-0.5 jumps from ~15 to ~200 m/km at its last link. In the tiled reference
(pw125.md) this is also why the 4 km arc zoom's p99 pixel step is 1.6x what 1 km tiles averaged to 4 km
give (1439 vs 860 m).

To try (the C fit is PW-298's; maybe fold this into it): smooth C's update (fit it on the coarse cells'
means and interpolate smoothly, like `keep_means`), or fit against the relief above the drainage as
PW-298 suggests. Then the valley's mean comes from its sides rather than from walls at the tributaries'
mouths. Measure with the 8 zooms of world 592f2a (`stats.falls` kind `drop` >= 100 m by stage) and
the tiled reference's p99 step on the arc.
- [ ] drops >= 100 m on the arc zoom well under 28, with no loss of designed lips

## Updates
- 2026-10-15: Created from inbox draft draft-zoom-c-fit-steep-links-at-pinned-courses.md (found by pw125).
