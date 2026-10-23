# Health sweep 2026-10-23 01:03

Commit 3a25e95. 8 runs (default params, `--every 4`) at 4 workers x 2 numba threads; simulations 15.5 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | 465182 | 441 | 132 / 412 | 11.8 | 0 | 17.6 | 0.956 | 29.4 | 0.0 | ok | ok | 43.1 |
| 2 | 6 | 500 | cbe366 | 417 | 140 / 396 | 16.2 | 0 | 2.0 | 0.97 | 19.6 | 0.0 | ok | ok | 51.0 |
| 11 | 6 | 500 | 4fdd05 | 426 | 128 / 372 | 9.2 | 0 | 0.0 | 0.967 | 0.0 | 0.0 | ok | ok | 68.6 |
| 21 | 6 | 500 | c80e28 | 522 | 136 / 404 | 12.9 | 0 | 5.9 | 0.966 | 23.5 | 0.0 | ok | ok | 54.9 |
| 3199 | 6 | 500 | 8698e2 | 409 | 132 / 376 | 7.8 | 0 | 0.0 | 0.974 | 0.0 | 0.0 | ok | F: icehouse 73% of the time, outside 5-70% | 72.5 |
| 42 | 6 | 500 | f6611e | 464 | 116 / 404 | 14.4 | 0 | 0.0 | 0.977 | 49.0 | 0.0 | ok | F: icehouse 86% of the time, outside 5-70% | 86.3 |
| 77 | 6 | 500 | 1ad5e3 | 414 | 124 / 416 | 10.2 | 0 | 13.7 | 0.987 | 60.8 | 0.0 | ok | F: icehouse 100% of the time, outside 5-70% | 100.0 |
| 505 | 6 | 500 | d267c7 | 406 | 132 / 416 | 9.2 | 0 | 0.0 | 0.96 | 0.0 | 0.0 | ok | ok | 7.8 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 31.5 | 40.4 | 33.5 | 15.0 | 54.7 | 4.0 | 86.1 | -17.0 | 96.1 | 1.0 | 13.7 | -0.5 | 18.5 | 1.7 | 0.5 | 0.1 | 4.3 | 39.2 | 345.3 | 10.0 | 14.4 |
| 2 | 6 | 32.4 | 39.1 | 34.5 | 11.0 | 56.5 | 4.8 | 39.3 | -20.6 | 53.2 | 1.7 | 14.3 | 0.1 | 22.4 | 3.6 | 0.5 | 0.1 | 6.5 | 35.1 | 309.4 | 7.0 | 19.9 |
| 11 | 6 | 33.0 | 39.5 | 34.6 | 11.0 | 65.4 | 3.7 | -73.7 | -65.3 | 39.8 | 2.5 | 13.7 | -0.7 | 25.5 | 3.4 | 0.4 | 0.1 | 4.6 | 28.8 | 239.2 | 4.0 | 33.4 |
| 21 | 6 | 31.2 | 40.2 | 33.7 | 15.0 | 46.0 | 4.0 | 188.5 | -27.1 | 211.6 | 1.4 | 12.2 | -1.2 | 22.1 | 2.8 | 0.4 | 0.1 | 4.4 | 33.1 | 317.3 | 8.0 | 28.0 |
| 3199 | 6 | 32.0 | 39.4 | 34.5 | 11.0 | 55.6 | 4.5 | 12.0 | -45.3 | 65.1 | 2.2 | 11.9 | -0.4 | 31.1 | 3.4 | 0.2 | 0.1 | 6.3 | 24.7 | 314.6 | 8.0 | 19.0 |
| 42 | 6 | 31.1 | 39.6 | 34.4 | 10.0 | 53.4 | 4.5 | -26.9 | -120.7 | 91.2 | 5.1 | 9.8 | -0.7 | 17.8 | 2.4 | 0.4 | 0.1 | 5.0 | 38.5 | 345.7 | 8.0 | 20.5 |
| 77 | 6 | 32.0 | 39.2 | 35.2 | 13.0 | 51.8 | 4.9 | -101.0 | -192.6 | 104.5 | 6.3 | 12.2 | -0.4 | 23.8 | 4.4 | 0.6 | 0.2 | 5.4 | 26.5 | 309.8 | 7.0 | 15.7 |
| 505 | 6 | 33.0 | 39.9 | 33.7 | 10.0 | 50.6 | 4.0 | 113.6 | -2.1 | 113.6 | 0.2 | 14.9 | -0.2 | 29.9 | 2.1 | 0.1 | 0.0 | 4.6 | 21.6 | 398.9 | 5.0 | 22.0 |

