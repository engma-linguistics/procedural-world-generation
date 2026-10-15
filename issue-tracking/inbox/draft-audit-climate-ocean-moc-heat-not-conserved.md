---
title: "Overturning heat is a net source: moc_zonal = 0 double-counts warmth t_eq already holds (kept for +0.19 pt Köppen)"
type: task
status: needs-decision
parent: PW-245
subsystem: ocean
effort: s
impact: med
found_by: audit-climate-ocean
blocked_by: []
relates: [PW-038, PW-013]
refs: [planet/climate.py, planet/ocean.py, docs/review/audit/climate-ocean.md]
---

## Description
`sea_surface` (climate.py:822-826) and `ocean.solve.sst_c` (ocean.py:588-592) add the overturning inflow's warmth `E` to the SST and subtract `moc_zonal × zonal_mean(E)`. `TUNE["moc_zonal"]` is 0. The inflow's heat is also never taken out of the low latitudes it comes from. So the overturning is a net heat source. The code itself says why that double-counts: "t_eq was fitted to Earth's sea, overturning and all". The gyres, by contrast, conserve heat per band. Commit d909b83 chose 0 because "the Köppen score preferred this (70.69% against 70.50%)". That is a bandaid kept for a metric.

Measured on run a1d3b9 (last frame on L6, dT = 0):

| moc_zonal | Ocean-mean SST warming | Poleward of 45° | Global mean T |
|---|---|---|---|
| 0 | +0.52 °C | +0.98 °C | 14.41 °C |
| 0.5 | +0.26 °C | +0.50 °C | 14.22 °C |
| 1 | +0.02 °C | +0.06 °C | 14.04 °C |

The sinking (~16 Sv per site) is unchanged across the three.

Options:
- A: `moc_zonal` = 1 (one-line change). Heat stays within its band: the inflow's longitudes warm and the rest of the band cools. This is a sound and simple approximation.
- B: take the heat from the source instead: cool the cells equatorward of `moc_src_lat` along the routes by what the inflow carries (∑ area·ΔSST ≈ 0). This is closer to the real AMOC, which cools the South Atlantic and tropics.
- C: keep 0 and document it as Earth-calibrated. Not recommended: it only works because t_eq is Earth's.

Lean: A now, B if a later pass wants the tropics to feel it. Re-centre the global mean (curve offset, ~+0.35 °C) if needed, then re-run earth_check, the scorecard and the golden tests.
- [ ] area-weighted SST change from the overturning ≈ 0
- [ ] earth_check Köppen within ~0.3 pt of before
