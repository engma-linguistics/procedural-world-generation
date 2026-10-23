# Health sweep 2026-10-23 02:42

Commit 8d02259. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 12.2 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | 4e8e7b | 635 | 132 / 412 | 8.3 | 0 | 0.0 | 0.962 | 0.0 | 0.0 | ok | F: icehouse 4% of the time, outside 5-70% | 3.9 |
| 2 | 6 | 500 | 2151fd | 662 | 140 / 396 | 14.4 | 0 | 3.9 | 0.969 | 9.8 | 0.0 | ok | ok | 21.6 |
| 11 | 6 | 500 | 54fa7e | 653 | 128 / 372 | 7.8 | 0 | 3.9 | 0.97 | 0.0 | 0.0 | F | F: icehouse 96% of the time, outside 5-70% | 96.1 |
| 21 | 6 | 500 | 517235 | 636 | 136 / 404 | 10.2 | 0 | 9.8 | 0.963 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 3199 | 6 | 500 | 6d6d48 | 648 | 132 / 376 | 11.2 | 0 | 5.9 | 0.959 | 0.0 | 0.0 | ok | ok | 15.7 |
| 42 | 6 | 500 | ca2787 | 732 | 116 / 404 | 7.7 | 0 | 0.0 | 0.981 | 0.0 | 0.0 | ok | ok | 47.1 |
| 77 | 6 | 500 | d5a9c6 | 698 | 124 / 416 | 7.0 | 0 | 17.6 | 0.981 | 5.9 | 0.0 | ok | F: icehouse 76% of the time, outside 5-70% | 76.5 |
| 505 | 6 | 500 | 33ed64 | 667 | 132 / 416 | 8.9 | 0 | 3.9 | 0.995 | 3.9 | 0.0 | ok | F: icehouse 100% of the time, outside 5-70% | 100.0 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 34.6 | 40.4 | 33.4 | 11.0 | 68.8 | 4.0 | -63.2 | -2.1 | -58.6 | 0.2 | 15.6 | 0.2 | 20.9 | 4.3 | 0.3 | 0.1 | 3.6 | 34.4 | 309.9 | 9.0 | 17.1 |
| 2 | 6 | 33.2 | 40.2 | 33.7 | 16.0 | 51.9 | 4.7 | 113.7 | -13.5 | 125.0 | 1.1 | 17.1 | 1.1 | 21.3 | 3.6 | 0.4 | 0.1 | 5.1 | 40.1 | 352.7 | 10.0 | 14.0 |
| 11 | 6 | 33.4 | 40.3 | 33.7 | 14.0 | 47.3 | 4.4 | 91.8 | -43.6 | 133.2 | 2.1 | 14.2 | -0.8 | 26.2 | 5.8 | 0.4 | 0.1 | 4.4 | 27.5 | 261.2 | 6.0 | 15.2 |
| 21 | 6 | 33.9 | 40.7 | 33.3 | 14.0 | 50.9 | 4.2 | 122.9 | -3.7 | 127.2 | 0.3 | 16.8 | 0.2 | 23.9 | 4.0 | 0.4 | 0.1 | 5.0 | 27.7 | 337.4 | 8.0 | 16.4 |
| 3199 | 6 | 33.9 | 40.2 | 33.7 | 15.0 | 54.6 | 5.0 | 105.4 | -5.0 | 105.8 | 0.3 | 15.3 | 0.6 | 26.9 | 4.6 | 0.3 | 0.1 | 4.5 | 28.6 | 313.1 | 6.0 | 20.8 |
| 42 | 6 | 33.3 | 40.2 | 33.8 | 10.0 | 59.9 | 4.3 | -41.2 | -19.3 | -4.4 | 1.4 | 16.9 | 1.2 | 21.9 | 3.4 | 0.4 | 0.1 | 6.5 | 36.2 | 345.6 | 7.0 | 14.7 |
| 77 | 6 | 33.7 | 40.8 | 33.5 | 10.0 | 63.0 | 5.2 | -17.5 | -32.6 | 1.4 | 2.3 | 15.9 | 0.7 | 29.4 | 6.1 | 0.5 | 0.2 | 5.4 | 27.2 | 307.1 | 6.0 | 20.9 |
| 505 | 6 | 32.7 | 39.6 | 34.7 | 12.0 | 50.9 | 4.0 | 66.1 | -64.5 | 112.7 | 3.2 | 14.0 | -0.1 | 21.3 | 4.8 | 0.7 | 0.1 | 6.1 | 30.0 | 346.0 | 7.0 | 15.1 |

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

