# Health sweep 2026-10-23 13:00

Commit c13b567. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 10.8 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | a47d91 | 619 | 132 / 412 | 7.8 | 0 | 13.7 | 0.985 | 0.0 | 0.0 | ok | ok | 27.5 |
| 2 | 6 | 500 | 04b3a6 | 587 | 140 / 396 | 15.8 | 0 | 17.6 | 0.982 | 5.9 | 0.0 | ok | ok | 7.8 |
| 11 | 6 | 500 | 5dbdb6 | 633 | 128 / 372 | 5.2 | 0 | 5.9 | 0.967 | 0.0 | 0.0 | F | ok | 49.0 |
| 21 | 6 | 500 | 27e5fc | 613 | 136 / 404 | 12.9 | 0 | 3.9 | 0.985 | 25.5 | 0.0 | ok | ok | 66.7 |
| 3199 | 6 | 500 | a8c2c8 | 576 | 132 / 376 | 6.2 | 0 | 7.8 | 0.956 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 42 | 6 | 500 | b61d37 | 589 | 116 / 404 | 11.7 | 0 | 21.6 | 0.952 | 5.9 | 0.0 | ok | ok | 52.9 |
| 77 | 6 | 500 | 604c34 | 625 | 124 / 416 | 11.6 | 0 | 3.9 | 0.951 | 0.0 | 0.0 | ok | ok | 21.6 |
| 505 | 6 | 500 | 65ad3f | 644 | 132 / 416 | 11.5 | 0 | 11.8 | 0.964 | 23.5 | 0.0 | ok | ok | 33.3 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 33.4 | 39.9 | 34.1 | 10.0 | 55.6 | 4.2 | 17.3 | -12.7 | 41.3 | 1.2 | 17.0 | 0.5 | 21.7 | 4.3 | 0.6 | 0.1 | 6.6 | 39.5 | 372.6 | 6.0 | 14.5 |
| 2 | 6 | 34.0 | 39.3 | 34.8 | 14.0 | 50.2 | 5.1 | 111.3 | -5.4 | 117.1 | 0.4 | 20.2 | 1.0 | 30.5 | 6.7 | 0.4 | 0.1 | 6.8 | 36.1 | 360.0 | 7.0 | 23.1 |
| 11 | 6 | 33.1 | 40.0 | 33.9 | 12.0 | 56.9 | 3.9 | 33.8 | -19.7 | 65.8 | 1.7 | 16.9 | 0.2 | 23.3 | 4.2 | 0.6 | 0.1 | 6.8 | 33.5 | 311.5 | 9.0 | 18.9 |
| 21 | 6 | 32.2 | 39.8 | 34.4 | 15.0 | 48.5 | 4.5 | 119.3 | -29.7 | 148.8 | 2.0 | 14.7 | -0.1 | 20.8 | 3.3 | 0.5 | 0.1 | 6.0 | 24.5 | 283.5 | 13.0 | 13.3 |
| 3199 | 6 | 33.7 | 39.8 | 34.0 | 9.0 | 57.9 | 4.7 | 17.5 | -6.6 | 33.6 | 0.5 | 15.5 | 0.3 | 24.1 | 5.6 | 0.5 | 0.2 | 6.0 | 30.0 | 322.0 | 8.0 | 17.8 |
| 42 | 6 | 33.6 | 40.0 | 33.5 | 11.0 | 65.0 | 4.0 | -64.9 | -34.7 | -25.6 | 1.8 | 14.9 | 0.5 | 18.4 | 4.3 | 0.7 | 0.1 | 5.5 | 37.4 | 386.6 | 5.0 | 24.0 |
| 77 | 6 | 32.4 | 40.4 | 33.1 | 14.0 | 48.2 | 4.3 | 118.3 | -8.3 | 141.3 | 0.7 | 16.1 | -0.1 | 20.3 | 3.1 | 0.5 | 0.1 | 5.9 | 30.8 | 316.9 | 7.0 | 17.4 |
| 505 | 6 | 34.0 | 40.3 | 33.7 | 9.0 | 57.9 | 4.5 | 21.4 | -7.0 | 30.4 | 0.6 | 16.0 | 0.3 | 31.4 | 5.8 | 0.5 | 0.1 | 5.2 | 30.9 | 318.4 | 7.0 | 31.0 |

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