Measured on the run's keyframes (no slicing). A keyframe's rivers and lakes are routed on its own terrain (PW-239), so `inland_raw_pct` (every routed end on land, as highlights counts it) and `inland_pct` (ends that are closed lakes, salt pans or real pits) agree but for ends under land ice. Land ice and land shares use cells (near-equal area).

## Envelopes

| metric | low | high | Earth | source |
|---|---|---|---|---|
| land, % of surface (`land_pct`) | 22 | 42 | 29.20 | tests/test_envelopes.py (22-42%); Earth 29.2% |
| continental crust, % of surface (`cont_pct`) | 33 | 50 | 41 | tests/test_envelopes.py (33-50%); Earth ~41% with shelves (Cogley 1984) |
| mean continental crust thickness, km (`cont_km`) | 31 | 40 | 39 | target 35 km (PW-238, continental_thickness); Earth ~39 km (Christensen & Mooney 1995); known thinning to 32-33 km (PW-046) |
| plates (`plates`) | 5 | 30 | 15 | tests/test_envelopes.py (5-30; max_plates 30); Earth 7 major + ~8 minor; <= 4 is the PW-191 collapse |
| mean ocean-floor age, Myr (`ocean_age`) | 25 | 120 | 64 | tests/test_envelopes.py (25-120); Earth ~64 Myr (Mueller et al. 2008); PW-051 |
| mean plate speed, cm/yr (`speed`) | 2 | 9 | 4.50 | tests/test_envelopes.py (2-9 cm/yr); Earth ~4-5 |
| sea level, m (ice + ocean basins) (`sea_level`) | -250 | 300 | 0 | Phanerozoic ~-130 (LGM) .. +250 m (earth.py; Haq & Schutter 2008); -250: PW-240's hard goal |
| sea level from land ice, m (`sea_ice_m`) | -250 | - | 0 | Earth LGM ~-130 m; PW-240 goal -150 m typical / -250 m worst |
| sea level from the ocean basins, m (the other part of sea_level) (`sea_tect_m`) | -250 | 300 | 0 | PW-293/549: the floor's mean depth against the start's; Phanerozoic ~-100..+250 m without the ice (Haq & Schutter 2008; Mueller et al. 2008) |
| land ice, % of surface (`ice_pct`) | - | 10 | 3.10 | Earth 3.1% now (earth.EARTH_ICE), ~7-8% at the LGM |
| global mean temperature, C (`temp`) | 8 | 30 | 14.50 | Earth 14.5 C; LGM ~8 C (Tierney et al. 2020); Phanerozoic hothouses to ~30 C (Scotese et al. 2021) |
| CO2 index (ln(source/sink) / WEATHER_CO2) (`co2`) | -3.0 | 3.0 | 0.00 | the forcing's clip in earth.py (+-CO2_MAX = 3); Earth 0 |
| arid (Koppen B), % of land (`dry_pct`) | 12 | 45 | 30 | tests/test_envelopes.py (12-45%); Earth ~30% (Beck et al. 2018) |
| land draining inland, % of ice-free land (to a closed lake, salt pan or real pit) (`inland_pct`) | 8 | 30 | 18 | Earth ~18% (overview 2.9); L6 known ~9.5-11% (PW-054, PW-243). `inland_raw_pct` (not checked) follows the stored `downstream` to any end, as highlights does; since PW-239 the two agree but for ends under land ice |
| lakes, % of land (`lake_pct`) | 0.2 | 3.0 | 1.80 | Earth ~1.8% of ice-free land (HydroLAKES, Messager et al. 2016); generated L6 worlds 0.5-1% |
| largest lake, million km2 (`lake_max_mkm2`) | - | 1.0 | 0.37 | Caspian 0.37 Mkm2; 1 Mkm2 = the overview's giant lake (2.9) |
| highest peak, km (`max_elev_km`) | - | 9.5 | 8.85 | Everest 8.85 km; PW-172 (spikes above ~9.5 km) |
| tree cover, % of ice-free land (after forests appear) (`trees_pct`) | 10 | 50 | 30 | Earth ~30% potential canopy (forest 55-60 of ~130 Mkm2, overview 2.18) |
| land NPP, g C/m2/yr (after flowering trees appear) (`npp`) | 200 | 700 | 430 | Earth ~56 Pg C/yr over ~130 Mkm2 = ~430; the model on Earth's terrain 50 Pg C/yr, ~385 (overview 2.18). Before flowering trees (plant group 4) stand-ins grow at 70%, so runs sit at ~150-280 |
| landmasses (>= 3 cells) (`landmasses`) | 3 | 80 | - | loose: a lone supercontinent or a shattered archipelago |
| largest landmass, % of surface (`largest_pct`) | 5 | 35 | 16.60 | Afro-Eurasia 16.6%; a Pangaea ~30% (scorecard largest_max) |
| global temperature range over the run, C (`dT_range`, per run) | - | 25 | 25 | Phanerozoic 11-36 C (Scotese et al. 2021) |
| keyframes with a peak above 9.5 km (`peak_frames`, per run) | - | 0 | 0 | PW-172 (L7 seed 3199: 3 of 251) |
| % of keyframes with a lake over 1 Mkm2 (`giant_lake_frames`, per run) | - | 5 | 0 | overview 2.9 (L6: 3 of ~150 frames) |
| continental crust volume, end / start (`volume_ratio`, per run) | 0.9 | 1.1 | 1.0 | scorecard volume_ratio (x1.006) |
| % of keyframes with ice sea level below -150 m (`sea_ice_below_150`, per run) | - | 10 | 0 | PW-240 |
| % of keyframes with <= 4 plates (`low_plates`, per run) | - | 2 | 0 | PW-191 (L7 seed 21: 1%) |