## Top outliers (of 60 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 77 | 6 | giant_lake_frames | run | - | 17.60 | -..5 | 2.52 |
| 21 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 505 | 6 | lake_max_mkm2 | 312-312 | 1 | 5.09 | -..1.0 | 0.851 |
| 11 | 6 | lake_max_mkm2 | 348-348 | 1 | 3.95 | -..1.0 | 0.613 |
| 21 | 6 | lake_max_mkm2 | 500-500 | 1 | 3.83 | -..1.0 | 0.59 |
| 21 | 6 | lake_max_mkm2 | 472-480 | 3 | 3.09 | -..1.0 | 0.467 |
| 3199 | 6 | lake_max_mkm2 | 336-336 | 1 | 3.16 | -..1.0 | 0.45 |
| 77 | 6 | lake_max_mkm2 | 428-432 | 2 | 2.65 | -..1.0 | 0.357 |
| 2 | 6 | lake_max_mkm2 | 300-300 | 1 | 2.30 | -..1.0 | 0.271 |
| 3199 | 6 | lake_max_mkm2 | 348-348 | 1 | 1.94 | -..1.0 | 0.196 |
| 2 | 6 | lake_max_mkm2 | 328-328 | 1 | 1.92 | -..1.0 | 0.191 |
| 21 | 6 | inland_pct | 300-500 | 49 | 0.99 | 8..30 | 0.188 |
| 2 | 6 | inland_pct | 300-500 | 51 | 1.21 | 8..30 | 0.187 |
| 505 | 6 | lake_max_mkm2 | 332-332 | 1 | 1.89 | -..1.0 | 0.186 |
| 3199 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 42 | 6 | inland_pct | 300-500 | 50 | 1.55 | 8..30 | 0.175 |
| 1 | 6 | inland_pct | 300-500 | 51 | 2.00 | 8..30 | 0.165 |
| 11 | 6 | inland_pct | 300-500 | 46 | 1.67 | 8..30 | 0.163 |
| 3199 | 6 | inland_pct | 368-496 | 33 | 1.30 | 8..30 | 0.141 |
| 77 | 6 | lake_max_mkm2 | 472-484 | 3 | 1.63 | -..1.0 | 0.141 |
| 505 | 6 | inland_pct | 320-500 | 44 | 2.35 | 8..30 | 0.141 |
| 77 | 6 | lake_max_mkm2 | 452-452 | 1 | 1.63 | -..1.0 | 0.131 |
| 2 | 6 | sea_ice_m | 492-500 | 3 | -387.30 | -250..- | 0.123 |
| 77 | 6 | lake_max_mkm2 | 324-324 | 1 | 1.52 | -..1.0 | 0.108 |
| 11 | 6 | lake_max_mkm2 | 360-360 | 1 | 1.47 | -..1.0 | 0.098 |
| 3199 | 6 | lake_max_mkm2 | 360-360 | 1 | 1.47 | -..1.0 | 0.098 |
| 77 | 6 | inland_pct | 340-396 | 15 | 1.72 | 8..30 | 0.091 |
| 77 | 6 | inland_pct | 408-500 | 19 | 2.60 | 8..30 | 0.086 |
| 21 | 6 | lake_max_mkm2 | 348-348 | 1 | 1.33 | -..1.0 | 0.069 |
| 3199 | 6 | inland_pct | 304-356 | 11 | 2.77 | 8..30 | 0.068 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run 4e8e7b)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.89 | 34.58 | 35.43 |  |
| cont_pct | 39.81 | 40.39 | 41.24 |  |
| cont_km | 32.81 | 33.39 | 34.20 |  |
| plates | 9.00 | 11.00 | 13.00 |  |
| ocean_age | 56.00 | 68.80 | 73.90 |  |
| speed | 3.32 | 3.96 | 4.52 |  |
| sea_level | -107.70 | -63.20 | 30.80 |  |
| sea_ice_m | -23.00 | -2.10 | -0.00 |  |
| sea_tect_m | -97.50 | -58.60 | 41.20 |  |
| ice_pct | 0.00 | 0.20 | 1.10 |  |
| temp | 11.40 | 15.60 | 19.70 |  |
| co2 | -0.78 | 0.18 | 0.98 |  |
| dry_pct | 16.47 | 20.91 | 25.26 |  |
| inland_pct | 2.00 | 4.28 | 7.90 | 300-500: 2.00 |
| lake_pct | 0.17 | 0.28 | 0.91 | 452-452: 0.17 |
| lake_max_mkm2 | 0.03 | 0.07 | 0.87 |  |
| max_elev_km | 2.84 | 3.65 | 7.65 |  |
| trees_pct | 28.00 | 34.35 | 43.95 |  |
| npp | 213.60 | 309.90 | 344.40 |  |
| landmasses | 3.00 | 9.00 | 16.00 |  |
| largest_pct | 12.90 | 17.10 | 21.90 |  |

