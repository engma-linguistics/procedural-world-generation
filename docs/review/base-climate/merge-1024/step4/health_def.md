# Health sweep 2026-10-23 13:26

Commit 555883d. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 11.6 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | df3ee5 | 626 | 132 / 412 | 14.3 | 0 | 3.9 | 0.977 | 0.0 | 0.0 | ok | ok | 47.1 |
| 2 | 6 | 500 | ffe554 | 628 | 140 / 396 | 12.9 | 0 | 33.3 | 0.955 | 3.9 | 0.0 | ok | ok | 17.6 |
| 11 | 6 | 500 | 94578f | 680 | 128 / 372 | 9.8 | 0 | 0.0 | 0.953 | 0.0 | 0.0 | F | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 21 | 6 | 500 | a97a70 | 662 | 136 / 404 | 5.7 | 0 | 7.8 | 0.942 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 3199 | 6 | 500 | db671f | 677 | 132 / 376 | 7.5 | 0 | 7.8 | 0.973 | 0.0 | 0.0 | ok | ok | 23.5 |
| 42 | 6 | 500 | ced491 | 698 | 116 / 404 | 10.7 | 0 | 2.0 | 0.999 | 31.4 | 0.0 | ok | ok | 68.6 |
| 77 | 6 | 500 | bf811e | 655 | 124 / 416 | 7.7 | 0 | 0.0 | 0.956 | 0.0 | 0.0 | ok | ok | 62.7 |
| 505 | 6 | 500 | d1aeb2 | 684 | 132 / 416 | 8.5 | 0 | 9.8 | 0.973 | 0.0 | 0.0 | ok | ok | 47.1 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 35.0 | 39.8 | 34.4 | 11.0 | 59.6 | 4.2 | 10.0 | -4.2 | 32.0 | 0.3 | 16.2 | -0.1 | 26.1 | 5.5 | 0.4 | 0.1 | 4.7 | 34.0 | 270.8 | 7.0 | 23.8 |
| 2 | 6 | 32.3 | 41.2 | 32.7 | 13.0 | 46.8 | 4.0 | 143.8 | -3.8 | 144.9 | 0.3 | 16.9 | 0.6 | 18.8 | 3.0 | 0.5 | 0.2 | 4.0 | 38.1 | 372.6 | 10.0 | 18.7 |
| 11 | 6 | 32.8 | 40.6 | 33.1 | 15.0 | 47.5 | 3.6 | 166.2 | -2.9 | 166.3 | 0.2 | 16.3 | 0.0 | 25.0 | 4.0 | 0.3 | 0.1 | 4.3 | 25.1 | 296.0 | 9.0 | 16.5 |
| 21 | 6 | 33.3 | 41.7 | 32.6 | 11.0 | 60.0 | 4.8 | 36.6 | -4.1 | 48.4 | 0.3 | 19.0 | 0.7 | 26.2 | 4.7 | 0.5 | 0.1 | 5.0 | 35.1 | 371.9 | 8.0 | 24.0 |
| 3199 | 6 | 33.3 | 40.1 | 33.9 | 14.0 | 49.5 | 4.6 | 90.1 | -10.0 | 109.3 | 0.9 | 17.8 | 0.8 | 22.5 | 5.4 | 0.5 | 0.1 | 5.3 | 40.1 | 354.3 | 8.0 | 18.8 |
| 42 | 6 | 33.7 | 40.7 | 33.9 | 12.0 | 57.6 | 4.0 | -67.8 | -25.9 | 3.9 | 1.7 | 16.0 | 0.4 | 17.7 | 4.3 | 0.4 | 0.1 | 4.5 | 39.5 | 409.1 | 9.0 | 16.3 |
| 77 | 6 | 32.4 | 40.7 | 33.4 | 14.0 | 51.1 | 4.3 | 121.0 | -25.2 | 148.6 | 1.7 | 16.6 | 0.4 | 21.1 | 3.0 | 0.4 | 0.1 | 5.1 | 34.0 | 369.9 | 6.0 | 28.8 |
| 505 | 6 | 33.8 | 40.4 | 33.7 | 9.0 | 62.7 | 5.0 | -41.1 | -19.4 | -12.3 | 1.8 | 14.9 | -0.1 | 26.1 | 5.1 | 0.6 | 0.2 | 6.0 | 28.9 | 218.4 | 6.0 | 28.8 |

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

