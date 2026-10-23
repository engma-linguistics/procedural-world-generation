# Health sweep 2026-10-23 00:47

Commit d32f7fa. 8 runs (default params, `--every 4`) at 4 workers x 2 numba threads; simulations 19.3 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | 84f2e0 | 685 | 132 / 412 | 10.8 | 0 | 0.0 | 0.969 | 9.8 | 0.0 | ok | ok | 66.7 |
| 2 | 6 | 500 | c8d4ae | 640 | 140 / 396 | 15.8 | 0 | 3.9 | 0.959 | 15.7 | 0.0 | F | F: icehouse 73% of the time, outside 5-70% | 72.5 |
| 11 | 6 | 500 | 6d90b1 | 582 | 128 / 372 | 10.6 | 0 | 2.0 | 0.943 | 0.0 | 0.0 | F | F: icehouse 2% of the time, outside 5-70% | 2.0 |
| 21 | 6 | 500 | d914da | 579 | 136 / 404 | 10.5 | 0 | 9.8 | 0.963 | 0.0 | 0.0 | ok | ok | 43.1 |
| 3199 | 6 | 500 | 697aa5 | 430 | 132 / 376 | 7.7 | 0 | 7.8 | 0.976 | 0.0 | 0.0 | ok | ok | 51.0 |
| 42 | 6 | 500 | d73833 | 491 | 116 / 404 | 10.2 | 0 | 5.9 | 0.961 | 25.5 | 0.0 | ok | F: icehouse 84% of the time, outside 5-70% | 84.3 |
| 77 | 6 | 500 | 11cc85 | 459 | 124 / 416 | 13.1 | 0 | 0.0 | 0.97 | 0.0 | 0.0 | ok | F: icehouse 82% of the time, outside 5-70% | 82.4 |
| 505 | 6 | 500 | 22c289 | 471 | 132 / 416 | 6.9 | 0 | 2.0 | 0.99 | 0.0 | 0.0 | ok | F: icehouse 90% of the time, outside 5-70% | 90.2 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 30.8 | 39.1 | 34.5 | 14.0 | 51.6 | 4.7 | 96.4 | -31.1 | 136.9 | 2.1 | 15.1 | 0.0 | 22.7 | 2.6 | 0.4 | 0.1 | 6.8 | 37.8 | 320.1 | 8.0 | 16.6 |
| 2 | 6 | 33.0 | 39.8 | 33.7 | 8.0 | 67.7 | 3.3 | -70.3 | -23.9 | -48.5 | 2.3 | 13.6 | 0.1 | 13.3 | 2.6 | 0.4 | 0.1 | 5.5 | 39.5 | 288.6 | 10.0 | 23.3 |
| 11 | 6 | 32.0 | 40.0 | 33.3 | 13.0 | 52.8 | 4.7 | 82.1 | -6.1 | 91.7 | 0.5 | 14.0 | -1.0 | 27.9 | 3.7 | 0.3 | 0.1 | 6.8 | 23.9 | 340.5 | 7.0 | 26.9 |
| 21 | 6 | 33.0 | 39.7 | 34.3 | 14.0 | 49.3 | 4.4 | 138.1 | -14.1 | 149.6 | 1.1 | 14.2 | -0.7 | 28.0 | 3.5 | 0.3 | 0.1 | 5.3 | 27.8 | 294.1 | 7.0 | 28.4 |
| 3199 | 6 | 32.3 | 39.6 | 34.6 | 11.0 | 60.5 | 4.4 | -27.6 | -21.2 | -6.4 | 2.0 | 12.7 | -0.4 | 26.6 | 3.0 | 0.4 | 0.1 | 6.8 | 28.9 | 306.9 | 8.0 | 16.5 |
| 42 | 6 | 31.6 | 40.5 | 33.6 | 13.0 | 51.7 | 4.7 | -95.7 | -93.2 | 88.1 | 3.9 | 12.6 | 0.1 | 21.6 | 2.7 | 0.4 | 0.1 | 5.0 | 34.5 | 360.3 | 6.0 | 26.5 |
| 77 | 6 | 31.5 | 39.4 | 34.5 | 11.0 | 58.1 | 5.5 | 11.5 | -43.2 | 79.6 | 2.7 | 14.1 | 0.3 | 28.4 | 4.5 | 0.5 | 0.1 | 5.2 | 30.7 | 330.6 | 7.0 | 17.4 |
| 505 | 6 | 32.6 | 39.0 | 34.9 | 10.0 | 56.1 | 4.2 | 7.4 | -31.3 | 44.3 | 2.1 | 13.0 | -0.6 | 23.3 | 3.9 | 0.5 | 0.1 | 5.0 | 28.4 | 324.6 | 7.0 | 26.3 |

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