## Top outliers (of 99 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 42 | 6 | giant_lake_frames | run | - | 21.60 | -..5 | 3.32 |
| 2 | 6 | giant_lake_frames | run | - | 17.60 | -..5 | 2.52 |
| 1 | 6 | lake_max_mkm2 | 500-500 | 1 | 13.10 | -..1.0 | 2.516 |
| 1 | 6 | giant_lake_frames | run | - | 13.70 | -..5 | 1.74 |
| 21 | 6 | sea_ice_below_150 | run | - | 25.50 | -..10 | 1.55 |
| 505 | 6 | giant_lake_frames | run | - | 11.80 | -..5 | 1.36 |
| 505 | 6 | sea_ice_below_150 | run | - | 23.50 | -..10 | 1.35 |
| 1 | 6 | lake_max_mkm2 | 392-400 | 2 | 5.67 | -..1.0 | 1.007 |
| 21 | 6 | lake_max_mkm2 | 392-392 | 1 | 5.47 | -..1.0 | 0.929 |
| 42 | 6 | lake_max_mkm2 | 416-424 | 3 | 4.62 | -..1.0 | 0.81 |
| 3199 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 1 | 6 | lake_pct | 500-500 | 1 | 8.31 | 0.2..3.0 | 0.394 |
| 2 | 6 | lake_max_mkm2 | 372-372 | 1 | 2.83 | -..1.0 | 0.38 |
| 505 | 6 | lake_max_mkm2 | 424-428 | 2 | 2.52 | -..1.0 | 0.327 |
| 3199 | 6 | lake_max_mkm2 | 436-436 | 1 | 2.43 | -..1.0 | 0.297 |
| 505 | 6 | lake_max_mkm2 | 440-444 | 2 | 2.19 | -..1.0 | 0.257 |
| 505 | 6 | sea_level | 300-352 | 14 | -672.60 | -250..300 | 0.239 |
| 77 | 6 | lake_max_mkm2 | 444-444 | 1 | 2.14 | -..1.0 | 0.237 |
| 505 | 6 | sea_ice_m | 300-332 | 9 | -445.00 | -250..- | 0.212 |
| 21 | 6 | inland_pct | 300-500 | 49 | 0.66 | 8..30 | 0.196 |
| 2 | 6 | lake_max_mkm2 | 332-348 | 4 | 1.82 | -..1.0 | 0.19 |
| 3199 | 6 | lake_max_mkm2 | 316-316 | 1 | 1.91 | -..1.0 | 0.188 |
| 77 | 6 | inland_pct | 304-500 | 49 | 0.96 | 8..30 | 0.188 |
| 11 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 1 | 6 | inland_pct | 300-496 | 47 | 1.35 | 8..30 | 0.173 |
| 11 | 6 | inland_pct | 300-500 | 51 | 1.70 | 8..30 | 0.173 |
| 42 | 6 | lake_max_mkm2 | 480-500 | 5 | 1.67 | -..1.0 | 0.16 |
| 42 | 6 | inland_pct | 316-464 | 36 | 1.24 | 8..30 | 0.149 |
| 1 | 6 | lake_max_mkm2 | 372-376 | 2 | 1.67 | -..1.0 | 0.144 |
| 2 | 6 | lake_max_mkm2 | 476-476 | 1 | 1.61 | -..1.0 | 0.126 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run a47d91)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.46 | 33.42 | 34.24 |  |
| cont_pct | 39.23 | 39.85 | 41.12 |  |
| cont_km | 33.53 | 34.10 | 34.57 |  |
| plates | 8.00 | 10.00 | 15.00 |  |
| ocean_age | 45.50 | 55.60 | 61.90 |  |
| speed | 3.21 | 4.15 | 4.63 |  |
| sea_level | -76.20 | 17.30 | 106.20 |  |
| sea_ice_m | -105.10 | -12.70 | -3.50 |  |
| sea_tect_m | -18.20 | 41.30 | 117.00 |  |
| ice_pct | 0.30 | 1.20 | 3.60 |  |
| temp | 12.70 | 17.00 | 20.50 |  |
| co2 | -0.24 | 0.54 | 1.21 |  |
| dry_pct | 13.13 | 21.73 | 30.27 |  |
| inland_pct | 1.35 | 4.29 | 17.41 | 300-496: 1.35 |
| lake_pct | 0.16 | 0.56 | 8.31 | 384-392: 3.75; 500-500: 8.31 |
| lake_max_mkm2 | 0.03 | 0.10 | 13.10 | 300-300: 1.07; 324-324: 1.27; 372-376: 1.67; 392-400: 5.67; +1 more |
| max_elev_km | 4.22 | 6.60 | 8.14 |  |
| trees_pct | 26.95 | 39.55 | 55.80 | 420-472: 55.80 |
| npp | 249.70 | 372.60 | 398.10 |  |
| landmasses | 3.00 | 6.00 | 12.00 |  |
| largest_pct | 11.10 | 14.50 | 21.60 |  |

