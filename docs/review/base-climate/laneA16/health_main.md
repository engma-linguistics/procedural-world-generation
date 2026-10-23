# Health sweep 2026-10-23 02:38

Commit 2180b8e. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 12.9 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | d25504 | 764 | 132 / 412 | 8.1 | 0 | 0.0 | 0.964 | 0.0 | 0.0 | ok | ok | 29.4 |
| 2 | 6 | 500 | 84028b | 675 | 140 / 396 | 11.6 | 0 | 3.9 | 0.971 | 0.0 | 0.0 | ok | ok | 19.6 |
| 11 | 6 | 500 | 49cae8 | 723 | 128 / 372 | 6.1 | 0 | 11.8 | 0.967 | 0.0 | 0.0 | F | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 21 | 6 | 500 | 0e375a | 690 | 136 / 404 | 13.1 | 0 | 13.7 | 0.954 | 0.0 | 0.0 | ok | ok | 21.6 |
| 3199 | 6 | 500 | 30bf88 | 665 | 132 / 376 | 8.4 | 0 | 15.7 | 0.957 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 42 | 6 | 500 | 17709d | 755 | 116 / 404 | 10.0 | 0 | 9.8 | 0.974 | 47.1 | 0.0 | ok | F: icehouse 100% of the time, outside 5-70% | 100.0 |
| 77 | 6 | 500 | d4bc0d | 749 | 124 / 416 | 14.3 | 0 | 15.7 | 0.952 | 37.3 | 23.5 | F | ok | 43.1 |
| 505 | 6 | 500 | 1b37ba | 682 | 132 / 416 | 5.2 | 0 | 9.8 | 0.959 | 0.0 | 0.0 | ok | ok | 9.8 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 34.2 | 40.9 | 33.0 | 11.0 | 59.9 | 4.3 | 16.4 | -13.0 | 30.6 | 1.0 | 16.7 | 0.5 | 20.7 | 4.3 | 0.6 | 0.1 | 5.1 | 31.8 | 314.2 | 7.0 | 21.2 |
| 2 | 6 | 34.2 | 40.4 | 33.6 | 11.0 | 54.1 | 4.2 | 81.5 | -7.4 | 89.6 | 0.5 | 18.0 | 1.2 | 20.1 | 3.6 | 0.4 | 0.1 | 4.1 | 42.6 | 321.8 | 7.0 | 18.0 |
| 11 | 6 | 34.3 | 41.0 | 33.5 | 9.0 | 66.7 | 4.1 | -41.7 | -8.2 | -34.8 | 0.7 | 14.6 | -0.3 | 22.0 | 4.1 | 0.4 | 0.1 | 6.4 | 33.1 | 255.6 | 8.0 | 20.2 |
| 21 | 6 | 32.6 | 40.3 | 33.4 | 16.0 | 45.7 | 4.5 | 170.1 | -4.6 | 173.2 | 0.4 | 15.4 | -0.3 | 24.0 | 3.1 | 0.4 | 0.1 | 5.3 | 28.0 | 320.6 | 10.0 | 16.7 |
| 3199 | 6 | 33.5 | 40.3 | 33.4 | 14.0 | 45.9 | 4.8 | 157.7 | -0.5 | 161.8 | 0.0 | 14.9 | 0.3 | 25.9 | 5.3 | 0.4 | 0.1 | 3.4 | 29.6 | 330.6 | 8.0 | 16.2 |
| 42 | 6 | 33.4 | 40.1 | 33.8 | 10.0 | 65.0 | 4.2 | -220.9 | -130.5 | -50.6 | 4.7 | 12.8 | 0.0 | 23.2 | 4.2 | 0.4 | 0.1 | 5.8 | 34.2 | 389.1 | 9.0 | 25.3 |
| 77 | 6 | 33.4 | 40.8 | 33.2 | 8.0 | 93.2 | 3.8 | -284.0 | -16.9 | -283.2 | 0.9 | 15.4 | 0.1 | 31.2 | 6.2 | 0.6 | 0.1 | 5.3 | 30.8 | 332.6 | 6.0 | 21.9 |
| 505 | 6 | 33.6 | 40.6 | 33.4 | 11.0 | 57.5 | 4.6 | 41.3 | -6.7 | 50.3 | 0.5 | 15.9 | 0.0 | 28.5 | 4.5 | 0.4 | 0.1 | 4.9 | 27.8 | 322.8 | 7.0 | 20.2 |

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
| CO2 index (ln of the CO2 stock against the reference balance) (`co2`) | -6.0 | 6.0 | 0.00 | where the forcing levels off in earth.py (+-CO2_MAX = 6 e-folds); Earth 0 |
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

