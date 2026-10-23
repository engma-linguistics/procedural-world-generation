# Health sweep 2026-10-23 13:55

Commit 0646532. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 12.4 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | c4e389 | 632 | 104 / 316 | 9.1 | 0 | 25.5 | 0.973 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 2 | 6 | 500 | 91011f | 718 | 116 / 268 | 11.1 | 0 | 0.0 | 0.965 | 0.0 | 0.0 | ok | ok | 51.0 |
| 11 | 6 | 500 | e7ee20 | 737 | 116 / 272 | 10.4 | 0 | 2.0 | 0.98 | 27.5 | 0.0 | ok | ok | 54.9 |
| 21 | 6 | 500 | 7c6530 | 631 | 116 / 336 | 11.4 | 0 | 9.8 | 0.949 | 0.0 | 0.0 | ok | F: icehouse 2% of the time, outside 5-70% | 2.0 |
| 3199 | 6 | 500 | 8d06ca | 677 | 112 / 344 | 8.9 | 0 | 2.0 | 0.96 | 0.0 | 0.0 | ok | F: icehouse 76% of the time, outside 5-70% | 76.5 |
| 42 | 6 | 500 | 77ea91 | 690 | 116 / 288 | 10.0 | 0 | 3.9 | 0.975 | 23.5 | 0.0 | ok | F: icehouse 71% of the time, outside 5-70% | 70.6 |
| 77 | 6 | 500 | 69a333 | 739 | 112 / 272 | 13.7 | 0 | 2.0 | 0.966 | 88.2 | 2.0 | ok | F: deep era 300-476 Myr lasts 180 > 150; icehouse 100% of the time, outside 5-70% | 100.0 |
| 505 | 6 | 500 | fae5c0 | 706 | 108 / 328 | 7.2 | 0 | 5.9 | 0.969 | 0.0 | 0.0 | ok | ok | 13.7 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 34.9 | 40.0 | 34.2 | 14.0 | 56.2 | 4.2 | 64.8 | -4.5 | 68.7 | 0.3 | 15.9 | 0.2 | 26.6 | 7.3 | 0.6 | 0.3 | 4.1 | 33.8 | 280.3 | 5.0 | 21.1 |
| 2 | 6 | 34.2 | 40.7 | 32.9 | 9.0 | 78.2 | 4.2 | -167.6 | -21.4 | -136.6 | 1.2 | 15.3 | 0.4 | 23.9 | 2.9 | 0.4 | 0.1 | 7.0 | 35.6 | 370.8 | 9.0 | 28.0 |
| 11 | 6 | 31.1 | 39.7 | 33.9 | 12.0 | 59.3 | 4.0 | 24.0 | -27.9 | 40.2 | 2.4 | 14.1 | -0.3 | 20.3 | 4.3 | 0.6 | 0.1 | 6.7 | 28.5 | 276.1 | 10.0 | 15.8 |
| 21 | 6 | 34.4 | 40.5 | 33.1 | 12.0 | 61.7 | 4.5 | 10.6 | -3.0 | 15.3 | 0.2 | 16.1 | 0.1 | 32.2 | 6.2 | 0.3 | 0.1 | 5.3 | 21.8 | 307.0 | 8.0 | 25.9 |
| 3199 | 6 | 32.9 | 39.8 | 33.9 | 10.0 | 55.7 | 4.1 | 2.6 | -68.4 | 55.6 | 3.4 | 12.7 | -0.0 | 24.0 | 3.9 | 0.4 | 0.1 | 6.2 | 30.5 | 352.5 | 6.0 | 19.2 |
| 42 | 6 | 33.3 | 40.3 | 33.7 | 13.0 | 57.4 | 4.1 | -28.9 | -30.1 | 44.3 | 1.9 | 13.6 | 0.4 | 23.7 | 3.6 | 0.3 | 0.1 | 4.3 | 38.0 | 324.1 | 8.0 | 19.9 |
| 77 | 6 | 32.2 | 40.1 | 33.9 | 6.0 | 90.5 | 3.0 | -534.0 | -337.2 | -247.1 | 12.2 | 10.3 | -0.5 | 22.3 | 3.7 | 0.4 | 0.1 | 7.3 | 23.2 | 253.8 | 8.0 | 33.7 |
| 505 | 6 | 34.1 | 41.5 | 32.7 | 9.0 | 55.8 | 4.3 | 35.1 | -8.9 | 43.7 | 0.6 | 15.3 | -0.1 | 26.2 | 2.7 | 0.3 | 0.1 | 5.8 | 26.6 | 332.4 | 6.0 | 21.6 |

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