## Top outliers (of 61 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 2 | 6 | giant_lake_frames | run | - | 33.30 | -..5 | 5.66 |
| 42 | 6 | sea_ice_below_150 | run | - | 31.40 | -..10 | 2.14 |
| 3199 | 6 | lake_max_mkm2 | 372-376 | 2 | 9.23 | -..1.0 | 1.776 |
| 505 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 21 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 3199 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 2 | 6 | lake_max_mkm2 | 468-500 | 9 | 2.23 | -..1.0 | 0.334 |
| 2 | 6 | lake_max_mkm2 | 400-416 | 5 | 2.15 | -..1.0 | 0.277 |
| 21 | 6 | lake_max_mkm2 | 388-392 | 2 | 2.15 | -..1.0 | 0.249 |
| 42 | 6 | sea_ice_m | 444-484 | 11 | -423.10 | -250..- | 0.199 |
| 3199 | 6 | lake_pct | 372-372 | 1 | 5.66 | 0.2..3.0 | 0.198 |
| 77 | 6 | inland_pct | 300-500 | 49 | 1.01 | 8..30 | 0.187 |
| 42 | 6 | inland_pct | 300-500 | 49 | 1.25 | 8..30 | 0.181 |
| 11 | 6 | inland_pct | 300-500 | 51 | 1.57 | 8..30 | 0.177 |
| 21 | 6 | inland_pct | 340-500 | 39 | 1.07 | 8..30 | 0.161 |
| 1 | 6 | inland_pct | 332-488 | 36 | 1.94 | 8..30 | 0.134 |
| 2 | 6 | inland_pct | 300-400 | 26 | 0.93 | 8..30 | 0.131 |
| 505 | 6 | lake_max_mkm2 | 416-428 | 3 | 1.58 | -..1.0 | 0.13 |
| 3199 | 6 | inland_pct | 376-500 | 30 | 2.08 | 8..30 | 0.118 |
| 2 | 6 | lake_max_mkm2 | 444-452 | 3 | 1.52 | -..1.0 | 0.116 |
| 505 | 6 | lake_max_mkm2 | 304-304 | 1 | 1.56 | -..1.0 | 0.116 |
| 505 | 6 | inland_pct | 312-412 | 23 | 1.71 | 8..30 | 0.109 |
| 2 | 6 | inland_pct | 420-472 | 13 | 1.42 | 8..30 | 0.091 |
| 3199 | 6 | lake_max_mkm2 | 300-308 | 2 | 1.38 | -..1.0 | 0.082 |
| 505 | 6 | inland_pct | 424-500 | 16 | 2.62 | 8..30 | 0.08 |
| 21 | 6 | trees_pct | 392-416 | 7 | 59.98 | 10..50 | 0.064 |
| 21 | 6 | inland_pct | 300-324 | 7 | 2.79 | 8..30 | 0.061 |
| 42 | 6 | sea_level | 448-476 | 8 | -378.20 | -250..300 | 0.061 |
| 505 | 6 | trees_pct | 448-480 | 9 | 1.53 | 10..50 | 0.057 |
| 42 | 6 | ice_pct | 448-468 | 6 | 12.10 | -..10 | 0.052 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run df3ee5)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 34.15 | 34.98 | 35.35 |  |
| cont_pct | 39.07 | 39.80 | 40.91 |  |
| cont_km | 33.53 | 34.40 | 35.00 |  |
| plates | 9.00 | 11.00 | 14.00 |  |
| ocean_age | 42.80 | 59.60 | 71.60 |  |
| speed | 3.21 | 4.20 | 5.48 |  |
| sea_level | -180.90 | 10.00 | 147.80 |  |
| sea_ice_m | -99.80 | -4.20 | -0.00 |  |
| sea_tect_m | -86.90 | 32.00 | 147.80 |  |
| ice_pct | 0.00 | 0.30 | 3.80 |  |
| temp | 7.60 | 16.20 | 21.90 | 496-500: 7.60 |
| co2 | -0.54 | -0.06 | 1.61 |  |
| dry_pct | 21.33 | 26.07 | 32.45 |  |
| inland_pct | 1.94 | 5.48 | 13.23 | 304-320: 3.56; 332-488: 1.94; 500-500: 7.88 |
| lake_pct | 0.16 | 0.39 | 1.11 | 364-364: 0.16; 392-392: 0.20 |
| lake_max_mkm2 | 0.01 | 0.10 | 1.10 | 324-324: 1.08; 360-360: 1.10 |
| max_elev_km | 4.07 | 4.66 | 6.27 |  |
| trees_pct | 21.42 | 33.99 | 42.59 |  |
| npp | 137.80 | 270.80 | 344.00 | 412-424: 137.80 |
| landmasses | 4.00 | 7.00 | 13.00 |  |
| largest_pct | 14.50 | 23.80 | 32.30 |  |