### Seed 2, L6 (run 2151fd)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.03 | 33.24 | 34.10 |  |
| cont_pct | 38.93 | 40.25 | 41.34 |  |
| cont_km | 32.65 | 33.69 | 35.03 |  |
| plates | 11.00 | 16.00 | 18.00 |  |
| ocean_age | 41.30 | 51.90 | 58.40 |  |
| speed | 3.08 | 4.69 | 5.53 |  |
| sea_level | -327.70 | 113.70 | 198.80 | 492-500: -327.70 |
| sea_ice_m | -387.30 | -13.50 | -6.40 | 492-500: -387.30 |
| sea_tect_m | 59.60 | 125.00 | 205.60 |  |
| ice_pct | 0.60 | 1.10 | 11.20 | 496-500: 11.20 |
| temp | 7.10 | 17.10 | 21.50 | 492-500: 7.10 |
| co2 | 0.18 | 1.08 | 1.89 |  |
| dry_pct | 14.17 | 21.34 | 30.68 |  |
| inland_pct | 1.21 | 3.58 | 7.52 | 300-500: 1.21 |
| lake_pct | 0.17 | 0.36 | 1.72 | 348-348: 0.18; 372-372: 0.17 |
| lake_max_mkm2 | 0.03 | 0.07 | 2.30 | 300-300: 2.30; 328-328: 1.92 |
| max_elev_km | 4.07 | 5.12 | 8.33 |  |
| trees_pct | 21.31 | 40.11 | 54.37 | 404-424: 54.37 |
| npp | 249.70 | 352.70 | 484.50 |  |
| landmasses | 4.00 | 10.00 | 14.00 |  |
| largest_pct | 8.30 | 14.00 | 29.90 |  |

### Seed 11, L6 (run 54fa7e)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.50 | 33.41 | 34.63 |  |
| cont_pct | 39.06 | 40.27 | 41.24 |  |
| cont_km | 33.29 | 33.69 | 34.97 |  |
| plates | 10.00 | 14.00 | 16.00 |  |
| ocean_age | 39.40 | 47.30 | 74.80 |  |
| speed | 2.11 | 4.44 | 5.46 |  |
| sea_level | -155.90 | 91.80 | 175.70 |  |
| sea_ice_m | -67.70 | -43.60 | -19.60 |  |
| sea_tect_m | -113.70 | 133.20 | 207.60 |  |
| ice_pct | 1.40 | 2.10 | 3.20 |  |
| temp | 11.50 | 14.20 | 19.30 |  |
| co2 | -2.40 | -0.76 | 0.56 |  |
| dry_pct | 20.44 | 26.23 | 33.80 |  |
| inland_pct | 1.67 | 5.84 | 13.79 | 300-500: 1.67 |
| lake_pct | 0.16 | 0.42 | 2.84 | 396-396: 0.16; 420-420: 0.17; 432-432: 0.19 |
| lake_max_mkm2 | 0.04 | 0.10 | 3.95 | 348-348: 3.95; 360-360: 1.47 |
| max_elev_km | 3.78 | 4.36 | 8.32 |  |
| trees_pct | 19.80 | 27.47 | 45.01 |  |
| npp | 216.90 | 261.20 | 324.60 |  |
| landmasses | 2.00 | 6.00 | 13.00 | 324-328: 2; 340-344: 2 |
| largest_pct | 13.80 | 15.20 | 30.80 |  |