## Top outliers (of 101 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 77 | 6 | sea_ice_below_150 | run | - | 88.20 | -..10 | 7.82 |
| 1 | 6 | giant_lake_frames | run | - | 25.50 | -..5 | 4.1 |
| 1 | 6 | lake_max_mkm2 | 340-352 | 4 | 12.29 | -..1.0 | 2.616 |
| 1 | 6 | lake_max_mkm2 | 424-440 | 5 | 10.16 | -..1.0 | 2.196 |
| 11 | 6 | sea_ice_below_150 | run | - | 27.50 | -..10 | 1.75 |
| 1 | 6 | lake_max_mkm2 | 404-412 | 2 | 9.04 | -..1.0 | 1.736 |
| 1 | 6 | lake_max_mkm2 | 452-452 | 1 | 9.24 | -..1.0 | 1.713 |
| 42 | 6 | sea_ice_below_150 | run | - | 23.50 | -..10 | 1.35 |
| 21 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 21 | 6 | lake_max_mkm2 | 484-484 | 1 | 3.76 | -..1.0 | 0.574 |
| 77 | 6 | sea_level | 316-500 | 47 | -718.70 | -250..300 | 0.488 |
| 1 | 6 | lake_max_mkm2 | 388-388 | 1 | 2.96 | -..1.0 | 0.408 |
| 1 | 6 | lake_pct | 340-352 | 4 | 7.45 | 0.2..3.0 | 0.368 |
| 21 | 6 | lake_max_mkm2 | 300-308 | 3 | 2.44 | -..1.0 | 0.323 |
| 77 | 6 | sea_ice_m | 304-472 | 43 | -389.50 | -250..- | 0.302 |
| 21 | 6 | lake_max_mkm2 | 468-468 | 1 | 2.19 | -..1.0 | 0.248 |
| 1 | 6 | lake_pct | 424-432 | 3 | 6.00 | 0.2..3.0 | 0.24 |
| 1 | 6 | lake_pct | 452-452 | 1 | 6.13 | 0.2..3.0 | 0.232 |
| 1 | 6 | lake_pct | 412-412 | 1 | 5.81 | 0.2..3.0 | 0.209 |
| 2 | 6 | inland_pct | 300-500 | 51 | 0.40 | 8..30 | 0.209 |
| 505 | 6 | inland_pct | 300-500 | 49 | 0.39 | 8..30 | 0.204 |
| 11 | 6 | inland_pct | 304-500 | 50 | 0.88 | 8..30 | 0.193 |
| 77 | 6 | ice_pct | 336-468 | 34 | 13.90 | -..10 | 0.183 |
| 3199 | 6 | inland_pct | 300-500 | 50 | 1.35 | 8..30 | 0.18 |
| 77 | 6 | inland_pct | 300-500 | 49 | 1.28 | 8..30 | 0.18 |
| 505 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 42 | 6 | inland_pct | 300-484 | 47 | 1.18 | 8..30 | 0.178 |
| 77 | 6 | lake_max_mkm2 | 428-428 | 1 | 1.58 | -..1.0 | 0.121 |
| 505 | 6 | lake_max_mkm2 | 440-440 | 1 | 1.54 | -..1.0 | 0.113 |
| 42 | 6 | lake_max_mkm2 | 492-496 | 2 | 1.49 | -..1.0 | 0.107 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run c4e389)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 34.58 | 34.90 | 35.24 |  |
| cont_pct | 39.03 | 39.95 | 40.41 |  |
| cont_km | 33.67 | 34.16 | 34.76 |  |
| plates | 11.00 | 14.00 | 17.00 |  |
| ocean_age | 51.70 | 56.20 | 62.80 |  |
| speed | 2.48 | 4.18 | 5.49 |  |
| sea_level | -6.10 | 64.80 | 98.60 |  |
| sea_ice_m | -14.00 | -4.50 | -0.00 |  |
| sea_tect_m | -6.10 | 68.70 | 103.40 |  |
| ice_pct | 0.00 | 0.30 | 1.00 |  |
| temp | 11.70 | 15.90 | 20.80 |  |
| co2 | -0.46 | 0.22 | 0.81 |  |
| dry_pct | 15.97 | 26.58 | 45.50 | 300-300: 45.50 |
| inland_pct | 2.32 | 7.35 | 20.42 | 316-316: 7.34; 336-344: 4.05; 356-404: 2.32; 416-420: 4.62; +3 more |
| lake_pct | 0.24 | 0.60 | 7.45 | 340-352: 7.45; 412-412: 5.81; 424-432: 6.00; 452-452: 6.13 |
| lake_max_mkm2 | 0.01 | 0.31 | 12.29 | 340-352: 12.29; 388-388: 2.96; 404-412: 9.04; 424-440: 10.16; +1 more |
| max_elev_km | 3.13 | 4.14 | 6.36 |  |
| trees_pct | 21.83 | 33.75 | 48.46 |  |
| npp | 180.00 | 280.30 | 355.90 | 356-364: 180.00 |
| landmasses | 2.00 | 5.00 | 7.00 | 300-300: 2; 452-452: 2 |
| largest_pct | 14.80 | 21.10 | 32.50 |  |

