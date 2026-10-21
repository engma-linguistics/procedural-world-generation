---
id: PW-414
title: Penman lake evaporation uses a fixed 2 m/s wind, sea-level pressure and air temperature for the water
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: s
impact: low
found_by: pw358
blocked_by: []
relates: [PW-358, PW-300]
refs: [planet/climate.py, docs/review/health-pw358-after/diag/lake_probe.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`climate.open_water_evap` (PW-358) makes three simplifications that are sound but leave known errors
on Earth L6 (`docs/review/health-pw358-after/diag/lake_probe.py`):
- **Wind** is FAO-56's default of 2 m/s everywhere (`TUNE["lake_wind"]`). The climate has surface winds
  (`wind_jul`/`wind_jan`); u2 ~ 0.75 x a 10 m wind (FAO-56 log profile). Windy steppe and trade-wind
  lakes would evaporate more, and sheltered ones less.
- **The psychrometric constant** is the sea-level value (0.0665 kPa/C). At altitude it falls with
  pressure (FAO-56 eq. 7-8: gamma = 0.000665 x 101.3 ((293 - 0.0065 z) / 293)^5.26), so high lakes get
  relatively more of their evaporation from radiation. Lake Titicaca comes out at 305 mm against ~1700.
  Most of that gap is the model cell's mean temperature of -0.2 C, though, not gamma.
- **The water's temperature is the air's**, month by month, with no heat storage. Deep lakes lag the air
  and evaporate most in autumn and early winter: Lake Michigan comes out at 1050 mm against ~650.
Only worth doing if PW-300's re-check shows lake sizes are sensitive to these. PW-358 found that the
giant lakes are held mainly by the open/closed switch of the outlet carving, not by evaporation.
- [ ] model wind (and optionally elevation pressure) in open_water_evap; Earth lake probe re-run

## Updates
- 2026-10-16: Created from inbox draft draft-penman-lakes-wind-height-storage.md (found by pw358).