## Top outliers (of 80 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 77 | 6 | low_plates | run | - | 23.50 | -..2 | 10.75 |
| 42 | 6 | sea_ice_below_150 | run | - | 47.10 | -..10 | 3.71 |
| 77 | 6 | sea_ice_below_150 | run | - | 37.30 | -..10 | 2.73 |
| 3199 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 77 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 21 | 6 | giant_lake_frames | run | - | 13.70 | -..5 | 1.74 |
| 11 | 6 | giant_lake_frames | run | - | 11.80 | -..5 | 1.36 |
| 42 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 505 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 11 | 6 | lake_max_mkm2 | 496-500 | 2 | 5.23 | -..1.0 | 0.913 |
| 42 | 6 | lake_max_mkm2 | 408-412 | 2 | 5.23 | -..1.0 | 0.913 |
| 42 | 6 | lake_max_mkm2 | 432-440 | 3 | 4.84 | -..1.0 | 0.86 |
| 3199 | 6 | lake_max_mkm2 | 300-308 | 2 | 4.30 | -..1.0 | 0.712 |
| 505 | 6 | lake_max_mkm2 | 464-464 | 1 | 4.01 | -..1.0 | 0.626 |
| 21 | 6 | lake_max_mkm2 | 436-464 | 6 | 3.21 | -..1.0 | 0.548 |
| 77 | 6 | sea_level | 300-404 | 27 | -834.90 | -250..300 | 0.441 |
| 505 | 6 | lake_max_mkm2 | 496-496 | 1 | 2.98 | -..1.0 | 0.411 |
| 505 | 6 | lake_max_mkm2 | 300-304 | 2 | 2.89 | -..1.0 | 0.408 |
| 77 | 6 | lake_max_mkm2 | 312-348 | 8 | 2.25 | -..1.0 | 0.33 |
| 77 | 6 | sea_ice_m | 300-368 | 18 | -482.20 | -250..- | 0.318 |
| 77 | 6 | inland_pct | 308-496 | 42 | 42.57 | 8..30 | 0.305 |
| 3199 | 6 | lake_max_mkm2 | 436-444 | 3 | 2.33 | -..1.0 | 0.297 |
| 11 | 6 | lake_pct | 496-500 | 2 | 5.66 | 0.2..3.0 | 0.205 |
| 2 | 6 | inland_pct | 304-480 | 45 | 0.88 | 8..30 | 0.18 |
| 11 | 6 | inland_pct | 300-492 | 45 | 1.05 | 8..30 | 0.176 |
| 11 | 6 | lake_max_mkm2 | 480-480 | 1 | 1.81 | -..1.0 | 0.168 |
| 3199 | 6 | lake_max_mkm2 | 368-372 | 2 | 1.73 | -..1.0 | 0.158 |
| 505 | 6 | inland_pct | 312-500 | 44 | 1.80 | 8..30 | 0.155 |
| 1 | 6 | inland_pct | 300-432 | 34 | 1.35 | 8..30 | 0.142 |
| 21 | 6 | inland_pct | 308-444 | 33 | 1.29 | 8..30 | 0.141 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run d25504)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.66 | 34.23 | 34.91 |  |
| cont_pct | 39.32 | 40.88 | 42.48 |  |
| cont_km | 32.33 | 33.02 | 34.85 |  |
| plates | 9.00 | 11.00 | 13.00 |  |
| ocean_age | 46.70 | 59.90 | 69.50 |  |
| speed | 2.79 | 4.26 | 5.25 |  |
| sea_level | -131.70 | 16.40 | 106.90 |  |
| sea_ice_m | -81.50 | -13.00 | -1.80 |  |
| sea_tect_m | -50.20 | 30.60 | 119.30 |  |
| ice_pct | 0.10 | 1.00 | 4.90 |  |
| temp | 13.00 | 16.70 | 21.10 |  |
| co2 | -0.42 | 0.52 | 1.72 |  |
| dry_pct | 17.51 | 20.71 | 31.40 |  |
| inland_pct | 1.35 | 4.32 | 10.27 | 300-432: 1.35; 460-500: 2.87 |
| lake_pct | 0.17 | 0.58 | 1.47 | 372-372: 0.17 |
| lake_max_mkm2 | 0.03 | 0.14 | 0.56 |  |
| max_elev_km | 4.16 | 5.13 | 7.84 |  |
| trees_pct | 22.25 | 31.80 | 39.48 |  |
| npp | 209.10 | 314.20 | 355.10 |  |
| landmasses | 4.00 | 7.00 | 15.00 |  |
| largest_pct | 13.60 | 21.20 | 34.80 |  |