### Seed 2, L6 (run 91011f)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.58 | 34.18 | 35.25 |  |
| cont_pct | 39.79 | 40.72 | 41.51 |  |
| cont_km | 32.14 | 32.88 | 33.96 |  |
| plates | 7.00 | 9.00 | 11.00 |  |
| ocean_age | 64.00 | 78.20 | 86.70 |  |
| speed | 1.82 | 4.24 | 5.47 | 348-352: 1.82; 400-400: 1.97 |
| sea_level | -223.90 | -167.60 | -60.90 |  |
| sea_ice_m | -84.80 | -21.40 | -1.80 |  |
| sea_tect_m | -179.70 | -136.60 | -55.90 |  |
| ice_pct | 0.20 | 1.20 | 4.70 |  |
| temp | 10.10 | 15.30 | 21.20 |  |
| co2 | -0.66 | 0.39 | 1.73 |  |
| dry_pct | 16.94 | 23.92 | 30.97 |  |
| inland_pct | 0.40 | 2.88 | 5.80 | 300-500: 0.40 |
| lake_pct | 0.11 | 0.35 | 0.62 | 324-340: 0.11 |
| lake_max_mkm2 | 0.01 | 0.05 | 0.35 |  |
| max_elev_km | 4.92 | 7.04 | 8.55 |  |
| trees_pct | 20.17 | 35.63 | 40.58 |  |
| npp | 161.10 | 370.80 | 468.90 | 304-304: 191.10; 348-352: 161.10 |
| landmasses | 4.00 | 9.00 | 14.00 |  |
| largest_pct | 12.40 | 28.00 | 35.20 | 300-304: 35.20 |

### Seed 11, L6 (run e7ee20)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 28.71 | 31.05 | 32.67 |  |
| cont_pct | 38.21 | 39.71 | 41.07 |  |
| cont_km | 33.15 | 33.94 | 35.12 |  |
| plates | 10.00 | 12.00 | 16.00 |  |
| ocean_age | 43.60 | 59.30 | 64.40 |  |
| speed | 3.18 | 4.03 | 5.14 |  |
| sea_level | -278.00 | 24.00 | 92.60 | 412-432: -278.00 |
| sea_ice_m | -258.50 | -27.90 | -5.00 | 408-424: -258.50 |
| sea_tect_m | -25.50 | 40.20 | 121.70 |  |
| ice_pct | 0.60 | 2.40 | 8.60 |  |
| temp | 9.10 | 14.10 | 19.50 |  |
| co2 | -1.85 | -0.29 | 0.59 |  |
| dry_pct | 17.02 | 20.30 | 28.31 |  |
| inland_pct | 0.88 | 4.29 | 12.04 | 304-500: 0.88 |
| lake_pct | 0.21 | 0.58 | 1.19 |  |
| lake_max_mkm2 | 0.03 | 0.09 | 1.07 | 300-300: 1.07 |
| max_elev_km | 5.64 | 6.72 | 8.32 |  |
| trees_pct | 1.02 | 28.54 | 40.68 | 300-324: 1.51; 472-500: 1.02 |
| npp | 58.50 | 276.10 | 476.20 | 300-348: 58.50 |
| landmasses | 4.00 | 10.00 | 16.00 |  |
| largest_pct | 11.50 | 15.80 | 21.30 |  |

