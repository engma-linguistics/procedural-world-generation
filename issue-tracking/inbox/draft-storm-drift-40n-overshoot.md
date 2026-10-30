---
title: "The storms' poleward vapour drift overshoots at 40-50N (0.96 / 0.65 Sv vs NCEP-implied 0.83 / 0.52) while 30S stays at a quarter"
type: task
status: todo
parent: PW-013
milestone: v1
subsystem: climate
effort: m
impact: low
found_by: lane26b
blocked_by: []
relates: [PW-998]
refs: [planet/climate.py, docs/review/base-climate/coasts/README.md]
---

## Description
PW-998 round 3 (e81915cd, `face_winds`' eddy_drift 1 m/s x the storm track's storminess) moves Earth's northward
vapour transport toward NCEP E - GPCP P:
- 30N: +0.19 -> +0.41 Sv (NCEP-implied +0.72)
- 30S: -0.03 -> -0.31 Sv (-1.24)
- 40N: +0.74 -> +0.96 Sv, past +0.83
- 50N: +0.46 -> +0.65 Sv, past +0.52

Riding the jet's storm tracks instead of the whole storminess didn't change this; the tracks peak there. The
subtropics' moisture divide is still at ~25N/~28S (NCEP ~18N/~12S). Open:
- Is the drift's magnitude per latitude right? u_e ~ 1 m/s is an unverified back-of-envelope figure; a source is
  on docs/references/wishlist.md.
- The southern hemisphere's shortfall may be its storm track's strength over the open Southern Ocean.

Only after the package judge (draft-coasts-package-judge-icebox).