### Seed 21, L6 (run 517235)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.79 | 33.91 | 34.70 |  |
| cont_pct | 39.31 | 40.67 | 41.07 |  |
| cont_km | 32.85 | 33.34 | 34.40 |  |
| plates | 8.00 | 14.00 | 17.00 |  |
| ocean_age | 34.90 | 50.90 | 79.60 |  |
| speed | 3.40 | 4.15 | 5.14 |  |
| sea_level | -147.80 | 122.90 | 238.20 |  |
| sea_ice_m | -18.60 | -3.70 | -0.00 |  |
| sea_tect_m | -133.50 | 127.20 | 243.40 |  |
| ice_pct | 0.00 | 0.30 | 1.10 |  |
| temp | 12.80 | 16.80 | 23.00 |  |
| co2 | -0.74 | 0.16 | 0.75 |  |
| dry_pct | 18.03 | 23.87 | 28.71 |  |
| inland_pct | 0.99 | 3.95 | 8.64 | 300-500: 0.99 |
| lake_pct | 0.11 | 0.41 | 2.60 | 388-388: 0.15; 408-420: 0.11 |
| lake_max_mkm2 | 0.01 | 0.11 | 3.83 | 348-348: 1.33; 472-480: 3.09; 500-500: 3.83 |
| max_elev_km | 4.34 | 4.96 | 7.57 |  |
| trees_pct | 23.51 | 27.72 | 43.79 |  |
| npp | 220.20 | 337.40 | 351.50 |  |
| landmasses | 3.00 | 8.00 | 17.00 |  |
| largest_pct | 14.50 | 16.40 | 34.50 |  |

### Seed 3199, L6 (run 6d6d48)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.49 | 33.87 | 34.84 |  |
| cont_pct | 38.38 | 40.18 | 41.68 |  |
| cont_km | 32.54 | 33.72 | 35.34 |  |
| plates | 9.00 | 15.00 | 17.00 |  |
| ocean_age | 43.80 | 54.60 | 75.60 |  |
| speed | 3.05 | 5.02 | 6.41 |  |
| sea_level | -205.00 | 105.40 | 200.40 |  |
| sea_ice_m | -111.00 | -5.00 | -0.00 |  |
| sea_tect_m | -94.00 | 105.80 | 200.40 |  |
| ice_pct | 0.00 | 0.30 | 5.00 |  |
| temp | 9.10 | 15.30 | 20.30 |  |
| co2 | -0.95 | 0.59 | 1.32 |  |
| dry_pct | 17.28 | 26.86 | 38.10 |  |
| inland_pct | 1.30 | 4.56 | 13.59 | 304-356: 2.77; 368-496: 1.30 |
| lake_pct | 0.12 | 0.30 | 2.30 | 368-416: 0.13; 436-444: 0.12 |
| lake_max_mkm2 | 0.03 | 0.06 | 3.16 | 336-336: 3.16; 348-348: 1.94; 360-360: 1.47 |
| max_elev_km | 2.73 | 4.53 | 8.53 |  |
| trees_pct | 25.08 | 28.59 | 34.20 |  |
| npp | 228.20 | 313.10 | 392.80 |  |
| landmasses | 2.00 | 6.00 | 17.00 | 344-344: 2 |
| largest_pct | 15.60 | 20.80 | 34.70 |  |

### Seed 42, L6 (run ca2787)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.45 | 33.31 | 34.66 |  |
| cont_pct | 39.37 | 40.18 | 41.19 |  |
| cont_km | 33.21 | 33.79 | 34.48 |  |
| plates | 8.00 | 10.00 | 13.00 |  |
| ocean_age | 47.50 | 59.90 | 104.90 |  |
| speed | 3.13 | 4.27 | 5.35 |  |
| sea_level | -306.30 | -41.20 | 43.60 | 300-320: -306.30 |
| sea_ice_m | -51.00 | -19.30 | -5.40 |  |
| sea_tect_m | -292.20 | -4.40 | 64.60 | 300-316: -292.20 |
| ice_pct | 0.50 | 1.40 | 3.80 |  |
| temp | 13.40 | 16.90 | 21.10 |  |
| co2 | -0.24 | 1.21 | 1.78 |  |
| dry_pct | 17.56 | 21.95 | 25.07 |  |
| inland_pct | 1.55 | 3.42 | 8.00 | 300-500: 1.55 |
| lake_pct | 0.26 | 0.45 | 1.50 |  |
| lake_max_mkm2 | 0.03 | 0.12 | 0.95 |  |
| max_elev_km | 4.40 | 6.49 | 8.09 |  |
| trees_pct | 26.73 | 36.23 | 43.65 |  |
| npp | 273.40 | 345.60 | 372.50 |  |
| landmasses | 3.00 | 7.00 | 12.00 |  |
| largest_pct | 9.20 | 14.70 | 30.00 |  |