## Top outliers (of 54 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 42 | 6 | sea_ice_below_150 | run | - | 25.50 | -..10 | 1.55 |
| 505 | 6 | lake_max_mkm2 | 492-492 | 1 | 6.45 | -..1.0 | 1.133 |
| 21 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 2 | 6 | sea_ice_below_150 | run | - | 15.70 | -..10 | 0.57 |
| 3199 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 3199 | 6 | lake_max_mkm2 | 472-480 | 3 | 3.29 | -..1.0 | 0.512 |
| 2 | 6 | sea_ice_m | 476-500 | 7 | -714.40 | -250..- | 0.475 |
| 2 | 6 | sea_level | 464-500 | 10 | -960.40 | -250..300 | 0.361 |
| 2 | 6 | ice_pct | 476-500 | 7 | 19.40 | -..10 | 0.24 |
| 2 | 6 | inland_pct | 300-500 | 51 | 0.19 | 8..30 | 0.215 |
| 42 | 6 | inland_pct | 300-500 | 51 | 0.51 | 8..30 | 0.206 |
| 1 | 6 | inland_pct | 300-500 | 51 | 0.81 | 8..30 | 0.198 |
| 505 | 6 | lake_pct | 492-492 | 1 | 5.66 | 0.2..3.0 | 0.198 |
| 21 | 6 | inland_pct | 300-496 | 50 | 1.01 | 8..30 | 0.19 |
| 3199 | 6 | inland_pct | 300-500 | 50 | 1.11 | 8..30 | 0.187 |
| 3199 | 6 | lake_max_mkm2 | 408-408 | 1 | 1.88 | -..1.0 | 0.183 |
| 11 | 6 | inland_pct | 300-500 | 51 | 1.44 | 8..30 | 0.18 |
| 42 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 505 | 6 | inland_pct | 320-488 | 41 | 1.14 | 8..30 | 0.164 |
| 2 | 6 | lake_max_mkm2 | 464-468 | 2 | 1.66 | -..1.0 | 0.142 |
| 21 | 6 | lake_max_mkm2 | 472-488 | 5 | 1.57 | -..1.0 | 0.136 |
| 77 | 6 | inland_pct | 380-500 | 30 | 1.25 | 8..30 | 0.134 |
| 42 | 6 | lake_max_mkm2 | 440-444 | 2 | 1.34 | -..1.0 | 0.074 |
| 77 | 6 | sea_level | 300-336 | 10 | -381.10 | -250..300 | 0.067 |
| 2 | 6 | temp | 480-500 | 6 | 3.10 | 8..30 | 0.055 |
| 11 | 6 | lake_max_mkm2 | 392-392 | 1 | 1.25 | -..1.0 | 0.051 |
| 77 | 6 | inland_pct | 356-364 | 3 | 5.42 | 8..30 | 0.026 |
| 505 | 6 | inland_pct | 300-300 | 1 | 5.97 | 8..30 | 0.019 |
| 2 | 6 | dry_pct | 480-500 | 6 | 10.15 | 12..45 | 0.014 |
| 77 | 6 | inland_pct | 304-304 | 1 | 6.79 | 8..30 | 0.011 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run 84f2e0)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.64 | 30.79 | 31.80 |  |
| cont_pct | 38.33 | 39.13 | 40.10 |  |
| cont_km | 33.96 | 34.48 | 35.37 |  |
| plates | 11.00 | 14.00 | 17.00 |  |
| ocean_age | 40.20 | 51.60 | 69.00 |  |
| speed | 3.89 | 4.69 | 5.04 |  |
| sea_level | -94.60 | 96.40 | 190.50 |  |
| sea_ice_m | -178.50 | -31.10 | -10.00 |  |
| sea_tect_m | -2.70 | 136.90 | 210.30 |  |
| ice_pct | 0.80 | 2.10 | 8.40 |  |
| temp | 8.30 | 15.10 | 19.10 |  |
| co2 | -0.69 | 0.01 | 0.45 |  |
| dry_pct | 13.42 | 22.70 | 25.99 |  |
| inland_pct | 0.81 | 2.60 | 5.03 | 300-500: 0.81 |
| lake_pct | 0.14 | 0.39 | 0.89 | 452-452: 0.14 |
| lake_max_mkm2 | 0.03 | 0.10 | 0.80 |  |
| max_elev_km | 4.59 | 6.84 | 8.33 |  |
| trees_pct | 20.15 | 37.84 | 44.53 |  |
| npp | 219.00 | 320.10 | 384.40 |  |
| landmasses | 6.00 | 8.00 | 13.00 |  |
| largest_pct | 9.30 | 16.60 | 24.70 |  |

