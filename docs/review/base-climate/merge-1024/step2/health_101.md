# Health sweep 2026-10-23 12:47

Commit feec571. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 12.1 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 500 | ea1745 | 554 | 136 / 408 | 4.0 | 0 | 7.8 | 0.962 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 102 | 6 | 500 | de9dc9 | 563 | 140 / 392 | 6.0 | 0 | 2.0 | 0.953 | 0.0 | 0.0 | ok | ok | 17.6 |
| 103 | 6 | 500 | 9187cb | 726 | 128 / 424 | 11.4 | 0 | 3.9 | 0.976 | 3.9 | 0.0 | ok | F: icehouse 88% of the time, outside 5-70% | 88.2 |
| 104 | 6 | 500 | bb8ab6 | 616 | 124 / 432 | 7.8 | 0 | 9.8 | 0.984 | 0.0 | 0.0 | ok | ok | 41.2 |
| 105 | 6 | 500 | ebcbe5 | 675 | 132 / 376 | 11.5 | 0 | 3.9 | 0.985 | 21.6 | 0.0 | ok | F: icehouse 84% of the time, outside 5-70% | 84.3 |
| 106 | 6 | 500 | f4fa03 | 592 | 132 / 396 | 8.8 | 0 | 5.9 | 0.973 | 0.0 | 0.0 | ok | ok | 35.3 |
| 107 | 6 | 500 | f55641 | 640 | 132 / 404 | 8.8 | 0 | 2.0 | 0.948 | 0.0 | 0.0 | ok | ok | 33.3 |
| 108 | 6 | 500 | f690cc | 573 | 128 / 376 | 10.6 | 0 | 0.0 | 0.971 | 0.0 | 0.0 | ok | ok | 29.4 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 34.1 | 41.3 | 32.7 | 14.0 | 60.1 | 3.9 | 36.6 | -0.2 | 38.4 | 0.0 | 17.0 | -0.6 | 28.5 | 4.7 | 0.2 | 0.0 | 3.9 | 9.2 | 333.4 | 6.0 | 16.0 |
| 102 | 6 | 33.0 | 41.2 | 32.8 | 14.0 | 49.9 | 4.1 | 150.1 | -4.4 | 159.5 | 0.4 | 15.1 | 0.1 | 24.8 | 3.2 | 0.3 | 0.1 | 4.1 | 33.7 | 361.6 | 10.0 | 10.9 |
| 103 | 6 | 32.1 | 41.0 | 33.7 | 13.0 | 50.0 | 3.7 | 27.1 | -61.3 | 99.7 | 2.8 | 12.7 | -0.7 | 29.3 | 4.6 | 0.3 | 0.1 | 5.4 | 9.2 | 284.0 | 8.0 | 25.4 |
| 104 | 6 | 32.8 | 40.5 | 33.8 | 11.0 | 52.1 | 3.6 | 113.5 | -14.6 | 115.9 | 0.9 | 13.8 | -0.2 | 29.8 | 4.0 | 0.4 | 0.1 | 5.5 | 24.9 | 288.4 | 7.0 | 22.7 |
| 105 | 6 | 33.3 | 38.7 | 35.2 | 11.0 | 61.5 | 4.2 | -7.9 | -27.9 | 18.0 | 1.8 | 15.3 | 0.0 | 17.2 | 3.5 | 0.6 | 0.1 | 5.8 | 34.8 | 315.4 | 8.0 | 23.7 |
| 106 | 6 | 33.4 | 40.3 | 33.6 | 11.0 | 56.2 | 4.7 | 39.3 | -16.9 | 66.0 | 1.0 | 14.6 | 0.3 | 28.7 | 4.3 | 0.4 | 0.1 | 5.4 | 29.8 | 310.0 | 8.0 | 20.1 |
| 107 | 6 | 34.1 | 40.8 | 33.2 | 11.0 | 66.2 | 4.7 | -39.7 | -8.7 | -30.7 | 0.7 | 11.7 | -0.4 | 28.5 | 3.2 | 0.4 | 0.1 | 6.3 | 20.3 | 273.8 | 9.0 | 18.8 |
| 108 | 6 | 32.7 | 40.3 | 33.9 | 17.0 | 49.3 | 4.3 | 147.6 | -11.2 | 154.7 | 0.7 | 13.9 | 0.0 | 24.1 | 3.8 | 0.4 | 0.1 | 6.5 | 27.6 | 305.6 | 8.0 | 26.6 |

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

