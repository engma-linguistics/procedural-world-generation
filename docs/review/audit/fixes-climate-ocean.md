# Audit fixes: climate and ocean (2026-10-15)

Branch `worktree-agent-abb0b6d2589154fc4`. Tickets PW-267, PW-265, PW-266, PW-278 and PW-264, one commit each, plus a follow-up commit for PW-266: a NaN guard in the kernel's Budyko for a trace of rain, found by the health sweep.

## What changed
- **PW-267:** the rain kernel's mm/yr, which it uses for the wet-cool / dry-hot showers, now use `mean_mm × e^(0.03 dT)`. Outputs at dT = 0 are unchanged.
- **PW-265:** `moc_zonal` = 1. The overturning's warmth stays within its latitude band. No re-centring: Earth's global mean was 0.5 °C above NCEP's and is now 0.3 °C above.
- **PW-266:** the kernel's land evaporation is now `water_balance`'s Budyko AET, per half-year with the soil carry-over and Fu's w per cell, on first-pass PET. The air takes up water only through open sea. Vegetation's separate `et` share is gone: plants recycle through w, so keeping `et` would count them twice. `ocean.freshwater` still takes the mean off, but now warns above 2 cm/yr.
- **PW-278:** `WEATHER_K` 0.12 → 0.09.
- **PW-264:** the CO2 baselines learn over ≤ 1 Gyr (`REF_MYR`) instead of ≤ 200 Myr.

## Fixed-planet probe (climate.compute at dT = 0; L6 planets saved from 400 Myr runs, and Earth)
| | main | PW-265 | PW-266 |
|---|---|---|---|
| ocean-mean SST warming by the overturning, seed 3199 / Earth (°C) | +0.57 / +0.22 | +0.01 / +0.03 | +0.00 / +0.02 |
| poleward of 45° (°C) | +1.43 / +0.64 | +0.05 / +0.10 | |
| global mean T, seed 3199 / Earth (°C; NCEP 14.03) | 13.63 / 14.54 | 13.21 / 14.36 | 13.17 / 14.32 |
| fresh-water mean taken off, seed 3199 / seed 11 / Earth (m/yr) | −0.021 / −0.025 / −0.032 | same | +0.005 / −0.010 / +0.001 |
| land rain, seed 3199 / seed 11 / Earth (mm) | 800 / 920 / 772 | same | 926 / 1039 / 918 |

## earth_check (L6; baseline docs/review/baseline-2026-10-15)
| | main | PW-265 | PW-266 (= final; PW-278 and PW-264 act only in runs) | observed |
|---|---|---|---|---|
| Köppen group / exact (%) | 71.75 / 38.92 | 71.34 / 38.52 | 71.23 / 33.01 | |
| B share of land, excl. Antarctica (%) | 28.9 | 28.9 | 20.3 | 30.1 |
| land P mean / median (mm) | 840 / 515 | 840 / 515 | 1008 / 737 | 791 / 546 |
| global T (°C) | 14.54 | 14.37 | 14.34 | 14.03 |
| point score exact / group / miss | 33 / 27 / 18 | 33 / 26 / 19 | 29 / 34 / 15 | |

PW-265 costs 0.4 points of Köppen group agreement, a little more than the ticket's ~0.3. PW-266 costs 5.9 points of exact agreement, because dry interiors now recycle their own rain (Australia interior 463 → 837 mm against 291 observed, Gobi 303 → 582 against 157). Regions that were too dry improve: Great Plains 264 → 640 (obs 550), W Siberia 271 → 557 (obs 503), and the Pampas group match goes from 5% to 74%. Filed as a needs-decision draft (`draft-climate-ocean-recycling-wets-dry-interiors.md`).

## Scorecard (final; seeds 1 and 2 at 1000 Myr)
| | main | final |
|---|---|---|
| Earth group / exact / log-rain corr | (not measured in the baseline) | 71.2 / 33.0 / 0.61 |
| seed 1: dry % / ice % / ocean age / NPP / tree cover | 32.0 / 0.0 / 73.6 / 395 / 23.3 | 18.5 / 0.6 / 95.9 / 329 / 29.2 |
| seed 2: same | 37.2 / 3.6 / 41.5 / 327 / 19.8 | 20.7 / 3.3 / 66.9 / 282 / 29.3 |

## health --quick (8 L6 seeds, 500 Myr; docs/review/health-climate-ocean)
| (mean of the per-seed medians, range) | main | final |
|---|---|---|
| temp (°C) | 14.8 (12.8–16.7) | 14.9 (13.1–16.7) |
| per-seed min / max temp (°C) | 2.2–11.1 / 18.0–23.7 | 3.0–12.1 / 18.4–22.6 |
| dT range per run (°C) | 8.4–19.1 | 10.0–18.4 |
| dry_pct | 36.7 (30.2–44.7) | 27.4 (23.6–30.6) |
| inland_pct (envelope 8–30) | 10.8 (8.6–14.1) | 7.5 (6.2–8.6) |
| trees_pct / npp | 26.9 / 356 | 30.7 / 339 |
| deepest ice sea level: seed 11 / 42 / 3199 (m) | −360 / −304 / −129 | −206 / −45 / −174 |
| frames with ice SL < −150 m: seeds 2 / 11 / 42 / 3199 (%) | 6.2 / 15.0 / 13.3 / 0 | 0 / 6.2 / 0 / 7.1 |

With the slower baselines (PW-264), the temperature spread stays within the envelopes (8–30 °C for the medians; dT range ≤ 25). Cold eras are mostly milder and shorter, even though PW-278's weaker thermostat should make them longer: the wetter, greener land and the slower baselines outweigh it. Seed 3199 got a deeper cold era. Less land drains inland (`inland_pct` is now below its 8% envelope on all 8 seeds): wetter land fills and overflows its closed basins (PW-054).

Not measured: veg_check (it needs an Earth world in a `worlds/` store, which this worktree doesn't have), L7 (PW-290), the 1 Gyr sweep (PW-240's −384 m is from it).