### Seed 2, L6 (run 84028b)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.38 | 34.17 | 34.51 |  |
| cont_pct | 39.26 | 40.37 | 41.37 |  |
| cont_km | 32.86 | 33.62 | 34.27 |  |
| plates | 9.00 | 11.00 | 14.00 |  |
| ocean_age | 45.60 | 54.10 | 64.20 |  |
| speed | 3.22 | 4.20 | 5.02 |  |
| sea_level | -9.80 | 81.50 | 160.40 |  |
| sea_ice_m | -56.30 | -7.40 | -1.90 |  |
| sea_tect_m | 11.50 | 89.60 | 163.50 |  |
| ice_pct | 0.10 | 0.50 | 2.70 |  |
| temp | 10.60 | 18.00 | 22.20 |  |
| co2 | 0.38 | 1.25 | 2.40 |  |
| dry_pct | 14.23 | 20.06 | 33.19 |  |
| inland_pct | 0.88 | 3.58 | 11.53 | 304-480: 0.88; 492-496: 5.11 |
| lake_pct | 0.24 | 0.43 | 1.52 |  |
| lake_max_mkm2 | 0.03 | 0.07 | 1.40 | 300-300: 1.06; 500-500: 1.40 |
| max_elev_km | 3.03 | 4.11 | 6.95 |  |
| trees_pct | 22.70 | 42.63 | 51.74 | 388-412: 51.74 |
| npp | 253.40 | 321.80 | 360.40 |  |
| landmasses | 5.00 | 7.00 | 13.00 |  |
| largest_pct | 15.60 | 18.00 | 34.20 |  |

### Seed 11, L6 (run 49cae8)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.60 | 34.34 | 34.79 |  |
| cont_pct | 39.74 | 40.97 | 41.64 |  |
| cont_km | 32.83 | 33.49 | 34.26 |  |
| plates | 7.00 | 9.00 | 11.00 |  |
| ocean_age | 54.00 | 66.70 | 75.40 |  |
| speed | 2.41 | 4.06 | 5.21 |  |
| sea_level | -153.60 | -41.70 | 25.90 |  |
| sea_ice_m | -16.10 | -8.20 | -2.40 |  |
| sea_tect_m | -137.80 | -34.80 | 28.70 |  |
| ice_pct | 0.20 | 0.70 | 1.20 |  |
| temp | 12.60 | 14.60 | 18.70 |  |
| co2 | -1.83 | -0.34 | 0.83 |  |
| dry_pct | 17.20 | 21.98 | 37.74 |  |
| inland_pct | 1.05 | 4.10 | 16.16 | 300-492: 1.05 |
| lake_pct | 0.11 | 0.44 | 5.66 | 448-448: 0.18; 460-460: 0.11; 496-500: 5.66 |
| lake_max_mkm2 | 0.03 | 0.10 | 5.23 | 300-304: 1.62; 344-344: 1.12; 480-480: 1.81; 496-500: 5.23 |
| max_elev_km | 4.37 | 6.36 | 7.90 |  |
| trees_pct | 17.14 | 33.07 | 45.99 |  |
| npp | 209.20 | 255.60 | 330.30 |  |
| landmasses | 3.00 | 8.00 | 12.00 |  |
| largest_pct | 10.20 | 20.20 | 29.70 |  |