## Top outliers (of 71 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 105 | 6 | sea_ice_below_150 | run | - | 21.60 | -..10 | 1.16 |
| 104 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 101 | 6 | lake_max_mkm2 | 308-320 | 4 | 3.64 | -..1.0 | 0.611 |
| 101 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 103 | 6 | lake_max_mkm2 | 324-324 | 1 | 2.86 | -..1.0 | 0.388 |
| 106 | 6 | lake_max_mkm2 | 404-404 | 1 | 2.58 | -..1.0 | 0.328 |
| 103 | 6 | lake_max_mkm2 | 344-344 | 1 | 2.44 | -..1.0 | 0.3 |
| 107 | 6 | lake_max_mkm2 | 452-452 | 1 | 2.18 | -..1.0 | 0.245 |
| 105 | 6 | inland_pct | 300-488 | 47 | 0.29 | 8..30 | 0.201 |
| 108 | 6 | inland_pct | 320-500 | 46 | 0.62 | 8..30 | 0.19 |
| 106 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 102 | 6 | inland_pct | 300-500 | 49 | 1.33 | 8..30 | 0.179 |
| 107 | 6 | inland_pct | 332-500 | 43 | 0.87 | 8..30 | 0.175 |
| 104 | 6 | lake_max_mkm2 | 376-392 | 5 | 1.72 | -..1.0 | 0.172 |
| 103 | 6 | inland_pct | 304-500 | 46 | 1.34 | 8..30 | 0.171 |
| 101 | 6 | inland_pct | 300-500 | 48 | 1.70 | 8..30 | 0.166 |
| 104 | 6 | inland_pct | 396-500 | 27 | 1.53 | 8..30 | 0.122 |
| 104 | 6 | inland_pct | 300-372 | 19 | 0.96 | 8..30 | 0.112 |
| 106 | 6 | inland_pct | 328-424 | 25 | 2.06 | 8..30 | 0.108 |
| 106 | 6 | lake_max_mkm2 | 312-312 | 1 | 1.51 | -..1.0 | 0.105 |
| 105 | 6 | sea_ice_m | 464-488 | 7 | -344.30 | -250..- | 0.096 |
| 103 | 6 | trees_pct | 400-500 | 26 | 1.15 | 10..50 | 0.09 |
| 106 | 6 | inland_pct | 436-500 | 16 | 2.20 | 8..30 | 0.086 |
| 106 | 6 | inland_pct | 300-316 | 4 | 1.45 | 8..30 | 0.069 |
| 101 | 6 | trees_pct | 312-376 | 15 | 1.60 | 10..50 | 0.067 |
| 107 | 6 | sea_level | 472-500 | 8 | -373.20 | -250..300 | 0.059 |
| 105 | 6 | sea_level | 464-500 | 10 | -360.90 | -250..300 | 0.056 |
| 101 | 6 | trees_pct | 416-452 | 10 | 3.91 | 10..50 | 0.043 |
| 101 | 6 | trees_pct | 492-500 | 3 | 2.60 | 10..50 | 0.041 |
| 107 | 6 | trees_pct | 416-452 | 9 | 4.45 | 10..50 | 0.038 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 101, L6 (run ea1745)