### Seed 21, L6 (run 7c6530)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.43 | 34.43 | 35.76 |  |
| cont_pct | 39.62 | 40.47 | 42.12 |  |
| cont_km | 32.43 | 33.08 | 33.61 |  |
| plates | 7.00 | 12.00 | 16.00 |  |
| ocean_age | 49.50 | 61.70 | 85.20 |  |
| speed | 2.64 | 4.55 | 5.53 |  |
| sea_level | -222.60 | 10.60 | 126.80 |  |
| sea_ice_m | -26.20 | -3.00 | -0.00 |  |
| sea_tect_m | -196.40 | 15.30 | 129.40 |  |
| ice_pct | 0.00 | 0.20 | 1.60 |  |
| temp | 12.30 | 16.10 | 23.70 |  |
| co2 | -0.96 | 0.05 | 0.69 |  |
| dry_pct | 26.39 | 32.22 | 40.01 |  |
| inland_pct | 2.82 | 6.23 | 16.40 | 312-336: 4.82; 356-356: 7.15; 368-496: 2.82 |
| lake_pct | 0.09 | 0.27 | 2.49 | 340-352: 0.13; 368-376: 0.16; 388-428: 0.09; 444-444: 0.18 |
| lake_max_mkm2 | 0.01 | 0.07 | 3.76 | 300-308: 2.44; 468-468: 2.19; 484-484: 3.76 |
| max_elev_km | 3.03 | 5.28 | 8.62 |  |
| trees_pct | 3.75 | 21.82 | 37.67 | 388-388: 7.71; 468-500: 3.75 |
| npp | 169.90 | 307.00 | 405.00 | 336-340: 191.50; 352-352: 169.90; 364-364: 198.50; 376-380: 172.20 |
| landmasses | 2.00 | 8.00 | 13.00 | 304-304: 2 |
| largest_pct | 16.00 | 25.90 | 35.70 | 300-304: 35.70 |

### Seed 3199, L6 (run 8d06ca)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.51 | 32.85 | 34.39 |  |
| cont_pct | 39.33 | 39.81 | 40.33 |  |
| cont_km | 33.58 | 33.86 | 34.18 |  |
| plates | 8.00 | 10.00 | 14.00 |  |
| ocean_age | 41.60 | 55.70 | 64.90 |  |
| speed | 2.90 | 4.07 | 5.33 |  |
| sea_level | -145.90 | 2.60 | 157.40 |  |
| sea_ice_m | -96.50 | -68.40 | -3.30 |  |
| sea_tect_m | -50.00 | 55.60 | 195.10 |  |
| ice_pct | 0.30 | 3.40 | 4.40 |  |
| temp | 9.90 | 12.70 | 18.80 |  |
| co2 | -0.77 | -0.03 | 0.74 |  |
| dry_pct | 17.18 | 23.97 | 35.37 |  |
| inland_pct | 1.35 | 3.87 | 8.29 | 300-500: 1.35 |
| lake_pct | 0.13 | 0.35 | 0.91 | 320-320: 0.20; 372-384: 0.13; 484-484: 0.19 |
| lake_max_mkm2 | 0.03 | 0.07 | 1.23 | 308-308: 1.23 |
| max_elev_km | 3.35 | 6.18 | 7.73 |  |
| trees_pct | 14.31 | 30.46 | 41.28 |  |
| npp | 237.50 | 352.50 | 478.60 |  |
| landmasses | 4.00 | 6.00 | 11.00 |  |
| largest_pct | 10.70 | 19.20 | 34.00 |  |

### Seed 42, L6 (run 77ea91)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.71 | 33.33 | 34.37 |  |
| cont_pct | 39.80 | 40.30 | 40.78 |  |
| cont_km | 33.28 | 33.69 | 34.18 |  |
| plates | 10.00 | 13.00 | 15.00 |  |
| ocean_age | 46.80 | 57.40 | 68.30 |  |
| speed | 2.91 | 4.09 | 4.88 |  |
| sea_level | -225.70 | -28.90 | 135.40 |  |
| sea_ice_m | -221.30 | -30.10 | -6.70 |  |
| sea_tect_m | -40.90 | 44.30 | 146.80 |  |
| ice_pct | 0.60 | 1.90 | 6.80 |  |
| temp | 10.80 | 13.60 | 20.80 |  |
| co2 | -0.07 | 0.42 | 0.86 |  |
| dry_pct | 20.80 | 23.68 | 27.86 |  |
| inland_pct | 1.18 | 3.62 | 11.11 | 300-484: 1.18; 500-500: 2.83 |
| lake_pct | 0.13 | 0.33 | 1.90 | 332-332: 0.17; 424-428: 0.17; 440-444: 0.13; 464-464: 0.20 |
| lake_max_mkm2 | 0.03 | 0.07 | 1.49 | 492-496: 1.49 |
| max_elev_km | 3.84 | 4.27 | 8.56 |  |
| trees_pct | 27.18 | 37.96 | 49.62 |  |
| npp | 182.40 | 324.10 | 444.90 | 304-316: 182.40 |
| landmasses | 2.00 | 8.00 | 11.00 | 500-500: 2 |
| largest_pct | 10.90 | 19.90 | 34.00 |  |