## Top outliers (of 61 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 77 | 6 | sea_ice_below_150 | run | - | 60.80 | -..10 | 5.08 |
| 42 | 6 | sea_ice_below_150 | run | - | 49.00 | -..10 | 3.9 |
| 1 | 6 | giant_lake_frames | run | - | 17.60 | -..5 | 2.52 |
| 1 | 6 | sea_ice_below_150 | run | - | 29.40 | -..10 | 1.94 |
| 77 | 6 | giant_lake_frames | run | - | 13.70 | -..5 | 1.74 |
| 21 | 6 | sea_ice_below_150 | run | - | 23.50 | -..10 | 1.35 |
| 2 | 6 | sea_ice_below_150 | run | - | 19.60 | -..10 | 0.96 |
| 2 | 6 | lake_max_mkm2 | 492-492 | 1 | 3.24 | -..1.0 | 0.465 |
| 21 | 6 | lake_max_mkm2 | 304-304 | 1 | 2.10 | -..1.0 | 0.23 |
| 1 | 6 | lake_max_mkm2 | 456-464 | 3 | 1.98 | -..1.0 | 0.219 |
| 77 | 6 | lake_max_mkm2 | 444-452 | 3 | 1.92 | -..1.0 | 0.205 |
| 1 | 6 | lake_max_mkm2 | 476-500 | 5 | 1.84 | -..1.0 | 0.202 |
| 42 | 6 | inland_pct | 300-500 | 51 | 0.73 | 8..30 | 0.2 |
| 505 | 6 | inland_pct | 300-500 | 51 | 0.93 | 8..30 | 0.194 |
| 1 | 6 | inland_pct | 300-496 | 48 | 0.78 | 8..30 | 0.191 |
| 11 | 6 | inland_pct | 300-500 | 51 | 1.04 | 8..30 | 0.191 |
| 3199 | 6 | inland_pct | 300-496 | 49 | 1.16 | 8..30 | 0.183 |
| 21 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 2 | 6 | sea_ice_m | 468-500 | 9 | -401.70 | -250..- | 0.165 |
| 77 | 6 | lake_max_mkm2 | 320-328 | 3 | 1.71 | -..1.0 | 0.158 |
| 2 | 6 | inland_pct | 344-500 | 39 | 1.23 | 8..30 | 0.157 |
| 21 | 6 | sea_level | 460-500 | 11 | -546.00 | -250..300 | 0.155 |
| 21 | 6 | inland_pct | 308-424 | 28 | 0.82 | 8..30 | 0.138 |
| 2 | 6 | sea_level | 464-500 | 10 | -497.90 | -250..300 | 0.126 |
| 77 | 6 | inland_pct | 352-440 | 22 | 1.28 | 8..30 | 0.114 |
| 21 | 6 | inland_pct | 436-500 | 17 | 1.38 | 8..30 | 0.101 |
| 1 | 6 | lake_max_mkm2 | 444-444 | 1 | 1.46 | -..1.0 | 0.095 |
| 77 | 6 | inland_pct | 452-500 | 13 | 1.69 | 8..30 | 0.087 |
| 2 | 6 | ice_pct | 472-500 | 8 | 12.70 | -..10 | 0.071 |
| 42 | 6 | temp | 424-492 | 18 | 3.50 | 8..30 | 0.07 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run 465182)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 28.16 | 31.53 | 32.54 |  |
| cont_pct | 39.29 | 40.44 | 42.09 |  |
| cont_km | 32.25 | 33.46 | 34.19 |  |
| plates | 11.00 | 15.00 | 17.00 |  |
| ocean_age | 50.60 | 54.70 | 68.20 |  |
| speed | 2.08 | 4.05 | 4.68 |  |
| sea_level | -214.70 | 86.10 | 102.60 |  |
| sea_ice_m | -225.90 | -17.00 | -4.20 |  |
| sea_tect_m | -18.30 | 96.10 | 114.40 |  |
| ice_pct | 0.30 | 1.00 | 7.50 |  |
| temp | 7.10 | 13.70 | 18.90 | 480-500: 7.10 |
| co2 | -0.98 | -0.49 | -0.16 |  |
| dry_pct | 12.85 | 18.46 | 25.17 |  |
| inland_pct | 0.78 | 1.67 | 12.22 | 300-496: 0.78 |
| lake_pct | 0.19 | 0.45 | 2.87 | 408-408: 0.19 |
| lake_max_mkm2 | 0.03 | 0.11 | 1.98 | 444-444: 1.46; 456-464: 1.98; 476-500: 1.84 |
| max_elev_km | 3.25 | 4.28 | 8.03 |  |
| trees_pct | 27.84 | 39.24 | 45.75 |  |
| npp | 234.70 | 345.30 | 360.00 |  |
| landmasses | 8.00 | 10.00 | 16.00 |  |
| largest_pct | 10.20 | 14.40 | 20.80 |  |