### Seed 21, L6 (run 0e375a)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.62 | 32.58 | 33.16 |  |
| cont_pct | 38.89 | 40.34 | 41.24 |  |
| cont_km | 32.66 | 33.39 | 34.73 |  |
| plates | 10.00 | 16.00 | 19.00 |  |
| ocean_age | 40.40 | 45.70 | 69.80 |  |
| speed | 2.69 | 4.54 | 5.12 |  |
| sea_level | -120.80 | 170.10 | 227.20 |  |
| sea_ice_m | -38.30 | -4.60 | -0.00 |  |
| sea_tect_m | -87.20 | 173.20 | 227.80 |  |
| ice_pct | 0.00 | 0.40 | 2.40 |  |
| temp | 11.70 | 15.40 | 24.80 |  |
| co2 | -1.00 | -0.25 | 1.13 |  |
| dry_pct | 13.43 | 24.02 | 38.64 |  |
| inland_pct | 0.74 | 3.11 | 11.93 | 308-444: 1.29; 456-500: 0.74 |
| lake_pct | 0.14 | 0.41 | 2.53 | 352-352: 0.14; 388-388: 0.17; 416-416: 0.19 |
| lake_max_mkm2 | 0.03 | 0.09 | 3.21 | 320-320: 1.49; 436-464: 3.21 |
| max_elev_km | 3.81 | 5.35 | 8.29 |  |
| trees_pct | 11.85 | 28.00 | 39.86 |  |
| npp | 211.40 | 320.60 | 351.40 |  |
| landmasses | 5.00 | 10.00 | 16.00 |  |
| largest_pct | 12.40 | 16.70 | 30.20 |  |

### Seed 3199, L6 (run 30bf88)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.84 | 33.53 | 33.90 |  |
| cont_pct | 39.54 | 40.29 | 41.07 |  |
| cont_km | 32.87 | 33.36 | 34.10 |  |
| plates | 11.00 | 14.00 | 16.00 |  |
| ocean_age | 42.30 | 45.90 | 57.50 |  |
| speed | 3.48 | 4.78 | 5.84 |  |
| sea_level | 68.80 | 157.70 | 198.70 |  |
| sea_ice_m | -14.60 | -0.50 | -0.00 |  |
| sea_tect_m | 83.30 | 161.80 | 198.70 |  |
| ice_pct | 0.00 | 0.00 | 1.40 |  |
| temp | 11.80 | 14.90 | 20.20 |  |
| co2 | -0.09 | 0.34 | 1.03 |  |
| dry_pct | 14.30 | 25.94 | 38.91 |  |
| inland_pct | 1.20 | 5.28 | 15.89 | 304-320: 3.67; 332-348: 4.88; 364-364: 7.25; 384-500: 1.20 |
| lake_pct | 0.17 | 0.39 | 3.04 | 300-300: 3.04; 404-428: 0.17 |
| lake_max_mkm2 | 0.03 | 0.11 | 4.30 | 300-308: 4.30; 356-356: 1.36; 368-372: 1.73; 436-444: 2.33 |
| max_elev_km | 2.53 | 3.43 | 7.36 |  |
| trees_pct | 24.73 | 29.55 | 39.01 |  |
| npp | 259.10 | 330.60 | 360.30 |  |
| landmasses | 3.00 | 8.00 | 12.00 |  |
| largest_pct | 12.30 | 16.20 | 29.90 |  |

### Seed 42, L6 (run 17709d)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.53 | 33.43 | 33.98 |  |
| cont_pct | 38.39 | 40.14 | 41.02 |  |
| cont_km | 33.32 | 33.84 | 35.72 |  |
| plates | 6.00 | 10.00 | 13.00 |  |
| ocean_age | 54.50 | 65.00 | 80.50 |  |
| speed | 2.74 | 4.16 | 5.42 |  |
| sea_level | -286.90 | -220.90 | -95.50 | 316-340: -286.90; 440-464: -272.80 |
| sea_ice_m | -217.80 | -130.50 | -24.80 |  |
| sea_tect_m | -208.40 | -50.60 | 1.70 |  |
| ice_pct | 2.00 | 4.70 | 7.00 |  |
| temp | 8.50 | 12.80 | 18.50 |  |
| co2 | -0.87 | 0.01 | 0.96 |  |
| dry_pct | 17.94 | 23.22 | 33.81 |  |
| inland_pct | 1.22 | 4.15 | 13.53 | 300-304: 5.47; 320-404: 2.45; 416-428: 2.87; 444-500: 1.22 |
| lake_pct | 0.18 | 0.39 | 3.53 | 384-384: 0.20; 408-412: 3.53; 432-436: 3.35; 452-452: 0.18 |
| lake_max_mkm2 | 0.03 | 0.07 | 5.23 | 408-412: 5.23; 432-440: 4.84 |
| max_elev_km | 4.06 | 5.85 | 8.52 |  |
| trees_pct | 22.76 | 34.19 | 44.54 |  |
| npp | 292.80 | 389.10 | 437.50 |  |
| landmasses | 3.00 | 9.00 | 14.00 |  |
| largest_pct | 15.10 | 25.30 | 33.60 |  |