### Seed 2, L6 (run c8d4ae)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.40 | 32.95 | 34.85 |  |
| cont_pct | 38.92 | 39.79 | 40.93 |  |
| cont_km | 33.01 | 33.73 | 34.93 |  |
| plates | 6.00 | 8.00 | 11.00 |  |
| ocean_age | 59.20 | 67.70 | 95.50 |  |
| speed | 2.13 | 3.30 | 4.36 |  |
| sea_level | -960.40 | -70.30 | 47.50 | 464-500: -960.40 |
| sea_ice_m | -714.40 | -23.90 | -11.50 | 476-500: -714.40 |
| sea_tect_m | -255.80 | -48.50 | 59.70 | 496-500: -255.80 |
| ice_pct | 0.80 | 2.30 | 19.40 | 476-500: 19.40 |
| temp | 3.10 | 13.60 | 18.90 | 480-500: 3.10 |
| co2 | -0.97 | 0.14 | 0.65 |  |
| dry_pct | 10.15 | 13.33 | 31.83 | 480-500: 10.15 |
| inland_pct | 0.19 | 2.57 | 7.25 | 300-500: 0.19 |
| lake_pct | 0.24 | 0.40 | 3.01 | 464-464: 3.01 |
| lake_max_mkm2 | 0.03 | 0.07 | 1.66 | 464-468: 1.66 |
| max_elev_km | 3.84 | 5.45 | 8.33 |  |
| trees_pct | 24.46 | 39.54 | 45.32 |  |
| npp | 210.10 | 288.60 | 456.20 |  |
| landmasses | 5.00 | 10.00 | 13.00 |  |
| largest_pct | 10.40 | 23.30 | 32.70 |  |

### Seed 11, L6 (run 6d90b1)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.57 | 31.96 | 32.66 |  |
| cont_pct | 38.94 | 40.05 | 40.75 |  |
| cont_km | 33.19 | 33.34 | 33.89 |  |
| plates | 11.00 | 13.00 | 15.00 |  |
| ocean_age | 42.90 | 52.80 | 60.90 |  |
| speed | 4.02 | 4.66 | 5.31 |  |
| sea_level | -79.60 | 82.10 | 184.00 |  |
| sea_ice_m | -128.70 | -6.10 | -0.10 |  |
| sea_tect_m | 28.30 | 91.70 | 185.30 |  |
| ice_pct | 0.00 | 0.50 | 3.80 |  |
| temp | 8.60 | 14.00 | 19.20 |  |
| co2 | -1.51 | -0.95 | -0.41 |  |
| dry_pct | 20.28 | 27.86 | 34.03 |  |
| inland_pct | 1.44 | 3.70 | 7.01 | 300-500: 1.44 |
| lake_pct | 0.14 | 0.33 | 1.22 | 328-344: 0.14; 360-368: 0.18; 428-428: 0.17 |
| lake_max_mkm2 | 0.03 | 0.06 | 1.25 | 392-392: 1.25 |
| max_elev_km | 3.53 | 6.77 | 8.22 |  |
| trees_pct | 12.39 | 23.91 | 38.41 |  |
| npp | 209.00 | 340.50 | 421.40 |  |
| landmasses | 2.00 | 7.00 | 12.00 | 396-400: 2 |
| largest_pct | 12.80 | 26.90 | 32.50 |  |