### Seed 2, L6 (run 04b3a6)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.83 | 34.04 | 34.89 |  |
| cont_pct | 37.90 | 39.34 | 39.84 |  |
| cont_km | 34.40 | 34.79 | 35.72 |  |
| plates | 11.00 | 14.00 | 17.00 |  |
| ocean_age | 46.50 | 50.20 | 56.70 |  |
| speed | 4.36 | 5.12 | 6.17 |  |
| sea_level | -285.40 | 111.30 | 131.40 | 496-500: -285.40 |
| sea_ice_m | -348.90 | -5.40 | -0.00 | 492-500: -348.90 |
| sea_tect_m | 22.80 | 117.10 | 134.20 |  |
| ice_pct | 0.00 | 0.40 | 9.90 |  |
| temp | 7.00 | 20.20 | 22.80 | 492-500: 7.00 |
| co2 | 0.17 | 1.02 | 1.81 |  |
| dry_pct | 14.60 | 30.46 | 36.53 |  |
| inland_pct | 1.35 | 6.65 | 18.47 | 308-308: 7.01; 324-324: 6.41; 344-344: 7.95; 360-364: 6.65; +2 more |
| lake_pct | 0.17 | 0.36 | 2.77 | 368-368: 0.18; 380-380: 0.20; 392-392: 0.18; 440-440: 0.17 |
| lake_max_mkm2 | 0.03 | 0.09 | 2.83 | 316-316: 1.37; 332-348: 1.82; 372-372: 2.83; 476-476: 1.61; +1 more |
| max_elev_km | 4.10 | 6.85 | 8.38 |  |
| trees_pct | 21.93 | 36.13 | 52.95 | 416-424: 52.95 |
| npp | 239.50 | 360.00 | 541.90 |  |
| landmasses | 3.00 | 7.00 | 13.00 |  |
| largest_pct | 14.50 | 23.10 | 31.30 |  |

### Seed 11, L6 (run 5dbdb6)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.46 | 33.10 | 33.69 |  |
| cont_pct | 38.28 | 40.02 | 41.46 |  |
| cont_km | 32.84 | 33.91 | 34.79 |  |
| plates | 10.00 | 12.00 | 16.00 |  |
| ocean_age | 50.40 | 56.90 | 69.90 |  |
| speed | 3.45 | 3.92 | 4.52 |  |
| sea_level | -148.90 | 33.80 | 95.70 |  |
| sea_ice_m | -41.30 | -19.70 | -2.70 |  |
| sea_tect_m | -123.80 | 65.80 | 98.70 |  |
| ice_pct | 0.20 | 1.70 | 2.80 |  |
| temp | 13.40 | 16.90 | 18.60 |  |
| co2 | -1.06 | 0.17 | 0.83 |  |
| dry_pct | 18.98 | 23.30 | 28.39 |  |
| inland_pct | 1.70 | 4.22 | 7.71 | 300-500: 1.70 |
| lake_pct | 0.18 | 0.62 | 1.73 | 428-428: 0.18 |
| lake_max_mkm2 | 0.03 | 0.10 | 1.22 | 328-328: 1.22; 360-360: 1.12; 408-408: 1.02 |
| max_elev_km | 3.85 | 6.82 | 8.35 |  |
| trees_pct | 1.04 | 33.50 | 47.32 | 464-500: 1.04 |
| npp | 265.50 | 311.50 | 381.30 |  |
| landmasses | 5.00 | 9.00 | 13.00 |  |
| largest_pct | 12.50 | 18.90 | 29.40 |  |