### Seed 2, L6 (run ffe554)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.91 | 32.31 | 33.42 |  |
| cont_pct | 40.65 | 41.18 | 41.68 |  |
| cont_km | 32.36 | 32.69 | 33.27 |  |
| plates | 10.00 | 13.00 | 17.00 |  |
| ocean_age | 38.50 | 46.80 | 67.30 |  |
| speed | 2.88 | 3.98 | 5.31 |  |
| sea_level | -170.60 | 143.80 | 218.50 |  |
| sea_ice_m | -175.60 | -3.80 | -0.00 |  |
| sea_tect_m | -26.30 | 144.90 | 222.10 |  |
| ice_pct | 0.00 | 0.30 | 6.00 |  |
| temp | 9.60 | 16.90 | 22.50 |  |
| co2 | -0.17 | 0.59 | 2.08 |  |
| dry_pct | 13.59 | 18.75 | 23.43 |  |
| inland_pct | 0.93 | 2.99 | 13.36 | 300-400: 0.93; 420-472: 1.42; 484-500: 3.40 |
| lake_pct | 0.15 | 0.52 | 2.88 | 336-344: 0.15 |
| lake_max_mkm2 | 0.03 | 0.19 | 2.23 | 400-416: 2.15; 444-452: 1.52; 468-500: 2.23 |
| max_elev_km | 2.97 | 4.03 | 6.80 |  |
| trees_pct | 26.37 | 38.13 | 54.10 | 380-420: 54.10 |
| npp | 296.00 | 372.60 | 517.90 |  |
| landmasses | 6.00 | 10.00 | 13.00 |  |
| largest_pct | 9.40 | 18.70 | 28.90 |  |

### Seed 11, L6 (run 94578f)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.55 | 32.83 | 33.39 |  |
| cont_pct | 39.94 | 40.62 | 41.13 |  |
| cont_km | 32.66 | 33.09 | 33.52 |  |
| plates | 12.00 | 15.00 | 19.00 |  |
| ocean_age | 34.40 | 47.50 | 58.70 |  |
| speed | 2.88 | 3.63 | 4.93 |  |
| sea_level | 52.40 | 166.20 | 249.50 |  |
| sea_ice_m | -8.90 | -2.90 | -0.10 |  |
| sea_tect_m | 54.10 | 166.30 | 252.90 |  |
| ice_pct | 0.00 | 0.20 | 0.70 |  |
| temp | 12.60 | 16.30 | 22.40 |  |
| co2 | -0.67 | 0.01 | 0.59 |  |
| dry_pct | 21.87 | 25.04 | 35.52 |  |
| inland_pct | 1.57 | 4.05 | 7.92 | 300-500: 1.57 |
| lake_pct | 0.12 | 0.30 | 1.07 | 308-308: 0.19; 468-484: 0.12; 496-496: 0.20 |
| lake_max_mkm2 | 0.03 | 0.07 | 0.95 |  |
| max_elev_km | 3.43 | 4.27 | 8.23 |  |
| trees_pct | 7.60 | 25.11 | 51.36 | 300-320: 7.60; 396-404: 51.36 |
| npp | 192.40 | 296.00 | 345.40 | 372-372: 192.40 |
| landmasses | 5.00 | 9.00 | 15.00 |  |
| largest_pct | 14.80 | 16.50 | 19.60 |  |

