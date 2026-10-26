---
id: PW-882
title: On v1-finish-12 the zoom names cloud forest from the light's shade, not the sky's cover (run and world pass sky)
type: task
status: todo
parent: null
milestone: v1
subsystem: zoom
effort: xs
impact: med
found_by: coupling-audit
blocked_by: []
relates: [PW-806, PW-808]
refs: [planet/zoom_vegetation.py, planet/vegetation.py, "worlds 6909cb 2a7385", docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Coupling audit finding C10 (severity low-med for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** v1-finish-12 planet/zoom_vegetation.py compute: V.site/V.model get shade_jul/jan only, no sky, so s["cloud"] falls back to the shade.

**Other side:** v1-finish-12 planet/world.py and earth.update_vegetation pass sky=(cloud_jul, cloud_jan); vegetation.classify's montane cloud forest test (cloud >= 0.65 above 1 km) reads s["cloud"].

**Why they disagree:** The PW-806/808 shade fix kept the sky for naming cloud forest in the run and worlds but not in zooms, so a zoom loses cloud forest its world has.

**Measured:** Tropical (|lat| < 25) land above 1 km, worlds 6909cb and 2a7385: mean sky cover 0.45 / 0.68 vs shade 0.39 / 0.59; cells at >= 0.65: 645 -> 423 and 1116 -> 837 (-34% and -25%).

**What to try:** Interpolate cloud_jul/jan in zoom_vegetation.fine_fields as before and pass sky= to the vegetation; land with the v1-finish-12 merge.

## Updates
- 2026-10-25: v1-finish-13 (1b52cdf): zoom_vegetation sets s['cloud'] from the world's sky cover (cloud_jul/jan), as the globe does.
- 2026-10-25: Created from inbox draft draft-zoom-cloud-forest-tested-on-shade-not-sky.md (found by coupling-audit).
