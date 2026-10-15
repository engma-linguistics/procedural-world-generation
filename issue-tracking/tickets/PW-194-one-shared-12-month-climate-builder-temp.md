---
id: PW-194
title: One shared 12-month climate builder (temperature, rain, PET, PAR, snow) for koppen, water balance, glaciers and vegetation
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: med
found_by: vegprop
blocked_by: []
relates: [PW-187, PW-185]
refs: [planet/climate.py, planet/tectonics/earth.py, planet/zoom.py, docs/proposals/vegetation.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The climate stores only annual, warmest/coldest-month temperature and two half-year rain rates. Several places rebuild months from these on their own, each slightly differently: `climate.koppen` (sinusoidal rain through p_jul/p_jan), `climate.pet_months` (sinusoidal temperature, Oudin PET), `tectonics/earth.py degree_days` (12 months with a daily spread), the zoom's glacier snow fraction (`zoom.py` ~l.872) and the time zoom. The vegetation model (PW-187, proposal docs/proposals/vegetation.md §1.3, §3.1) and soils (PW-185) need the same months plus GDD5, snowpack, an absolute-minimum temperature estimate and PAR (insolation x cloud).

Do: a `climate.months(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud=None)` helper returning (12, n) arrays of temperature, rain, PET, PAR and snow, used by the new code and (where it doesn't change results, or with a golden update) by the existing callers. Also keep `cloud_jul/jan` on the simulation in `update_climate` (computed by `climate.compute` but dropped today) so the run's vegetation can use cloudiness for light.
- [ ] helper with tests (month sums match the half-year inputs; PET sums match `water_balance`'s pet)
- [ ] sim keeps cloud_jul/jan

## Updates
- 2026-10-14: Created from inbox draft draft-climate-monthly-fields.md (found by vegprop).