### Seed 77, L6 (run d5a9c6)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.42 | 33.73 | 34.46 |  |
| cont_pct | 38.25 | 40.77 | 41.54 |  |
| cont_km | 32.68 | 33.53 | 35.07 |  |
| plates | 8.00 | 10.00 | 12.00 |  |
| ocean_age | 52.60 | 63.00 | 75.60 |  |
| speed | 3.16 | 5.22 | 6.43 |  |
| sea_level | -322.50 | -17.50 | 90.80 | 300-320: -322.50 |
| sea_ice_m | -162.50 | -32.60 | -10.90 |  |
| sea_tect_m | -159.90 | 1.40 | 115.50 |  |
| ice_pct | 0.70 | 2.30 | 6.50 |  |
| temp | 12.80 | 15.90 | 19.80 |  |
| co2 | -1.10 | 0.70 | 1.79 |  |
| dry_pct | 18.83 | 29.42 | 42.63 |  |
| inland_pct | 1.72 | 6.10 | 15.32 | 300-304: 6.04; 328-328: 6.10; 340-396: 1.72; 408-500: 2.60 |
| lake_pct | 0.12 | 0.53 | 2.22 | 316-328: 0.12 |
| lake_max_mkm2 | 0.03 | 0.17 | 2.65 | 308-308: 1.13; 324-324: 1.52; 428-432: 2.65; 452-452: 1.63; +2 more |
| max_elev_km | 3.63 | 5.42 | 7.82 |  |
| trees_pct | 18.35 | 27.18 | 31.96 |  |
| npp | 255.00 | 307.10 | 326.80 |  |
| landmasses | 3.00 | 6.00 | 9.00 |  |
| largest_pct | 14.30 | 20.90 | 34.60 |  |

### Seed 505, L6 (run 33ed64)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.97 | 32.66 | 35.24 |  |
| cont_pct | 38.31 | 39.65 | 41.43 |  |
| cont_km | 33.63 | 34.68 | 35.37 |  |
| plates | 8.00 | 12.00 | 14.00 |  |
| ocean_age | 41.20 | 50.90 | 83.50 |  |
| speed | 2.59 | 3.98 | 5.96 |  |
| sea_level | -393.90 | 66.10 | 101.10 | 496-500: -393.90 |
| sea_ice_m | -255.50 | -64.50 | -31.60 | 500-500: -255.50 |
| sea_tect_m | -138.40 | 112.70 | 179.40 |  |
| ice_pct | 1.80 | 3.20 | 8.30 |  |
| temp | 8.80 | 14.00 | 17.70 |  |
| co2 | -1.49 | -0.12 | 0.87 |  |
| dry_pct | 18.57 | 21.29 | 28.04 |  |
| inland_pct | 2.35 | 4.85 | 20.05 | 300-304: 7.29; 320-500: 2.35 |
| lake_pct | 0.30 | 0.67 | 3.74 | 312-312: 3.74 |
| lake_max_mkm2 | 0.04 | 0.14 | 5.09 | 312-312: 5.09; 332-332: 1.89 |
| max_elev_km | 5.00 | 6.08 | 7.01 |  |
| trees_pct | 21.27 | 30.00 | 46.48 |  |
| npp | 199.20 | 346.05 | 366.50 | 432-432: 199.20 |
| landmasses | 4.00 | 7.00 | 10.00 |  |
| largest_pct | 10.00 | 15.10 | 33.30 |  |

## Determinism

Seed 1 L6 re-run to 100 Myr (run cf232f) against the sweep's run 4e8e7b: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
