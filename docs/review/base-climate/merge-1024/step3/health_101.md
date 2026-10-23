# Health sweep 2026-10-23 13:11

Commit c13b567. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 11.4 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 500 | 32a059 | 544 | 136 / 408 | 5.0 | 0 | 0.0 | 0.972 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 102 | 6 | 500 | 8806f8 | 532 | 140 / 392 | 7.5 | 0 | 3.9 | 0.96 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 103 | 6 | 500 | 1547ba | 572 | 128 / 424 | 14.0 | 0 | 2.0 | 0.974 | 17.6 | 0.0 | ok | ok | 51.0 |
| 104 | 6 | 500 | d24ec7 | 649 | 124 / 432 | 8.0 | 0 | 3.9 | 0.966 | 0.0 | 0.0 | ok | F: icehouse 75% of the time, outside 5-70% | 74.5 |
| 105 | 6 | 500 | 103e30 | 683 | 132 / 376 | 8.1 | 0 | 17.6 | 0.958 | 0.0 | 0.0 | ok | ok | 33.3 |
| 106 | 6 | 500 | 42ca94 | 553 | 132 / 396 | 5.0 | 0 | 5.9 | 0.978 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 107 | 6 | 500 | bd9747 | 549 | 132 / 404 | 4.6 | 0 | 3.9 | 0.966 | 37.3 | 0.0 | F | F: icehouse 100% of the time, outside 5-70% | 100.0 |
| 108 | 6 | 500 | 1db687 | 567 | 128 / 376 | 7.5 | 0 | 11.8 | 0.975 | 3.9 | 0.0 | ok | ok | 54.9 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 33.9 | 40.7 | 33.4 | 15.0 | 52.8 | 4.2 | 89.2 | -0.2 | 89.2 | 0.0 | 17.3 | -0.5 | 29.3 | 5.2 | 0.3 | 0.1 | 4.5 | 9.3 | 360.8 | 6.0 | 22.0 |
| 102 | 6 | 32.4 | 40.7 | 33.1 | 14.0 | 43.8 | 4.9 | 198.3 | -3.5 | 206.0 | 0.2 | 16.8 | 0.4 | 26.0 | 5.0 | 0.4 | 0.1 | 4.8 | 30.1 | 313.4 | 12.0 | 16.0 |
| 103 | 6 | 32.0 | 40.0 | 34.3 | 13.0 | 46.0 | 4.2 | 96.8 | -30.1 | 141.4 | 1.4 | 14.5 | -0.3 | 31.0 | 6.7 | 0.3 | 0.1 | 4.9 | 17.6 | 352.4 | 7.0 | 22.2 |
| 104 | 6 | 33.4 | 41.1 | 33.0 | 12.0 | 46.8 | 4.6 | 76.8 | -35.5 | 182.2 | 1.8 | 13.8 | -0.0 | 24.0 | 3.6 | 0.3 | 0.1 | 5.2 | 31.1 | 305.0 | 8.0 | 21.7 |
| 105 | 6 | 33.5 | 40.3 | 33.6 | 10.0 | 65.0 | 4.0 | -40.6 | -12.5 | -26.1 | 0.9 | 16.1 | 0.3 | 17.0 | 3.3 | 0.7 | 0.3 | 4.6 | 38.0 | 356.0 | 8.0 | 14.7 |
| 106 | 6 | 34.2 | 40.7 | 33.6 | 13.0 | 45.9 | 4.4 | 170.1 | -2.1 | 172.0 | 0.2 | 18.5 | 0.8 | 23.7 | 4.0 | 0.3 | 0.1 | 3.8 | 39.1 | 386.5 | 7.0 | 17.7 |
| 107 | 6 | 33.2 | 42.3 | 32.1 | 10.0 | 77.8 | 3.6 | -202.5 | -79.3 | -123.2 | 3.4 | 11.2 | -0.4 | 23.6 | 2.8 | 0.3 | 0.1 | 6.1 | 21.0 | 408.8 | 5.0 | 32.1 |
| 108 | 6 | 33.6 | 39.4 | 34.8 | 12.0 | 53.4 | 4.5 | 76.8 | -27.9 | 98.1 | 1.9 | 14.9 | 0.4 | 23.5 | 5.8 | 0.6 | 0.1 | 5.1 | 38.8 | 346.9 | 5.0 | 24.4 |

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

