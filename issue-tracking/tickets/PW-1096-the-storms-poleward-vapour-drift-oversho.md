---
id: PW-1096
title: The storms' poleward vapour drift overshoots at 40-50N (0.96 / 0.65 Sv vs NCEP-implied 0.83 / 0.52) while 30S stays at a quarter
type: task
status: todo
parent: PW-013
milestone: later
subsystem: climate
effort: m
impact: low
found_by: lane26b
blocked_by: []
relates: [PW-998, PW-013]
refs: [planet/climate.py, docs/review/base-climate/coasts/README.md]
created: 2026-10-30
updated: 2026-11-03
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

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Earth-only regional residual; Earth is a test analogue (PW-013 relation added).
- 2026-10-30: Owner 10-30 D11: moisture/monsoon-coast work parked for v2; an agent will find a downloadable drag source.
- 2026-10-30: Lane 58 (docs/review/base-climate/moisture-budget/README.md): eddy_drift 0.8 brings 50 N to 0.61 Sv (40 N 0.91) but moves 50-60 N land only
  -11 mm and polar land -20; no drift costs polar land 100 mm and the Pampas 70. The drift is ~15% of the 50-60 N
  land excess; not worth a retune on its own.
- 2026-10-30: Created from inbox draft draft-storm-drift-40n-overshoot.md (found by lane26b).