### Seed 2, L6 (run cbe366)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.08 | 32.37 | 32.70 |  |
| cont_pct | 37.44 | 39.12 | 39.92 |  |
| cont_km | 33.98 | 34.52 | 36.20 |  |
| plates | 9.00 | 11.00 | 14.00 |  |
| ocean_age | 45.80 | 56.50 | 75.20 |  |
| speed | 3.30 | 4.80 | 5.39 |  |
| sea_level | -497.90 | 39.30 | 124.20 | 464-500: -497.90 |
| sea_ice_m | -401.70 | -20.60 | -6.80 | 468-500: -401.70 |
| sea_tect_m | -100.10 | 53.20 | 143.80 |  |
| ice_pct | 0.70 | 1.70 | 12.70 | 472-500: 12.70 |
| temp | 2.90 | 14.30 | 19.10 | 464-500: 2.90 |
| co2 | -0.73 | 0.06 | 0.95 |  |
| dry_pct | 19.72 | 22.36 | 31.41 |  |
| inland_pct | 1.23 | 3.65 | 12.90 | 300-332: 3.65; 344-500: 1.23 |
| lake_pct | 0.26 | 0.48 | 2.82 |  |
| lake_max_mkm2 | 0.03 | 0.09 | 3.24 | 492-492: 3.24 |
| max_elev_km | 4.50 | 6.49 | 9.08 |  |
| trees_pct | 22.25 | 35.09 | 45.85 |  |
| npp | 234.20 | 309.40 | 436.50 |  |
| landmasses | 4.00 | 7.00 | 11.00 |  |
| largest_pct | 10.20 | 19.90 | 32.90 |  |

### Seed 11, L6 (run 4fdd05)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.52 | 32.99 | 33.92 |  |
| cont_pct | 38.75 | 39.49 | 40.39 |  |
| cont_km | 33.77 | 34.65 | 34.98 |  |
| plates | 7.00 | 11.00 | 12.00 |  |
| ocean_age | 44.50 | 65.40 | 82.40 |  |
| speed | 2.53 | 3.66 | 5.06 |  |
| sea_level | -223.70 | -73.70 | 194.80 |  |
| sea_ice_m | -143.30 | -65.30 | -2.10 |  |
| sea_tect_m | -132.10 | 39.80 | 197.00 |  |
| ice_pct | 0.10 | 2.50 | 5.00 |  |
| temp | 8.80 | 13.70 | 18.00 |  |
| co2 | -1.47 | -0.73 | -0.15 |  |
| dry_pct | 23.62 | 25.48 | 28.32 |  |
| inland_pct | 1.04 | 3.38 | 6.95 | 300-500: 1.04 |
| lake_pct | 0.17 | 0.41 | 1.02 | 452-456: 0.17 |
| lake_max_mkm2 | 0.03 | 0.15 | 0.95 |  |
| max_elev_km | 3.53 | 4.61 | 8.49 |  |
| trees_pct | 15.49 | 28.75 | 42.43 |  |
| npp | 221.50 | 239.20 | 331.40 |  |
| landmasses | 1.00 | 4.00 | 10.00 | 396-404: 1 |
| largest_pct | 17.50 | 33.40 | 34.20 |  |

