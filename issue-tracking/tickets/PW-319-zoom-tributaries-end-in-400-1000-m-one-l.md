---
id: PW-319
title: "Zoom: tributaries end in 400-1000 m one-link walls beside pinned rivers (C fit peaks there)"
type: task
status: wontdo
parent: null
milestone: null
subsystem: zoom
effort: m
impact: low
found_by: pw125
blocked_by: []
relates: [PW-125, PW-298]
refs: [planet/zoom/regional.py, docs/review/zoom-polish/pw125.md, "world:592f2a(-9.35,-161.39)"]
created: 2026-10-15
updated: 2026-10-16
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
- 2026-10-16: Status in-progress -> wontdo. Stopped (zoom batch 2): C fit never settles (max x1.5 per pass); smoothing C helps drops but moves inland bias -25..-67 m. Coordinator: fold into PW-298.
- 2026-10-16: Measured (zoom batch 2, after PW-321's halo; arc zoom 592f2a -9.35,-161.39 2000@4 km): the C fit winds up. C *= clip(tmean/hmean)^0.8 per pixel never converges where a box can't reach its target mean (pinned low courses, the summit taper/cap, MAX_SLOPE): over 15 iterations C's max grows ~1.5x each (52 -> 32,874), p95 45 -> 876, 2.8% of land at MAX_SLOPE, box ratio p95 still 1.11. C at the drops' lips is 2-6x C three px upstream (1211/261, 2677/423, 1922/575 ...), so the last link is a wall. Option tried: smooth log C over the fit's own box after each update (C as the smooth field the docstring describes). It stops the windup (max 3,345, still creeping; lip ~= upstream C) and takes arc drops >= 100 m 29 -> 22, max 855 -> 424 m, p99 pixel step 1286 -> 1176 m; but it moves inland cell-mean bias/RMS: arc +9/146 -> -30/156, 49.32,37.38 +41/145 -> +14/136, 1.96,-70.44 (1 km) -18/102 -> -45/122, 4.81,-72.18 (1 km) +61/154 -> -7/161; drops on the others 1/2/1 -> 1/1/2. Not merged: 22 is not 'well under 28', and the bias shifts are PW-298's metric. The remaining 22 have equal C at lip and upstream, so something else concentrates them (rock K contrasts in 'rough', floors/banks of held courses: not yet traced). Lean: fold into PW-298 as one C-fit redesign: a smooth C (fitted on cell or box means, interpolated) with an anti-windup (no update where the box can't respond: held/capped pixels out of the comparison), measured on both metrics.
- 2026-10-15: Status todo -> in-progress. Zoom batch 2 agent started.
- 2026-10-15: Created from inbox draft draft-zoom-c-fit-steep-links-at-pinned-courses.md (found by pw125).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