![seed 101 L6](seed101_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.45 | 34.08 | 34.66 |  |
| cont_pct | 39.65 | 41.26 | 41.57 |  |
| cont_km | 32.42 | 32.73 | 34.40 |  |
| plates | 12.00 | 14.00 | 17.00 |  |
| ocean_age | 52.00 | 60.10 | 63.70 |  |
| speed | 3.29 | 3.90 | 5.24 |  |
| sea_level | 6.70 | 36.60 | 90.00 |  |
| sea_ice_m | -3.00 | -0.20 | -0.00 |  |
| sea_tect_m | 7.90 | 38.40 | 90.00 |  |
| ice_pct | 0.00 | 0.00 | 0.20 |  |
| temp | 15.20 | 17.00 | 19.20 |  |
| co2 | -1.12 | -0.63 | 0.23 |  |
| dry_pct | 24.45 | 28.52 | 32.07 |  |
| inland_pct | 1.70 | 4.65 | 9.52 | 300-500: 1.70 |
| lake_pct | 0.09 | 0.21 | 2.38 | 356-356: 0.18; 372-372: 0.17; 384-388: 0.19; 420-480: 0.09; +1 more |
| lake_max_mkm2 | 0.01 | 0.04 | 3.64 | 308-320: 3.64 |
| max_elev_km | 3.08 | 3.90 | 8.38 |  |
| trees_pct | 1.60 | 9.20 | 36.28 | 312-376: 1.60; 416-452: 3.91; 492-500: 2.60 |
| npp | 210.60 | 333.45 | 380.50 |  |
| landmasses | 3.00 | 6.00 | 11.00 |  |
| largest_pct | 10.60 | 16.00 | 19.80 |  |

### Seed 102, L6 (run de9dc9)

![seed 102 L6](seed102_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.62 | 32.99 | 33.81 |  |
| cont_pct | 40.05 | 41.16 | 42.20 |  |
| cont_km | 32.32 | 32.82 | 34.03 |  |
| plates | 11.00 | 14.00 | 17.00 |  |
| ocean_age | 43.70 | 49.90 | 55.50 |  |
| speed | 3.46 | 4.06 | 4.79 |  |
| sea_level | 79.30 | 150.10 | 205.70 |  |
| sea_ice_m | -29.10 | -4.40 | -0.00 |  |
| sea_tect_m | 89.00 | 159.50 | 209.60 |  |
| ice_pct | 0.00 | 0.40 | 1.50 |  |
| temp | 12.50 | 15.10 | 18.50 |  |
| co2 | -0.51 | 0.07 | 0.73 |  |
| dry_pct | 16.66 | 24.76 | 35.69 |  |
| inland_pct | 1.33 | 3.20 | 8.58 | 300-500: 1.33 |
| lake_pct | 0.12 | 0.29 | 1.03 | 300-340: 0.12; 360-360: 0.18; 408-416: 0.18; 456-456: 0.19 |
| lake_max_mkm2 | 0.03 | 0.06 | 1.05 | 424-424: 1.05 |
| max_elev_km | 3.19 | 4.11 | 8.25 |  |
| trees_pct | 18.94 | 33.68 | 47.77 |  |
| npp | 196.80 | 361.65 | 413.50 | 432-432: 196.80 |
| landmasses | 6.00 | 10.00 | 15.00 |  |
| largest_pct | 8.70 | 10.90 | 24.30 |  |

### Seed 103, L6 (run 9187cb)

![seed 103 L6](seed103_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.21 | 32.08 | 33.61 |  |
| cont_pct | 39.15 | 41.02 | 43.04 |  |
| cont_km | 31.98 | 33.66 | 34.83 |  |
| plates | 10.00 | 13.00 | 16.00 |  |
| ocean_age | 42.80 | 50.00 | 70.00 |  |
| speed | 3.22 | 3.68 | 5.35 |  |
| sea_level | -141.30 | 27.10 | 108.20 |  |
| sea_ice_m | -199.40 | -61.30 | -13.20 |  |
| sea_tect_m | -33.50 | 99.70 | 167.90 |  |
| ice_pct | 1.10 | 2.80 | 7.90 |  |
| temp | 6.90 | 12.70 | 18.30 | 300-304: 6.90 |
| co2 | -1.84 | -0.68 | 0.58 |  |
| dry_pct | 23.31 | 29.26 | 33.62 |  |
| inland_pct | 1.34 | 4.58 | 17.01 | 304-500: 1.34 |
| lake_pct | 0.12 | 0.32 | 2.53 | 440-440: 0.18; 472-488: 0.12 |
| lake_max_mkm2 | 0.01 | 0.05 | 2.86 | 324-324: 2.86; 344-344: 2.44 |
| max_elev_km | 4.08 | 5.41 | 7.27 |  |
| trees_pct | 1.15 | 9.25 | 45.68 | 400-500: 1.15 |
| npp | 251.30 | 284.00 | 325.30 |  |
| landmasses | 4.00 | 8.00 | 20.00 |  |
| largest_pct | 16.40 | 25.40 | 32.40 |  |

### Seed 104, L6 (run bb8ab6)

![seed 104 L6](seed104_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.67 | 32.77 | 34.02 |  |
| cont_pct | 39.69 | 40.46 | 40.95 |  |
| cont_km | 33.18 | 33.78 | 34.33 |  |
| plates | 9.00 | 11.00 | 16.00 |  |
| ocean_age | 41.60 | 52.10 | 72.20 |  |
| speed | 2.53 | 3.63 | 5.33 |  |
| sea_level | -95.70 | 113.50 | 180.40 |  |
| sea_ice_m | -55.40 | -14.60 | -0.70 |  |
| sea_tect_m | -44.30 | 115.90 | 196.50 |  |
| ice_pct | 0.10 | 0.90 | 3.10 |  |
| temp | 11.60 | 13.80 | 19.40 |  |
| co2 | -0.71 | -0.21 | 0.17 |  |
| dry_pct | 21.73 | 29.76 | 35.66 |  |
| inland_pct | 0.96 | 4.03 | 13.12 | 300-372: 0.96; 396-500: 1.53 |
| lake_pct | 0.12 | 0.44 | 1.41 | 316-316: 0.19; 348-360: 0.12; 412-412: 0.20 |
| lake_max_mkm2 | 0.01 | 0.10 | 1.72 | 376-392: 1.72 |
| max_elev_km | 4.02 | 5.46 | 7.95 |  |
| trees_pct | 9.52 | 24.93 | 41.31 | 336-336: 9.52; 400-400: 9.70 |
| npp | 207.20 | 288.40 | 338.00 |  |
| landmasses | 2.00 | 7.00 | 10.00 | 500-500: 2 |
| largest_pct | 11.80 | 22.70 | 32.80 |  |

### Seed 105, L6 (run ebcbe5)

![seed 105 L6](seed105_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.25 | 33.29 | 34.27 |  |
| cont_pct | 37.62 | 38.72 | 41.25 |  |
| cont_km | 33.69 | 35.25 | 35.83 |  |
| plates | 8.00 | 11.00 | 14.00 |  |
| ocean_age | 57.40 | 61.50 | 68.10 |  |
| speed | 2.95 | 4.17 | 4.94 |  |
| sea_level | -360.90 | -7.90 | 39.20 | 464-500: -360.90 |
| sea_ice_m | -344.30 | -27.90 | -7.70 | 464-488: -344.30 |
| sea_tect_m | -30.80 | 18.00 | 51.50 |  |
| ice_pct | 0.50 | 1.80 | 9.30 |  |
| temp | 7.30 | 15.30 | 18.80 | 468-468: 7.90; 500-500: 7.30 |
| co2 | -0.92 | 0.04 | 0.66 |  |
| dry_pct | 12.65 | 17.16 | 26.42 |  |
| inland_pct | 0.29 | 3.55 | 10.93 | 300-488: 0.29; 500-500: 6.55 |
| lake_pct | 0.27 | 0.64 | 1.49 |  |
| lake_max_mkm2 | 0.03 | 0.14 | 1.11 | 304-304: 1.11; 360-360: 1.11 |
| max_elev_km | 4.24 | 5.78 | 8.25 |  |
| trees_pct | 14.34 | 34.82 | 46.54 |  |
| npp | 261.50 | 315.40 | 388.00 |  |
| landmasses | 2.00 | 8.00 | 13.00 | 496-496: 2 |
| largest_pct | 11.80 | 23.70 | 29.60 |  |

### Seed 106, L6 (run f4fa03)

![seed 106 L6](seed106_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.12 | 33.38 | 33.94 |  |
| cont_pct | 38.61 | 40.31 | 41.15 |  |
| cont_km | 33.00 | 33.61 | 35.13 |  |
| plates | 8.00 | 11.00 | 13.00 |  |
| ocean_age | 46.30 | 56.20 | 72.90 |  |
| speed | 3.45 | 4.65 | 4.95 |  |
| sea_level | -88.10 | 39.30 | 153.10 |  |
| sea_ice_m | -46.40 | -16.90 | -3.10 |  |
| sea_tect_m | -66.80 | 66.00 | 156.60 |  |
| ice_pct | 0.20 | 1.00 | 3.10 |  |
| temp | 11.50 | 14.60 | 20.30 |  |
| co2 | -0.71 | 0.27 | 0.93 |  |
| dry_pct | 17.86 | 28.66 | 33.35 |  |
| inland_pct | 1.45 | 4.28 | 11.62 | 300-316: 1.45; 328-424: 2.06; 436-500: 2.20 |
| lake_pct | 0.15 | 0.36 | 2.17 | 352-352: 0.17; 372-376: 0.15 |
| lake_max_mkm2 | 0.03 | 0.10 | 2.58 | 312-312: 1.51; 404-404: 2.58; 480-480: 1.06 |
| max_elev_km | 4.14 | 5.38 | 8.23 |  |
| trees_pct | 14.46 | 29.80 | 35.24 |  |
| npp | 141.60 | 310.00 | 371.60 | 396-404: 141.60; 416-420: 171.20 |
| landmasses | 4.00 | 8.00 | 15.00 |  |
| largest_pct | 8.70 | 20.10 | 31.60 |  |

### Seed 107, L6 (run f55641)

![seed 107 L6](seed107_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.47 | 34.10 | 34.52 |  |
| cont_pct | 40.20 | 40.80 | 41.58 |  |
| cont_km | 32.70 | 33.18 | 34.25 |  |
| plates | 6.00 | 11.00 | 12.00 |  |
| ocean_age | 53.50 | 66.20 | 86.10 |  |
| speed | 2.66 | 4.68 | 5.51 |  |
| sea_level | -373.20 | -39.70 | 79.90 | 472-500: -373.20 |
| sea_ice_m | -149.60 | -8.70 | -0.60 |  |
| sea_tect_m | -223.60 | -30.70 | 81.60 |  |
| ice_pct | 0.00 | 0.70 | 6.20 |  |
| temp | 8.20 | 11.70 | 17.00 |  |
| co2 | -1.37 | -0.36 | 0.42 |  |
| dry_pct | 12.42 | 28.49 | 47.82 | 300-308: 47.82 |
| inland_pct | 0.87 | 3.20 | 13.10 | 308-308: 7.19; 332-500: 0.87 |
| lake_pct | 0.17 | 0.35 | 1.67 | 304-304: 0.19; 356-360: 0.17; 392-400: 0.18 |
| lake_max_mkm2 | 0.03 | 0.11 | 2.18 | 452-452: 2.18 |
| max_elev_km | 4.07 | 6.30 | 8.64 |  |
| trees_pct | 4.45 | 20.29 | 40.00 | 344-344: 5.93; 416-452: 4.45 |
| npp | 124.90 | 273.80 | 451.50 | 408-428: 124.90 |
| landmasses | 4.00 | 9.00 | 13.00 |  |
| largest_pct | 14.10 | 18.80 | 34.00 |  |

### Seed 108, L6 (run f690cc)

![seed 108 L6](seed108_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.49 | 32.66 | 34.45 |  |
| cont_pct | 39.03 | 40.26 | 40.94 |  |
| cont_km | 33.27 | 33.91 | 34.84 |  |
| plates | 12.00 | 17.00 | 19.00 |  |
| ocean_age | 33.20 | 49.30 | 73.10 |  |
| speed | 2.60 | 4.32 | 5.96 |  |
| sea_level | -221.80 | 147.60 | 263.20 |  |
| sea_ice_m | -128.50 | -11.20 | -1.00 |  |
| sea_tect_m | -105.90 | 154.70 | 267.50 |  |
| ice_pct | 0.10 | 0.70 | 4.60 |  |
| temp | 9.00 | 13.90 | 19.60 |  |
| co2 | -1.09 | 0.04 | 1.77 |  |
| dry_pct | 17.00 | 24.09 | 39.51 |  |
| inland_pct | 0.62 | 3.76 | 11.87 | 320-500: 0.62 |
| lake_pct | 0.14 | 0.44 | 1.18 | 344-352: 0.14 |
| lake_max_mkm2 | 0.03 | 0.09 | 0.80 |  |
| max_elev_km | 3.70 | 6.50 | 8.24 |  |
| trees_pct | 7.16 | 27.62 | 55.35 | 360-372: 55.35; 492-492: 7.16 |
| npp | 217.50 | 305.65 | 388.60 |  |
| landmasses | 5.00 | 8.00 | 12.00 |  |
| largest_pct | 11.20 | 26.60 | 30.90 |  |

## Determinism

Seed 101 L6 re-run to 100 Myr (run 04a54f) against the sweep's run ea1745: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