### Seed 21, L6 (run c80e28)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.78 | 31.20 | 34.12 |  |
| cont_pct | 37.60 | 40.18 | 40.87 |  |
| cont_km | 33.05 | 33.67 | 35.84 |  |
| plates | 6.00 | 15.00 | 20.00 |  |
| ocean_age | 35.00 | 46.00 | 92.10 |  |
| speed | 2.83 | 4.02 | 5.18 |  |
| sea_level | -546.00 | 188.50 | 241.20 | 460-500: -546.00 |
| sea_ice_m | -297.80 | -27.10 | -11.00 | 488-500: -297.80 |
| sea_tect_m | -248.20 | 211.60 | 256.10 |  |
| ice_pct | 0.60 | 1.40 | 8.60 |  |
| temp | 6.90 | 12.20 | 19.80 | 440-464: 6.90 |
| co2 | -2.22 | -1.19 | -0.84 |  |
| dry_pct | 17.13 | 22.09 | 35.07 |  |
| inland_pct | 0.82 | 2.77 | 10.88 | 308-424: 0.82; 436-500: 1.38 |
| lake_pct | 0.20 | 0.43 | 2.37 |  |
| lake_max_mkm2 | 0.03 | 0.09 | 2.10 | 304-304: 2.10; 428-432: 1.25 |
| max_elev_km | 3.71 | 4.42 | 6.71 |  |
| trees_pct | 15.50 | 33.06 | 43.13 |  |
| npp | 206.50 | 317.30 | 336.80 |  |
| landmasses | 3.00 | 8.00 | 12.00 |  |
| largest_pct | 11.00 | 28.00 | 31.10 |  |

### Seed 3199, L6 (run 8698e2)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.94 | 32.00 | 33.92 |  |
| cont_pct | 38.39 | 39.44 | 39.79 |  |
| cont_km | 34.18 | 34.46 | 35.25 |  |
| plates | 9.00 | 11.00 | 14.00 |  |
| ocean_age | 50.90 | 55.60 | 66.10 |  |
| speed | 3.42 | 4.47 | 5.76 |  |
| sea_level | -73.40 | 12.00 | 95.10 |  |
| sea_ice_m | -128.10 | -45.30 | -0.70 |  |
| sea_tect_m | -54.90 | 65.10 | 139.40 |  |
| ice_pct | 0.10 | 2.20 | 4.40 |  |
| temp | 8.80 | 11.90 | 16.60 |  |
| co2 | -0.89 | -0.39 | 0.13 |  |
| dry_pct | 18.77 | 31.09 | 39.86 |  |
| inland_pct | 1.16 | 3.44 | 8.36 | 300-496: 1.16 |
| lake_pct | 0.10 | 0.24 | 1.15 | 344-348: 0.11; 400-432: 0.11; 448-456: 0.10; 468-496: 0.13 |
| lake_max_mkm2 | 0.03 | 0.05 | 0.93 |  |
| max_elev_km | 3.45 | 6.34 | 7.56 |  |
| trees_pct | 22.16 | 24.72 | 35.90 |  |
| npp | 222.60 | 314.55 | 375.40 |  |
| landmasses | 5.00 | 8.00 | 15.00 |  |
| largest_pct | 15.80 | 19.00 | 25.50 |  |

