---
id: PW-320
title: "Zoom creep below 2 km: fine zooms are crept 4-16x less than physics says"
type: task
status: needs-decision
parent: null
subsystem: zoom
effort: s
impact: med
found_by: pw125
blocked_by: []
relates: [PW-125]
refs: [planet/zoom.py, docs/review/zoom-polish/pw125.md, "world:592f2a(49.32,37.38)", "world:592f2a(26.74,-49.92)"]
created: 2026-10-15
updated: 2026-10-16
---

## Description
PW-125 made creep a diffusivity above 2 km (`zoom.creep_kd`: per-step share x (2 km / res)^2, owner
decision), but finer zooms keep the 2 km share per pixel. In km terms a 1 km zoom creeps with 1/4 of
the 2 km diffusivity and a 0.5 km zoom with 1/16. Measured on world 592f2a (docs/review/zoom-polish/pw125.md):
a 1000 km @ 2 km zoom is smoother than 1 km tiles of the same area averaged to 2 km (mean |Laplacian|
98 vs 176 m on the range 49.32,37.38; 30 vs 40 m on the interior plain 26.74,-49.92). The difference
is the creep:
- 1 km tiles crept at the 2 km diffusivity (4x the steps at kd 0.25), averaged to 2 km: 92 / 28 m,
  matching the 2 km zoom (98 / 30).
- the 2 km zoom crept at the 1 km diffusivity (kd / 4): 238 / 45 m, near the 1 km tiles (176 / 40).
So with one diffusivity at every pixel size, zooms of one place at different resolutions agree; with the
current rule they don't.

Options:
- A. One diffusivity everywhere: below 2 km, more steps of at most kd 0.25 (1 km: 24 steps, 0.5 km: 96;
  `diffuse` is cheap, ~ms per step at 500 px). Fine zooms get visibly smoother (1 km Laplacian at 2 km
  scale ~176 -> ~92 m on the range), and consistent with the 2 and 4 km ones. Check D8 streaks and that
  the stream no-lift rule still holds with many steps.
- B. Keep as is: fine zooms rougher than the coarse ones say, by the numbers above.
- C. Set the reference at 1 km instead (KD_RES_KM = 1): coarser zooms get rougher still (4 km kd /16).
Lean: A, it is the same physics as C above 2 km; but it changes every 1 km and 0.5 km zoom's look, so it
wants a look at hillshades first.

## Updates
- 2026-10-16: Decision prepared (zoom batch 2): docs/review/zoom-polish/pw320.md with hillshade pairs pw320_{range,plain}_{1km,05km}.png (current | A). Option A is on local branch pw320-option-a (one commit), not merged. Zooms of one place averaged to 2 km, mean |Laplacian|: range 2 km zoom 103; 1 km current 161 -> A 82; 0.5 km (vs the 2 km zoom's middle, 69) current 183 -> A 67. Plain 25; 1 km 31 -> 23; 0.5 km (vs 15) 30 -> 22. A makes resolutions agree, but 0.5 km zooms lose their pixel-scale ridges and gullies (96 steps); alternative noted: A down to 1 km only (0.5 km at the 1 km step count, 4x today's diffusivity rather than 16x). Drops on the 1 km showcase zooms 2/1 -> 3/1 (noise), cost negligible.
- 2026-10-15: Zoom batch 2 agent preparing hillshade pairs (current vs one diffusivity) for the owner's call; no behaviour change merged.
- 2026-10-15: Created from inbox draft draft-zoom-creep-below-2km.md (found by pw125).