### Seed 21, L6 (run d914da)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.22 | 33.04 | 33.84 |  |
| cont_pct | 38.99 | 39.74 | 40.63 |  |
| cont_km | 33.72 | 34.27 | 34.67 |  |
| plates | 10.00 | 14.00 | 16.00 |  |
| ocean_age | 37.70 | 49.30 | 76.00 |  |
| speed | 2.81 | 4.37 | 5.42 |  |
| sea_level | -190.70 | 138.10 | 210.40 |  |
| sea_ice_m | -106.30 | -14.10 | -2.70 |  |
| sea_tect_m | -112.60 | 149.60 | 217.30 |  |
| ice_pct | 0.20 | 1.10 | 4.40 |  |
| temp | 10.20 | 14.20 | 20.70 |  |
| co2 | -1.18 | -0.68 | -0.31 |  |
| dry_pct | 20.80 | 28.00 | 30.63 |  |
| inland_pct | 1.01 | 3.54 | 9.84 | 300-496: 1.01 |
| lake_pct | 0.08 | 0.29 | 1.63 | 300-312: 0.13; 328-344: 0.13; 360-360: 0.14; 372-396: 0.08 |
| lake_max_mkm2 | 0.03 | 0.10 | 1.57 | 472-488: 1.57 |
| max_elev_km | 3.33 | 5.28 | 8.21 |  |
| trees_pct | 11.76 | 27.77 | 37.50 |  |
| npp | 196.50 | 294.10 | 318.10 | 424-424: 196.50 |
| landmasses | 4.00 | 7.00 | 12.00 |  |
| largest_pct | 14.00 | 28.40 | 33.40 |  |

### Seed 3199, L6 (run 697aa5)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.80 | 32.30 | 33.14 |  |
| cont_pct | 38.38 | 39.60 | 40.75 |  |
| cont_km | 33.69 | 34.57 | 35.37 |  |
| plates | 9.00 | 11.00 | 15.00 |  |
| ocean_age | 46.60 | 60.50 | 72.80 |  |
| speed | 3.73 | 4.43 | 5.70 |  |
| sea_level | -208.80 | -27.60 | 133.20 |  |
| sea_ice_m | -110.20 | -21.20 | -5.70 |  |
| sea_tect_m | -100.00 | -6.40 | 139.20 |  |
| ice_pct | 0.60 | 2.00 | 5.10 |  |
| temp | 8.50 | 12.70 | 16.20 |  |
| co2 | -1.11 | -0.37 | 0.60 |  |
| dry_pct | 10.98 | 26.57 | 30.52 | 500-500: 10.98 |
| inland_pct | 1.11 | 2.95 | 9.13 | 300-500: 1.11 |
| lake_pct | 0.20 | 0.40 | 2.88 | 380-384: 0.20 |
| lake_max_mkm2 | 0.03 | 0.09 | 3.29 | 408-408: 1.88; 472-480: 3.29 |
| max_elev_km | 5.32 | 6.78 | 7.71 |  |
| trees_pct | 26.12 | 28.85 | 37.07 |  |
| npp | 236.30 | 306.85 | 370.20 |  |
| landmasses | 5.00 | 8.00 | 15.00 |  |
| largest_pct | 15.20 | 16.50 | 27.80 |  |

