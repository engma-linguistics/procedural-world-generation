---
id: PW-810
title: The star thermostat (PW-791) is in the code, opt-in and off, but unmeasured
type: task
status: todo
parent: PW-791
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: v1-finish-9
blocked_by: []
relates: [PW-791, PW-780]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, docs/review/base-climate/v1-finish-9/launch.sh]
created: 2026-10-24
updated: 2026-10-24
---

## Description
v1-finish-9 added `earth.star_control` (params `star_thermostat`, default False; `star_ice_lo` 0.10, `star_ice_hi`
0.35, `star_window` 100 Myr, `star_gain` 0.2 C/Myr per unit share, `star_control_max` +-4% of luminosity = +-7.7 C,
`star_control_from` 200 Myr). It follows the planet's running icehouse share (land ice holding >= 20 m of sea
level, e-folding over 100 Myr) and moves the star's forcing only; CO2 stays the carbon cycle's outcome. Labelled as a
control in params.py; recorded in ice_diag's steps (`star`, `star_ctl`, `ice_share`). The earthlike preset does NOT
turn it on (owner ruling: the anchored star first). A sweep with it on was started and stopped when the star-anchor
ruling arrived: no numbers yet.
- [ ] after the star anchor, run `docs/review/base-climate/v1-finish-9/launch.sh` (it sets star_thermostat=1) and
  judge the strict bar; make it the earthlike default only if the anchored star still leaves runaway worlds
- [ ] if it becomes a default, add it to the world summary as a non-physical control
- [ ] gain and band: check the overshoot (the 100 Myr memory lags; an integral control can wind up)

## Updates
- 2026-10-24: v1-finish-10: measured on the anchored star (full Gough): passes rise from 0/6 to 3/6 (first wave) but runs end at pCO2 25-251 ppm with treeless wet tropics; not a default. docs/review/base-climate/v1-finish-10/README.md
- 2026-10-24: Measure after PW-809; default only if the anchored star still runs away.
- 2026-10-24: Created from inbox draft draft-star-thermostat-unmeasured.md (found by v1-finish-9).