## Top outliers (of 76 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 107 | 6 | sea_ice_below_150 | run | - | 37.30 | -..10 | 2.73 |
| 105 | 6 | giant_lake_frames | run | - | 17.60 | -..5 | 2.52 |
| 108 | 6 | giant_lake_frames | run | - | 11.80 | -..5 | 1.36 |
| 108 | 6 | lake_max_mkm2 | 428-428 | 1 | 7.08 | -..1.0 | 1.265 |
| 103 | 6 | sea_ice_below_150 | run | - | 17.60 | -..10 | 0.76 |
| 105 | 6 | lake_max_mkm2 | 320-328 | 3 | 3.64 | -..1.0 | 0.59 |
| 102 | 6 | lake_max_mkm2 | 440-440 | 1 | 2.69 | -..1.0 | 0.351 |
| 107 | 6 | sea_level | 300-388 | 23 | -588.40 | -250..300 | 0.235 |
| 105 | 6 | lake_max_mkm2 | 432-448 | 4 | 1.99 | -..1.0 | 0.23 |
| 106 | 6 | lake_max_mkm2 | 304-304 | 1 | 2.08 | -..1.0 | 0.225 |
| 102 | 6 | lake_max_mkm2 | 500-500 | 1 | 2.03 | -..1.0 | 0.214 |
| 101 | 6 | inland_pct | 300-500 | 49 | 1.28 | 8..30 | 0.18 |
| 106 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 107 | 6 | inland_pct | 312-500 | 48 | 1.22 | 8..30 | 0.179 |
| 106 | 6 | inland_pct | 300-500 | 48 | 1.33 | 8..30 | 0.176 |
| 102 | 6 | inland_pct | 304-500 | 48 | 1.72 | 8..30 | 0.166 |
| 108 | 6 | lake_max_mkm2 | 384-388 | 2 | 1.76 | -..1.0 | 0.163 |
| 104 | 6 | inland_pct | 300-448 | 38 | 0.89 | 8..30 | 0.162 |
| 105 | 6 | inland_pct | 380-500 | 31 | 0.50 | 8..30 | 0.152 |
| 108 | 6 | inland_pct | 344-496 | 35 | 1.28 | 8..30 | 0.146 |
| 104 | 6 | lake_max_mkm2 | 452-456 | 2 | 1.59 | -..1.0 | 0.128 |
| 107 | 6 | lake_max_mkm2 | 488-488 | 1 | 1.61 | -..1.0 | 0.126 |
| 108 | 6 | lake_pct | 428-428 | 1 | 4.66 | 0.2..3.0 | 0.123 |
| 107 | 6 | lake_max_mkm2 | 432-432 | 1 | 1.56 | -..1.0 | 0.116 |
| 103 | 6 | inland_pct | 324-500 | 39 | 3.48 | 8..30 | 0.105 |
| 105 | 6 | lake_max_mkm2 | 368-368 | 1 | 1.51 | -..1.0 | 0.105 |
| 106 | 6 | lake_max_mkm2 | 408-416 | 2 | 1.47 | -..1.0 | 0.101 |
| 103 | 6 | sea_ice_m | 300-316 | 5 | -343.50 | -250..- | 0.09 |
| 104 | 6 | inland_pct | 460-500 | 11 | 2.09 | 8..30 | 0.077 |
| 101 | 6 | trees_pct | 324-388 | 17 | 1.08 | 10..50 | 0.075 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 101, L6 (run 32a059)