### Seed 21, L6 (run 27e5fc)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.39 | 32.22 | 33.37 |  |
| cont_pct | 38.07 | 39.80 | 40.79 |  |
| cont_km | 33.82 | 34.37 | 35.44 |  |
| plates | 8.00 | 15.00 | 19.00 |  |
| ocean_age | 38.40 | 48.50 | 63.00 |  |
| speed | 2.47 | 4.49 | 4.82 |  |
| sea_level | -254.90 | 119.30 | 205.30 | 500-500: -254.90 |
| sea_ice_m | -258.70 | -29.70 | -12.20 | 460-464: -258.70; 484-488: -251.60; 500-500: -255.10 |
| sea_tect_m | 0.10 | 148.80 | 219.40 |  |
| ice_pct | 1.00 | 2.00 | 7.20 |  |
| temp | 9.30 | 14.70 | 22.20 |  |
| co2 | -1.13 | -0.07 | 0.73 |  |
| dry_pct | 17.59 | 20.83 | 31.17 |  |
| inland_pct | 0.66 | 3.34 | 12.64 | 300-500: 0.66 |
| lake_pct | 0.18 | 0.45 | 3.74 | 368-368: 0.18; 392-392: 3.74 |
| lake_max_mkm2 | 0.03 | 0.09 | 5.47 | 392-392: 5.47; 416-416: 1.46 |
| max_elev_km | 4.06 | 6.00 | 8.37 |  |
| trees_pct | 10.31 | 24.51 | 42.28 |  |
| npp | 176.20 | 283.50 | 365.10 | 416-420: 176.20 |
| landmasses | 7.00 | 13.00 | 16.00 |  |
| largest_pct | 9.00 | 13.30 | 30.80 |  |

### Seed 3199, L6 (run a8c2c8)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.85 | 33.71 | 34.93 |  |
| cont_pct | 38.17 | 39.77 | 41.00 |  |
| cont_km | 33.21 | 33.96 | 35.23 |  |
| plates | 6.00 | 9.00 | 14.00 |  |
| ocean_age | 49.30 | 57.90 | 70.50 |  |
| speed | 3.67 | 4.71 | 5.30 |  |
| sea_level | -58.60 | 17.50 | 95.30 |  |
| sea_ice_m | -19.90 | -6.60 | -0.00 |  |
| sea_tect_m | -57.80 | 33.60 | 110.20 |  |
| ice_pct | 0.00 | 0.50 | 1.40 |  |
| temp | 12.90 | 15.50 | 19.10 |  |
| co2 | -0.19 | 0.34 | 0.90 |  |
| dry_pct | 20.71 | 24.13 | 44.48 |  |
| inland_pct | 2.66 | 5.59 | 12.11 | 308-308: 7.77; 320-328: 5.90; 340-408: 3.71; 424-500: 2.66 |
| lake_pct | 0.16 | 0.46 | 2.25 | 340-340: 0.20; 400-400: 0.16 |
| lake_max_mkm2 | 0.01 | 0.17 | 2.43 | 316-316: 1.91; 412-416: 1.29; 436-436: 2.43 |
| max_elev_km | 4.43 | 6.03 | 8.03 |  |
| trees_pct | 21.65 | 29.98 | 39.80 |  |
| npp | 250.50 | 322.00 | 385.40 |  |
| landmasses | 4.00 | 8.00 | 13.00 |  |
| largest_pct | 15.50 | 17.80 | 34.80 |  |

### Seed 42, L6 (run b61d37)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.94 | 33.64 | 34.65 |  |
| cont_pct | 39.46 | 39.96 | 40.66 |  |
| cont_km | 33.10 | 33.51 | 34.09 |  |
| plates | 7.00 | 11.00 | 12.00 |  |
| ocean_age | 54.50 | 65.00 | 80.50 |  |
| speed | 2.38 | 3.98 | 4.88 |  |
| sea_level | -256.00 | -64.90 | 62.90 | 488-496: -256.00 |
| sea_ice_m | -172.50 | -34.70 | -0.00 |  |
| sea_tect_m | -166.70 | -25.60 | 62.90 |  |
| ice_pct | 0.00 | 1.80 | 7.10 |  |
| temp | 10.50 | 14.90 | 22.20 |  |
| co2 | -0.12 | 0.51 | 1.05 |  |
| dry_pct | 16.30 | 18.43 | 34.99 |  |
| inland_pct | 1.24 | 4.32 | 11.49 | 316-464: 1.24; 476-480: 4.63; 492-500: 4.81 |
| lake_pct | 0.14 | 0.67 | 3.69 | 324-324: 0.17; 344-364: 0.14; 416-424: 3.69 |
| lake_max_mkm2 | 0.03 | 0.11 | 4.62 | 304-304: 1.03; 416-424: 4.62; 456-456: 1.02; 468-468: 1.32; +1 more |
| max_elev_km | 3.20 | 5.49 | 7.71 |  |
| trees_pct | 21.36 | 37.41 | 43.55 |  |
| npp | 281.50 | 386.60 | 421.00 |  |
| landmasses | 3.00 | 5.00 | 8.00 |  |
| largest_pct | 13.30 | 24.00 | 29.30 |  |