### Seed 77, L6 (run 69a333)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.82 | 32.20 | 33.88 |  |
| cont_pct | 38.20 | 40.14 | 42.06 |  |
| cont_km | 32.17 | 33.85 | 35.29 |  |
| plates | 4.00 | 6.00 | 9.00 | 452-452: 4 |
| ocean_age | 56.70 | 90.50 | 120.30 | 456-456: 120.30 |
| speed | 0.76 | 2.97 | 6.84 | 364-376: 0.76 |
| sea_level | -718.70 | -534.00 | -207.90 | 316-500: -718.70 |
| sea_ice_m | -389.50 | -337.20 | -74.10 | 304-472: -389.50 |
| sea_tect_m | -335.90 | -247.10 | 40.40 | 392-488: -335.90 |
| ice_pct | 3.60 | 12.20 | 13.90 | 304-320: 10.50; 336-468: 13.90 |
| temp | 4.50 | 10.30 | 18.20 | 432-456: 4.50 |
| co2 | -1.56 | -0.50 | 0.78 |  |
| dry_pct | 18.53 | 22.27 | 28.20 |  |
| inland_pct | 1.28 | 3.68 | 9.75 | 300-500: 1.28 |
| lake_pct | 0.13 | 0.42 | 1.23 | 320-320: 0.18; 384-400: 0.13; 416-416: 0.19 |
| lake_max_mkm2 | 0.03 | 0.11 | 1.58 | 428-428: 1.58 |
| max_elev_km | 6.02 | 7.26 | 8.40 |  |
| trees_pct | 8.18 | 23.22 | 49.20 | 360-364: 9.38; 388-396: 8.18 |
| npp | 141.60 | 253.80 | 429.60 | 344-396: 141.60; 428-440: 175.90 |
| landmasses | 3.00 | 8.00 | 13.00 |  |
| largest_pct | 17.20 | 33.70 | 35.40 | 416-452: 35.40 |

### Seed 505, L6 (run fae5c0)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.06 | 34.07 | 34.99 |  |
| cont_pct | 39.09 | 41.53 | 42.51 |  |
| cont_km | 32.11 | 32.72 | 34.44 |  |
| plates | 6.00 | 9.00 | 12.00 |  |
| ocean_age | 50.60 | 55.80 | 69.70 |  |
| speed | 3.66 | 4.28 | 5.57 |  |
| sea_level | -206.90 | 35.10 | 73.40 |  |
| sea_ice_m | -29.30 | -8.90 | -1.00 |  |
| sea_tect_m | -179.60 | 43.70 | 79.00 |  |
| ice_pct | 0.10 | 0.60 | 2.00 |  |
| temp | 12.20 | 15.30 | 19.40 |  |
| co2 | -1.41 | -0.14 | 0.97 |  |
| dry_pct | 13.82 | 26.18 | 33.64 |  |
| inland_pct | 0.39 | 2.74 | 9.67 | 300-500: 0.39 |
| lake_pct | 0.10 | 0.29 | 1.63 | 360-360: 0.10; 416-416: 0.19; 468-468: 0.17; 488-500: 0.16 |
| lake_max_mkm2 | 0.03 | 0.07 | 1.54 | 420-420: 1.38; 440-440: 1.54; 460-460: 1.17 |
| max_elev_km | 4.18 | 5.78 | 7.19 |  |
| trees_pct | 1.59 | 26.64 | 47.90 | 444-496: 1.59 |
| npp | 231.30 | 332.35 | 412.10 |  |
| landmasses | 2.00 | 6.00 | 11.00 | 336-336: 2 |
| largest_pct | 12.20 | 21.60 | 34.40 |  |

## Determinism

Seed 1 L6 re-run to 100 Myr (run 74890d) against the sweep's run c4e389: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