![seed 101 L6](seed101_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.31 | 33.85 | 34.74 |  |
| cont_pct | 39.07 | 40.72 | 41.25 |  |
| cont_km | 33.00 | 33.41 | 34.58 |  |
| plates | 12.00 | 15.00 | 18.00 |  |
| ocean_age | 40.00 | 52.80 | 64.60 |  |
| speed | 3.32 | 4.22 | 4.95 |  |
| sea_level | -14.80 | 89.20 | 196.40 |  |
| sea_ice_m | -7.70 | -0.20 | -0.00 |  |
| sea_tect_m | -7.20 | 89.20 | 196.40 |  |
| ice_pct | 0.00 | 0.00 | 0.40 |  |
| temp | 15.90 | 17.30 | 20.90 |  |
| co2 | -1.35 | -0.52 | 0.46 |  |
| dry_pct | 19.13 | 29.27 | 40.81 |  |
| inland_pct | 1.28 | 5.17 | 10.96 | 300-500: 1.28 |
| lake_pct | 0.14 | 0.29 | 0.80 | 368-412: 0.14 |
| lake_max_mkm2 | 0.01 | 0.06 | 0.36 |  |
| max_elev_km | 3.56 | 4.51 | 8.34 |  |
| trees_pct | 1.08 | 9.32 | 38.65 | 324-388: 1.08; 420-452: 5.20 |
| npp | 242.30 | 360.80 | 413.10 |  |
| landmasses | 3.00 | 6.00 | 10.00 |  |
| largest_pct | 11.10 | 22.00 | 27.30 |  |

### Seed 102, L6 (run 8806f8)

![seed 102 L6](seed102_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.95 | 32.43 | 33.44 |  |
| cont_pct | 39.40 | 40.67 | 41.27 |  |
| cont_km | 32.77 | 33.10 | 34.53 |  |
| plates | 8.00 | 14.00 | 17.00 |  |
| ocean_age | 39.60 | 43.80 | 66.20 |  |
| speed | 2.90 | 4.92 | 6.13 |  |
| sea_level | -27.60 | 198.30 | 240.20 |  |
| sea_ice_m | -19.70 | -3.50 | -0.00 |  |
| sea_tect_m | -12.60 | 206.00 | 242.10 |  |
| ice_pct | 0.00 | 0.20 | 1.50 |  |
| temp | 13.10 | 16.80 | 20.60 |  |
| co2 | -0.65 | 0.38 | 1.07 |  |
| dry_pct | 17.15 | 25.96 | 31.58 |  |
| inland_pct | 1.72 | 5.00 | 8.71 | 304-500: 1.72 |
| lake_pct | 0.17 | 0.37 | 2.08 | 352-352: 0.17; 376-376: 0.17 |
| lake_max_mkm2 | 0.01 | 0.07 | 2.69 | 440-440: 2.69; 500-500: 2.03 |
| max_elev_km | 3.98 | 4.83 | 7.80 |  |
| trees_pct | 17.45 | 30.14 | 48.63 |  |
| npp | 265.00 | 313.45 | 372.90 |  |
| landmasses | 7.00 | 12.00 | 17.00 |  |
| largest_pct | 11.00 | 16.00 | 25.50 |  |

### Seed 103, L6 (run 1547ba)

![seed 103 L6](seed103_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.47 | 31.97 | 33.23 |  |
| cont_pct | 37.33 | 39.98 | 40.78 |  |
| cont_km | 33.64 | 34.31 | 35.97 |  |
| plates | 11.00 | 13.00 | 15.00 |  |
| ocean_age | 41.40 | 46.00 | 58.30 |  |
| speed | 2.62 | 4.15 | 4.89 |  |
| sea_level | -344.10 | 96.80 | 186.80 | 300-308: -344.10 |
| sea_ice_m | -343.50 | -30.10 | -5.70 | 300-316: -343.50 |
| sea_tect_m | -0.50 | 141.40 | 193.60 |  |
| ice_pct | 0.40 | 1.40 | 8.80 |  |
| temp | 6.70 | 14.50 | 20.70 | 300-304: 6.70; 320-324: 7.60 |
| co2 | -1.27 | -0.28 | 0.62 |  |
| dry_pct | 24.41 | 31.02 | 45.88 | 452-456: 45.88 |
| inland_pct | 3.48 | 6.65 | 22.28 | 324-500: 3.48 |
| lake_pct | 0.14 | 0.32 | 2.56 | 412-412: 0.16; 436-452: 0.18; 472-488: 0.14 |
| lake_max_mkm2 | 0.03 | 0.06 | 1.22 | 392-392: 1.22 |
| max_elev_km | 3.89 | 4.89 | 8.29 |  |
| trees_pct | 0.69 | 17.55 | 36.50 | 352-352: 8.76; 392-440: 0.69 |
| npp | 263.90 | 352.40 | 412.60 |  |
| landmasses | 3.00 | 7.00 | 14.00 |  |
| largest_pct | 15.30 | 22.20 | 23.60 |  |

### Seed 104, L6 (run d24ec7)

![seed 104 L6](seed104_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.27 | 33.37 | 34.30 |  |
| cont_pct | 39.19 | 41.12 | 41.49 |  |
| cont_km | 32.75 | 33.05 | 34.81 |  |
| plates | 9.00 | 12.00 | 16.00 |  |
| ocean_age | 42.00 | 46.80 | 70.80 |  |
| speed | 3.16 | 4.61 | 5.41 |  |
| sea_level | -139.90 | 76.80 | 197.80 |  |
| sea_ice_m | -142.60 | -35.50 | -10.60 |  |
| sea_tect_m | -95.90 | 182.20 | 209.10 |  |
| ice_pct | 0.60 | 1.80 | 4.70 |  |
| temp | 11.50 | 13.80 | 19.50 |  |
| co2 | -0.72 | -0.01 | 0.35 |  |
| dry_pct | 16.11 | 23.99 | 30.02 |  |
| inland_pct | 0.89 | 3.63 | 16.39 | 300-448: 0.89; 460-500: 2.09 |
| lake_pct | 0.10 | 0.30 | 1.37 | 316-316: 0.19; 364-380: 0.10 |
| lake_max_mkm2 | 0.03 | 0.05 | 1.59 | 452-456: 1.59 |
| max_elev_km | 3.98 | 5.15 | 6.36 |  |
| trees_pct | 8.44 | 31.09 | 53.20 | 312-312: 8.44; 432-452: 53.20 |
| npp | 239.70 | 304.95 | 410.80 |  |
| landmasses | 2.00 | 8.00 | 11.00 | 300-300: 2; 316-316: 2 |
| largest_pct | 13.50 | 21.70 | 27.50 |  |

### Seed 105, L6 (run 103e30)

![seed 105 L6](seed105_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.20 | 33.46 | 34.46 |  |
| cont_pct | 39.28 | 40.29 | 41.01 |  |
| cont_km | 33.15 | 33.62 | 34.90 |  |
| plates | 7.00 | 10.00 | 14.00 |  |
| ocean_age | 56.90 | 65.00 | 70.20 |  |
| speed | 2.50 | 4.02 | 4.91 |  |
| sea_level | -104.80 | -40.60 | 28.20 |  |
| sea_ice_m | -66.00 | -12.50 | -3.90 |  |
| sea_tect_m | -46.70 | -26.10 | 33.40 |  |
| ice_pct | 0.30 | 0.90 | 3.60 |  |
| temp | 11.30 | 16.10 | 19.40 |  |
| co2 | -0.39 | 0.30 | 1.13 |  |
| dry_pct | 12.36 | 17.02 | 27.18 |  |
| inland_pct | 0.50 | 3.27 | 15.68 | 300-300: 7.39; 328-328: 7.57; 348-364: 4.69; 380-500: 0.50 |
| lake_pct | 0.28 | 0.71 | 2.96 |  |
| lake_max_mkm2 | 0.04 | 0.29 | 3.64 | 320-328: 3.64; 368-368: 1.51; 416-416: 1.16; 432-448: 1.99 |
| max_elev_km | 3.45 | 4.60 | 7.40 |  |
| trees_pct | 18.70 | 38.05 | 51.86 | 364-368: 51.86 |
| npp | 282.50 | 356.05 | 458.10 |  |
| landmasses | 5.00 | 8.00 | 12.00 |  |
| largest_pct | 8.00 | 14.70 | 19.50 |  |

### Seed 106, L6 (run 42ca94)

![seed 106 L6](seed106_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.69 | 34.19 | 34.79 |  |
| cont_pct | 38.84 | 40.71 | 41.59 |  |
| cont_km | 33.16 | 33.56 | 34.71 |  |
| plates | 11.00 | 13.00 | 15.00 |  |
| ocean_age | 39.70 | 45.90 | 54.60 |  |
| speed | 3.44 | 4.37 | 5.01 |  |
| sea_level | -0.80 | 170.10 | 216.60 |  |
| sea_ice_m | -10.70 | -2.10 | -0.00 |  |
| sea_tect_m | -0.70 | 172.00 | 219.00 |  |
| ice_pct | 0.00 | 0.20 | 0.80 |  |
| temp | 15.20 | 18.50 | 20.20 |  |
| co2 | 0.02 | 0.84 | 1.41 |  |
| dry_pct | 12.81 | 23.70 | 40.03 |  |
| inland_pct | 1.33 | 3.96 | 14.07 | 300-500: 1.33 |
| lake_pct | 0.14 | 0.35 | 1.49 | 328-336: 0.14; 356-360: 0.14 |
| lake_max_mkm2 | 0.03 | 0.07 | 2.08 | 304-304: 2.08; 408-416: 1.47 |
| max_elev_km | 2.82 | 3.75 | 8.34 |  |
| trees_pct | 19.95 | 39.14 | 51.38 | 412-412: 51.38 |
| npp | 265.60 | 386.50 | 416.20 |  |
| landmasses | 2.00 | 7.00 | 11.00 | 308-312: 2 |
| largest_pct | 16.20 | 17.70 | 28.40 |  |

### Seed 107, L6 (run bd9747)

![seed 107 L6](seed107_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.61 | 33.21 | 35.63 |  |
| cont_pct | 40.50 | 42.30 | 42.70 |  |
| cont_km | 31.75 | 32.10 | 33.72 |  |
| plates | 6.00 | 10.00 | 12.00 |  |
| ocean_age | 67.10 | 77.80 | 105.70 |  |
| speed | 2.42 | 3.58 | 4.55 |  |
| sea_level | -588.40 | -202.50 | -109.00 | 300-388: -588.40 |
| sea_ice_m | -309.70 | -79.30 | -52.80 | 300-340: -309.70 |
| sea_tect_m | -279.70 | -123.20 | -37.00 | 300-340: -279.70 |
| ice_pct | 2.10 | 3.40 | 8.90 |  |
| temp | 9.20 | 11.20 | 13.80 |  |
| co2 | -1.31 | -0.36 | 0.53 |  |
| dry_pct | 19.82 | 23.57 | 32.23 |  |
| inland_pct | 1.22 | 2.77 | 11.08 | 312-500: 1.22 |
| lake_pct | 0.04 | 0.29 | 1.31 | 328-332: 0.17; 356-356: 0.17; 416-416: 0.17; 440-476: 0.04; +1 more |
| lake_max_mkm2 | 0.01 | 0.09 | 1.61 | 432-432: 1.56; 488-488: 1.61 |
| max_elev_km | 4.07 | 6.07 | 8.33 |  |
| trees_pct | 3.58 | 21.04 | 52.98 | 300-312: 3.58; 392-400: 52.98; 432-460: 6.70 |
| npp | 180.60 | 408.80 | 486.50 | 416-424: 180.60 |
| landmasses | 2.00 | 5.00 | 12.00 | 332-332: 2; 468-472: 2 |
| largest_pct | 19.50 | 32.10 | 35.40 | 300-320: 35.40 |

### Seed 108, L6 (run 1db687)

![seed 108 L6](seed108_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.53 | 33.56 | 34.41 |  |
| cont_pct | 38.03 | 39.35 | 40.18 |  |
| cont_km | 34.22 | 34.84 | 35.73 |  |
| plates | 10.00 | 12.00 | 15.00 |  |
| ocean_age | 43.30 | 53.40 | 62.60 |  |
| speed | 3.70 | 4.49 | 5.31 |  |
| sea_level | -124.80 | 76.80 | 170.70 |  |
| sea_ice_m | -171.60 | -27.90 | -1.30 |  |
| sea_tect_m | 38.40 | 98.10 | 178.20 |  |
| ice_pct | 0.10 | 1.90 | 6.50 |  |
| temp | 11.60 | 14.90 | 19.10 |  |
| co2 | -0.57 | 0.38 | 1.15 |  |
| dry_pct | 14.86 | 23.52 | 29.47 |  |
| inland_pct | 1.28 | 5.85 | 15.69 | 304-304: 7.43; 344-496: 1.28 |
| lake_pct | 0.24 | 0.55 | 4.66 | 428-428: 4.66 |
| lake_max_mkm2 | 0.03 | 0.15 | 7.08 | 336-340: 1.01; 368-368: 1.01; 384-388: 1.76; 428-428: 7.08 |
| max_elev_km | 4.35 | 5.09 | 7.86 |  |
| trees_pct | 14.33 | 38.82 | 46.67 |  |
| npp | 219.40 | 346.85 | 406.00 |  |
| landmasses | 3.00 | 5.00 | 9.00 |  |
| largest_pct | 10.70 | 24.40 | 28.40 |  |

## Determinism

Seed 101 L6 re-run to 100 Myr (run 6edc0c) against the sweep's run 32a059: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