### Seed 77, L6 (run 604c34)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.60 | 32.39 | 33.07 |  |
| cont_pct | 39.80 | 40.44 | 40.98 |  |
| cont_km | 32.68 | 33.10 | 34.16 |  |
| plates | 11.00 | 14.00 | 17.00 |  |
| ocean_age | 37.90 | 48.20 | 57.90 |  |
| speed | 3.45 | 4.26 | 5.13 |  |
| sea_level | -24.50 | 118.30 | 231.10 |  |
| sea_ice_m | -112.20 | -8.30 | -0.00 |  |
| sea_tect_m | 12.80 | 141.30 | 232.50 |  |
| ice_pct | 0.00 | 0.70 | 3.60 |  |
| temp | 7.70 | 16.10 | 19.30 | 444-444: 7.70 |
| co2 | -1.20 | -0.11 | 1.47 |  |
| dry_pct | 16.90 | 20.34 | 24.75 |  |
| inland_pct | 0.96 | 3.15 | 12.18 | 304-500: 0.96 |
| lake_pct | 0.18 | 0.46 | 2.01 | 396-396: 0.18; 408-416: 0.18 |
| lake_max_mkm2 | 0.03 | 0.09 | 2.14 | 328-328: 1.08; 444-444: 2.14 |
| max_elev_km | 2.83 | 5.88 | 7.86 |  |
| trees_pct | 4.05 | 30.81 | 43.94 | 432-436: 8.66; 476-500: 4.05 |
| npp | 161.90 | 316.90 | 406.10 | 428-436: 161.90 |
| landmasses | 3.00 | 7.00 | 14.00 |  |
| largest_pct | 10.40 | 17.40 | 31.20 |  |

### Seed 505, L6 (run 65ad3f)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.42 | 33.96 | 35.44 |  |
| cont_pct | 39.54 | 40.28 | 41.48 |  |
| cont_km | 32.55 | 33.66 | 34.17 |  |
| plates | 7.00 | 9.00 | 13.00 |  |
| ocean_age | 53.00 | 57.90 | 96.70 |  |
| speed | 3.48 | 4.52 | 5.38 |  |
| sea_level | -672.60 | 21.40 | 63.70 | 300-352: -672.60 |
| sea_ice_m | -445.00 | -7.00 | -0.10 | 300-332: -445.00 |
| sea_tect_m | -229.30 | 30.40 | 64.70 |  |
| ice_pct | 0.00 | 0.60 | 11.70 | 304-320: 11.70 |
| temp | 11.00 | 16.00 | 22.50 |  |
| co2 | -0.29 | 0.25 | 1.63 |  |
| dry_pct | 25.02 | 31.44 | 40.39 |  |
| inland_pct | 2.98 | 5.84 | 12.44 | 304-320: 3.04; 336-420: 3.32; 432-456: 4.34; 468-500: 2.98 |
| lake_pct | 0.12 | 0.54 | 1.71 | 308-312: 0.19; 456-456: 0.16; 472-472: 0.15; 484-496: 0.12 |
| lake_max_mkm2 | 0.03 | 0.15 | 2.52 | 300-300: 1.61; 324-324: 1.06; 424-428: 2.52; 440-444: 2.19 |
| max_elev_km | 3.52 | 5.23 | 7.97 |  |
| trees_pct | 20.53 | 30.88 | 41.49 |  |
| npp | 148.80 | 318.40 | 371.30 | 416-432: 148.80 |
| landmasses | 4.00 | 7.00 | 13.00 |  |
| largest_pct | 20.10 | 31.00 | 35.90 | 300-316: 35.90 |

## Determinism

Seed 1 L6 re-run to 100 Myr (run bbe777) against the sweep's run a47d91: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