### Seed 77, L6 (run d4bc0d)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.34 | 33.43 | 35.93 |  |
| cont_pct | 39.61 | 40.84 | 42.06 |  |
| cont_km | 32.01 | 33.17 | 33.87 |  |
| plates | 3.00 | 8.00 | 12.00 | 300-344: 3 |
| ocean_age | 40.90 | 93.20 | 142.30 | 308-384: 142.30 |
| speed | 1.77 | 3.75 | 6.26 | 300-316: 1.77 |
| sea_level | -834.90 | -284.00 | 153.30 | 300-404: -834.90 |
| sea_ice_m | -482.20 | -16.90 | -0.00 | 300-368: -482.20 |
| sea_tect_m | -365.90 | -283.20 | 172.50 | 300-404: -365.90 |
| ice_pct | 0.00 | 0.90 | 12.10 | 300-336: 12.10 |
| temp | 7.30 | 15.40 | 21.60 | 300-308: 7.30 |
| co2 | -1.31 | 0.13 | 1.26 |  |
| dry_pct | 18.75 | 31.22 | 36.63 |  |
| inland_pct | 0.96 | 6.17 | 42.57 | 308-496: 42.57 |
| lake_pct | 0.30 | 0.56 | 2.58 |  |
| lake_max_mkm2 | 0.04 | 0.15 | 2.25 | 312-348: 2.25 |
| max_elev_km | 3.76 | 5.33 | 8.26 |  |
| trees_pct | 19.01 | 30.78 | 36.65 |  |
| npp | 285.10 | 332.60 | 371.40 |  |
| landmasses | 2.00 | 6.00 | 14.00 | 360-360: 2 |
| largest_pct | 14.30 | 21.90 | 36.50 | 300-364: 36.50 |

### Seed 505, L6 (run 1b37ba)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.88 | 33.59 | 35.35 |  |
| cont_pct | 39.46 | 40.60 | 41.67 |  |
| cont_km | 32.59 | 33.39 | 34.87 |  |
| plates | 9.00 | 11.00 | 15.00 |  |
| ocean_age | 45.90 | 57.50 | 64.40 |  |
| speed | 2.86 | 4.58 | 4.99 |  |
| sea_level | -38.20 | 41.30 | 157.30 |  |
| sea_ice_m | -36.70 | -6.70 | -0.40 |  |
| sea_tect_m | -7.40 | 50.30 | 158.30 |  |
| ice_pct | 0.00 | 0.50 | 2.70 |  |
| temp | 13.50 | 15.90 | 18.70 |  |
| co2 | -1.13 | 0.03 | 0.76 |  |
| dry_pct | 20.05 | 28.54 | 34.72 |  |
| inland_pct | 1.80 | 4.52 | 14.48 | 300-300: 6.36; 312-500: 1.80 |
| lake_pct | 0.12 | 0.37 | 3.34 | 352-356: 0.15; 376-376: 0.12; 404-408: 0.12; 420-428: 0.17; +1 more |
| lake_max_mkm2 | 0.03 | 0.07 | 4.01 | 300-304: 2.89; 464-464: 4.01; 476-476: 1.15; 496-496: 2.98 |
| max_elev_km | 3.11 | 4.93 | 8.40 |  |
| trees_pct | 20.75 | 27.82 | 36.41 |  |
| npp | 172.20 | 322.75 | 359.30 | 416-432: 172.20; 444-444: 198.90 |
| landmasses | 3.00 | 7.00 | 16.00 |  |
| largest_pct | 8.60 | 20.20 | 35.20 | 300-300: 35.20 |

## Determinism

Seed 1 L6 re-run to 100 Myr (run c6131e) against the sweep's run d25504: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