### Seed 42, L6 (run d73833)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.51 | 31.58 | 34.45 |  |
| cont_pct | 39.08 | 40.45 | 40.94 |  |
| cont_km | 33.26 | 33.65 | 34.81 |  |
| plates | 10.00 | 13.00 | 16.00 |  |
| ocean_age | 47.80 | 51.70 | 74.90 |  |
| speed | 3.39 | 4.70 | 6.08 |  |
| sea_level | -151.20 | -95.70 | 12.50 |  |
| sea_ice_m | -219.00 | -93.20 | -5.70 |  |
| sea_tect_m | -141.40 | 88.10 | 110.30 |  |
| ice_pct | 0.40 | 3.90 | 8.00 |  |
| temp | 7.80 | 12.60 | 18.00 | 452-452: 7.80 |
| co2 | -1.13 | 0.05 | 0.44 |  |
| dry_pct | 19.36 | 21.60 | 27.46 |  |
| inland_pct | 0.51 | 2.66 | 7.13 | 300-500: 0.51 |
| lake_pct | 0.20 | 0.38 | 1.24 | 308-308: 0.20 |
| lake_max_mkm2 | 0.03 | 0.10 | 1.34 | 336-336: 1.02; 440-444: 1.34 |
| max_elev_km | 3.85 | 4.96 | 7.45 |  |
| trees_pct | 22.12 | 34.54 | 41.22 |  |
| npp | 259.60 | 360.30 | 384.40 |  |
| landmasses | 1.00 | 6.00 | 11.00 | 300-316: 1 |
| largest_pct | 14.70 | 26.50 | 34.40 |  |

### Seed 77, L6 (run 11cc85)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.80 | 31.47 | 32.52 |  |
| cont_pct | 37.72 | 39.37 | 40.57 |  |
| cont_km | 33.71 | 34.49 | 36.15 |  |
| plates | 8.00 | 11.00 | 14.00 |  |
| ocean_age | 52.50 | 58.10 | 96.00 |  |
| speed | 2.89 | 5.48 | 6.11 |  |
| sea_level | -381.10 | 11.50 | 95.50 | 300-336: -381.10 |
| sea_ice_m | -120.90 | -43.20 | -7.30 |  |
| sea_tect_m | -268.70 | 79.60 | 104.10 | 300-308: -268.70 |
| ice_pct | 0.70 | 2.70 | 5.70 |  |
| temp | 7.40 | 14.10 | 20.50 | 300-308: 7.40 |
| co2 | -1.96 | 0.32 | 0.88 |  |
| dry_pct | 15.56 | 28.37 | 38.77 |  |
| inland_pct | 1.25 | 4.49 | 16.48 | 304-304: 6.79; 344-344: 7.96; 356-364: 5.42; 380-500: 1.25 |
| lake_pct | 0.22 | 0.49 | 1.15 |  |
| lake_max_mkm2 | 0.03 | 0.14 | 0.77 |  |
| max_elev_km | 3.83 | 5.17 | 7.99 |  |
| trees_pct | 17.18 | 30.70 | 43.98 |  |
| npp | 286.60 | 330.60 | 344.40 |  |
| landmasses | 2.00 | 7.00 | 15.00 | 300-308: 2; 492-496: 2 |
| largest_pct | 12.50 | 17.40 | 33.40 |  |

### Seed 505, L6 (run 22c289)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.63 | 32.56 | 34.28 |  |
| cont_pct | 38.53 | 39.03 | 40.39 |  |
| cont_km | 34.32 | 34.93 | 35.46 |  |
| plates | 9.00 | 10.00 | 14.00 |  |
| ocean_age | 39.90 | 56.10 | 71.00 |  |
| speed | 2.70 | 4.24 | 5.55 |  |
| sea_level | -175.60 | 7.40 | 133.60 |  |
| sea_ice_m | -126.10 | -31.30 | -18.60 |  |
| sea_tect_m | -85.40 | 44.30 | 169.80 |  |
| ice_pct | 1.50 | 2.10 | 5.80 |  |
| temp | 10.00 | 13.00 | 16.90 |  |
| co2 | -1.27 | -0.64 | -0.21 |  |
| dry_pct | 20.42 | 23.33 | 27.36 |  |
| inland_pct | 1.14 | 3.91 | 26.55 | 300-300: 5.97; 320-488: 1.14 |
| lake_pct | 0.24 | 0.47 | 5.66 | 492-492: 5.66 |
| lake_max_mkm2 | 0.03 | 0.09 | 6.45 | 492-492: 6.45 |
| max_elev_km | 3.97 | 5.00 | 8.32 |  |
| trees_pct | 17.72 | 28.37 | 41.72 |  |
| npp | 180.50 | 324.60 | 331.80 | 416-440: 180.50 |
| landmasses | 3.00 | 7.00 | 13.00 |  |
| largest_pct | 19.20 | 26.30 | 33.40 |  |

## Determinism

(not run)