### Seed 21, L6 (run a97a70)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.81 | 33.29 | 36.74 |  |
| cont_pct | 39.01 | 41.68 | 42.51 |  |
| cont_km | 31.60 | 32.59 | 33.79 |  |
| plates | 8.00 | 11.00 | 16.00 |  |
| ocean_age | 41.60 | 60.00 | 94.10 |  |
| speed | 2.59 | 4.80 | 5.45 |  |
| sea_level | -248.30 | 36.60 | 181.10 |  |
| sea_ice_m | -13.30 | -4.10 | -0.00 |  |
| sea_tect_m | -248.30 | 48.40 | 185.20 |  |
| ice_pct | 0.00 | 0.30 | 1.20 |  |
| temp | 16.10 | 19.00 | 21.80 |  |
| co2 | -0.80 | 0.70 | 1.09 |  |
| dry_pct | 15.72 | 26.23 | 38.19 |  |
| inland_pct | 1.07 | 4.65 | 11.95 | 300-324: 2.79; 340-500: 1.07 |
| lake_pct | 0.16 | 0.46 | 2.25 | 344-344: 0.16 |
| lake_max_mkm2 | 0.03 | 0.12 | 2.15 | 388-392: 2.15; 424-428: 1.17 |
| max_elev_km | 3.78 | 5.05 | 8.18 |  |
| trees_pct | 8.13 | 35.07 | 59.98 | 300-300: 8.13; 392-416: 59.98 |
| npp | 310.00 | 371.90 | 404.20 |  |
| landmasses | 2.00 | 8.00 | 18.00 | 448-464: 2 |
| largest_pct | 8.20 | 24.00 | 36.50 | 300-300: 36.50 |

### Seed 3199, L6 (run db671f)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.50 | 33.32 | 34.15 |  |
| cont_pct | 38.60 | 40.09 | 40.55 |  |
| cont_km | 33.53 | 33.88 | 35.10 |  |
| plates | 12.00 | 14.00 | 16.00 |  |
| ocean_age | 44.50 | 49.50 | 55.70 |  |
| speed | 3.93 | 4.56 | 5.71 |  |
| sea_level | 3.10 | 90.10 | 168.40 |  |
| sea_ice_m | -36.20 | -10.00 | -0.10 |  |
| sea_tect_m | 9.40 | 109.30 | 179.20 |  |
| ice_pct | 0.00 | 0.90 | 1.80 |  |
| temp | 13.10 | 17.80 | 20.60 |  |
| co2 | 0.21 | 0.80 | 1.58 |  |
| dry_pct | 15.69 | 22.52 | 35.70 |  |
| inland_pct | 2.08 | 5.36 | 15.51 | 312-320: 5.36; 336-364: 4.31; 376-500: 2.08 |
| lake_pct | 0.17 | 0.49 | 5.66 | 336-336: 0.17; 372-372: 5.66 |
| lake_max_mkm2 | 0.03 | 0.12 | 9.23 | 300-308: 1.38; 372-376: 9.23 |
| max_elev_km | 3.74 | 5.27 | 8.36 |  |
| trees_pct | 26.83 | 40.12 | 44.98 |  |
| npp | 309.20 | 354.30 | 419.60 |  |
| landmasses | 5.00 | 8.00 | 16.00 |  |
| largest_pct | 9.80 | 18.80 | 26.30 |  |

