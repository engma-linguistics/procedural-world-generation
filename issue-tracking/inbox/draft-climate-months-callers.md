---
title: Switch koppen, the water balance and the glacier and time-zoom snow rules to climate.months
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: low
found_by: veg
blocked_by: []
relates: [PW-194]
refs: [planet/climate.py, planet/tectonics/earth.py, planet/zoom.py, planet/timezoom.py]
---

## Description
PW-194's builder `climate.months` (veg branch) now serves the vegetation and `pet_months` (identical PET, output-neutral). The other callers still build their own months:
- `koppen()` uses the analytic extremes of a continuous sinusoid (lo/hi = mean(1 -+ |a|)) for the driest month, not the 12 discrete months; switching to `month_rain` changes some B/C/D boundaries (the discrete months' extremes are ~5% smaller), so it needs a golden update and a fresh `tools/earth_check.py` (Koppen agreement).
- `earth.degree_days` (ice sheets) uses cos(2 pi m/12) months with a daily spread; `months()` has the same Reeh spread for GDD5 but a July/January peak per hemisphere and clipping to [t_cold, t_warm]. Switching shifts ice margins slightly.
- the zoom's glacier snow fraction and the time zoom's monthly snow have their own rules.
Not done in PW-187 because none of these is output-neutral. Do it in one go with golden and Earth-check updates, or decide they stay separate.
- [ ] koppen on month_rain / month_temps (earth_check before/after)
- [ ] ice_sheets on months() degree-days, zoom/time-zoom snow on months()