### Seed 42, L6 (run f6611e)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.12 | 31.15 | 32.85 |  |
| cont_pct | 38.58 | 39.60 | 41.14 |  |
| cont_km | 33.25 | 34.38 | 34.88 |  |
| plates | 6.00 | 10.00 | 14.00 |  |
| ocean_age | 47.60 | 53.40 | 82.40 |  |
| speed | 2.06 | 4.45 | 5.03 |  |
| sea_level | -376.70 | -26.90 | 95.10 | 460-500: -376.70 |
| sea_ice_m | -209.80 | -120.70 | -15.50 |  |
| sea_tect_m | -200.40 | 91.20 | 120.50 |  |
| ice_pct | 1.20 | 5.10 | 7.60 |  |
| temp | 3.50 | 9.80 | 17.90 | 424-492: 3.50 |
| co2 | -1.69 | -0.71 | -0.21 |  |
| dry_pct | 14.23 | 17.76 | 29.56 |  |
| inland_pct | 0.73 | 2.36 | 6.34 | 300-500: 0.73 |
| lake_pct | 0.08 | 0.39 | 0.65 | 300-300: 0.17; 312-320: 0.08 |
| lake_max_mkm2 | 0.01 | 0.07 | 0.31 |  |
| max_elev_km | 4.50 | 5.04 | 8.78 |  |
| trees_pct | 27.19 | 38.47 | 45.82 |  |
| npp | 310.20 | 345.70 | 365.90 |  |
| landmasses | 3.00 | 8.00 | 11.00 |  |
| largest_pct | 13.50 | 20.50 | 34.10 |  |

### Seed 77, L6 (run 1ad5e3)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.67 | 32.05 | 32.80 |  |
| cont_pct | 37.49 | 39.20 | 39.60 |  |
| cont_km | 34.79 | 35.21 | 36.32 |  |
| plates | 8.00 | 13.00 | 14.00 |  |
| ocean_age | 46.00 | 51.80 | 65.90 |  |
| speed | 2.74 | 4.93 | 5.63 |  |
| sea_level | -227.60 | -101.00 | 49.70 |  |
| sea_ice_m | -293.60 | -192.60 | -71.40 | 372-380: -273.80; 432-452: -293.60 |
| sea_tect_m | -28.30 | 104.50 | 134.10 |  |
| ice_pct | 2.80 | 6.30 | 9.50 |  |
| temp | 6.00 | 12.20 | 16.20 | 436-456: 6.00 |
| co2 | -1.47 | -0.41 | 0.34 |  |
| dry_pct | 21.17 | 23.75 | 40.65 |  |
| inland_pct | 1.28 | 4.40 | 15.13 | 332-340: 4.52; 352-440: 1.28; 452-500: 1.69 |
| lake_pct | 0.25 | 0.61 | 2.02 |  |
| lake_max_mkm2 | 0.03 | 0.25 | 1.92 | 320-328: 1.71; 432-432: 1.20; 444-452: 1.92 |
| max_elev_km | 3.65 | 5.39 | 8.34 |  |
| trees_pct | 18.23 | 26.52 | 36.95 |  |
| npp | 221.30 | 309.75 | 341.90 |  |
| landmasses | 2.00 | 7.00 | 10.00 | 476-476: 2; 488-496: 2 |
| largest_pct | 9.50 | 15.70 | 27.30 |  |

### Seed 505, L6 (run d267c7)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.33 | 33.01 | 34.33 |  |
| cont_pct | 39.63 | 39.91 | 40.50 |  |
| cont_km | 33.20 | 33.69 | 34.33 |  |
| plates | 7.00 | 10.00 | 12.00 |  |
| ocean_age | 42.30 | 50.60 | 77.20 |  |
| speed | 2.96 | 4.04 | 5.63 |  |
| sea_level | -141.10 | 113.60 | 172.60 |  |
| sea_ice_m | -25.60 | -2.10 | -0.00 |  |
| sea_tect_m | -133.40 | 113.60 | 174.70 |  |
| ice_pct | 0.00 | 0.20 | 1.70 |  |
| temp | 9.30 | 14.90 | 18.50 |  |
| co2 | -2.36 | -0.18 | 0.44 |  |
| dry_pct | 22.17 | 29.85 | 36.00 |  |
| inland_pct | 0.93 | 2.09 | 6.51 | 300-500: 0.93 |
| lake_pct | 0.02 | 0.15 | 0.37 | 300-300: 0.20; 312-320: 0.15; 332-332: 0.16; 348-464: 0.02; +2 more |
| lake_max_mkm2 | 0.01 | 0.04 | 0.31 |  |
| max_elev_km | 3.64 | 4.58 | 6.70 |  |
| trees_pct | 8.33 | 21.57 | 34.94 | 440-468: 8.33 |
| npp | 139.30 | 398.90 | 481.70 | 416-444: 139.30 |
| landmasses | 3.00 | 5.00 | 12.00 |  |
| largest_pct | 19.30 | 22.00 | 31.30 |  |

## Determinism

(not run)