### Seed 42, L6 (run ced491)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.73 | 33.68 | 34.64 |  |
| cont_pct | 37.18 | 40.73 | 42.89 |  |
| cont_km | 32.70 | 33.87 | 36.24 |  |
| plates | 10.00 | 12.00 | 13.00 |  |
| ocean_age | 50.10 | 57.60 | 64.00 |  |
| speed | 3.08 | 4.00 | 5.05 |  |
| sea_level | -378.20 | -67.80 | 50.80 | 448-476: -378.20 |
| sea_ice_m | -423.10 | -25.90 | -10.00 | 444-484: -423.10 |
| sea_tect_m | -58.40 | 3.90 | 73.90 |  |
| ice_pct | 0.70 | 1.70 | 12.10 | 448-468: 12.10 |
| temp | 9.40 | 16.00 | 20.10 |  |
| co2 | -0.42 | 0.42 | 0.93 |  |
| dry_pct | 12.71 | 17.72 | 27.27 |  |
| inland_pct | 1.25 | 4.30 | 8.98 | 300-500: 1.25 |
| lake_pct | 0.23 | 0.45 | 1.33 |  |
| lake_max_mkm2 | 0.03 | 0.10 | 1.02 | 464-464: 1.02 |
| max_elev_km | 3.62 | 4.46 | 9.00 |  |
| trees_pct | 23.45 | 39.49 | 48.80 |  |
| npp | 336.30 | 409.10 | 518.90 |  |
| landmasses | 5.00 | 9.00 | 14.00 |  |
| largest_pct | 9.10 | 16.30 | 26.70 |  |

### Seed 77, L6 (run bf811e)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.49 | 32.36 | 33.47 |  |
| cont_pct | 38.85 | 40.66 | 41.68 |  |
| cont_km | 32.33 | 33.37 | 34.85 |  |
| plates | 12.00 | 14.00 | 16.00 |  |
| ocean_age | 44.80 | 51.10 | 54.90 |  |
| speed | 2.76 | 4.33 | 6.13 |  |
| sea_level | 91.00 | 121.00 | 156.90 |  |
| sea_ice_m | -52.30 | -25.20 | -0.00 |  |
| sea_tect_m | 102.10 | 148.60 | 182.60 |  |
| ice_pct | 0.00 | 1.70 | 4.00 |  |
| temp | 12.10 | 16.60 | 19.80 |  |
| co2 | -0.17 | 0.44 | 1.32 |  |
| dry_pct | 17.64 | 21.14 | 29.04 |  |
| inland_pct | 1.01 | 3.00 | 8.98 | 300-500: 1.01 |
| lake_pct | 0.12 | 0.43 | 1.00 | 472-500: 0.12 |
| lake_max_mkm2 | 0.01 | 0.06 | 0.51 |  |
| max_elev_km | 2.91 | 5.13 | 6.58 |  |
| trees_pct | 27.24 | 34.03 | 41.66 |  |
| npp | 237.80 | 369.95 | 418.00 |  |
| landmasses | 3.00 | 6.00 | 10.00 |  |
| largest_pct | 15.90 | 28.80 | 33.40 |  |

### Seed 505, L6 (run d1aeb2)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.43 | 33.82 | 34.98 |  |
| cont_pct | 37.92 | 40.36 | 41.27 |  |
| cont_km | 33.27 | 33.71 | 35.75 |  |
| plates | 5.00 | 9.00 | 12.00 |  |
| ocean_age | 51.60 | 62.70 | 70.70 |  |
| speed | 3.54 | 4.95 | 5.48 |  |
| sea_level | -110.20 | -41.10 | 74.60 |  |
| sea_ice_m | -131.60 | -19.40 | -5.60 |  |
| sea_tect_m | -92.70 | -12.30 | 98.10 |  |
| ice_pct | 0.40 | 1.80 | 5.60 |  |
| temp | 10.90 | 14.90 | 19.40 |  |
| co2 | -1.06 | -0.08 | 0.97 |  |
| dry_pct | 16.21 | 26.12 | 31.78 |  |
| inland_pct | 1.71 | 5.11 | 14.22 | 300-300: 4.59; 312-412: 1.71; 424-500: 2.62 |
| lake_pct | 0.28 | 0.56 | 2.07 |  |
| lake_max_mkm2 | 0.04 | 0.16 | 1.58 | 304-304: 1.56; 316-316: 1.23; 416-428: 1.58 |
| max_elev_km | 5.46 | 5.98 | 8.05 |  |
| trees_pct | 1.53 | 28.94 | 47.41 | 448-480: 1.53 |
| npp | 109.70 | 218.40 | 365.10 | 416-444: 109.70; 464-464: 198.50 |
| landmasses | 3.00 | 6.00 | 14.00 |  |
| largest_pct | 22.00 | 28.80 | 34.20 |  |

## Determinism

Seed 1 L6 re-run to 100 Myr (run d237e7) against the sweep's run df3ee5: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
