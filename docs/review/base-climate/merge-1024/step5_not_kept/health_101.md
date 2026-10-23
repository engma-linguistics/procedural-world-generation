# Health sweep 2026-10-23 14:06

Commit 0646532. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 11.3 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 500 | 91531e | 671 | 116 / 352 | 10.1 | 0 | 3.9 | 0.977 | 0.0 | 0.0 | ok | ok | 37.3 |
| 102 | 6 | 500 | 5faece | 588 | 116 / 344 | 8.1 | 0 | 2.0 | 0.978 | 9.8 | 0.0 | ok | ok | 41.2 |
| 103 | 6 | 500 | 61c1c5 | 559 | 116 / 336 | 12.5 | 0 | 15.7 | 0.969 | 35.3 | 0.0 | F | ok | 62.7 |
| 104 | 6 | 500 | 8dc103 | 565 | 116 / 312 | 6.2 | 0 | 5.9 | 0.968 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 105 | 6 | 500 | aebbbe | 678 | 108 / 312 | 13.5 | 0 | 15.7 | 0.956 | 3.9 | 0.0 | ok | ok | 43.1 |
| 106 | 6 | 500 | 5bf6cd | 562 | 116 / 312 | 7.9 | 0 | 0.0 | 0.977 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 107 | 6 | 500 | 0b9b5b | 636 | 100 / 300 | 10.4 | 0 | 7.8 | 0.951 | 3.9 | 9.8 | ok | F: icehouse 84% of the time, outside 5-70% | 84.3 |
| 108 | 6 | 500 | 7d52b4 | 654 | 104 / 320 | 7.0 | 0 | 0.0 | 0.96 | 0.0 | 0.0 | ok | F: icehouse 78% of the time, outside 5-70% | 78.4 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 31.5 | 39.2 | 34.6 | 12.0 | 46.8 | 4.5 | 160.9 | -12.9 | 174.4 | 0.9 | 16.1 | -0.7 | 34.3 | 8.8 | 0.5 | 0.1 | 7.3 | 6.8 | 220.0 | 7.0 | 24.7 |
| 102 | 6 | 32.1 | 40.8 | 33.5 | 13.0 | 45.7 | 4.0 | 182.7 | -12.6 | 191.8 | 0.8 | 13.2 | -0.3 | 23.9 | 4.3 | 0.5 | 0.1 | 5.9 | 26.6 | 267.0 | 10.0 | 20.0 |
| 103 | 6 | 32.0 | 40.4 | 33.6 | 14.0 | 47.3 | 5.0 | 85.0 | -63.1 | 149.8 | 2.7 | 13.4 | -0.4 | 25.1 | 5.2 | 0.4 | 0.1 | 5.1 | 11.3 | 277.4 | 9.0 | 15.3 |
| 104 | 6 | 34.3 | 40.1 | 33.6 | 11.0 | 59.8 | 4.0 | 52.2 | -6.7 | 57.6 | 0.5 | 17.0 | 0.3 | 29.1 | 5.0 | 0.4 | 0.1 | 4.7 | 27.0 | 302.0 | 6.0 | 24.0 |
| 105 | 6 | 32.2 | 40.5 | 33.0 | 12.0 | 50.6 | 4.5 | 91.4 | -17.3 | 105.8 | 1.3 | 16.6 | 0.5 | 28.2 | 3.7 | 0.6 | 0.2 | 6.3 | 36.2 | 355.4 | 11.0 | 18.5 |
| 106 | 6 | 35.2 | 40.3 | 34.0 | 11.0 | 59.2 | 5.6 | 68.2 | -0.3 | 68.2 | 0.0 | 17.9 | 0.6 | 33.1 | 6.8 | 0.2 | 0.1 | 4.6 | 32.9 | 312.5 | 6.0 | 35.0 |
| 107 | 6 | 33.5 | 40.2 | 33.8 | 6.0 | 71.1 | 3.8 | -182.3 | -76.8 | -143.4 | 3.0 | 8.2 | -1.1 | 29.5 | 4.2 | 0.3 | 0.1 | 7.2 | 5.8 | 229.0 | 6.0 | 30.9 |
| 108 | 6 | 33.0 | 41.2 | 32.9 | 12.0 | 55.7 | 4.7 | -10.4 | -30.5 | 45.0 | 1.9 | 13.7 | 0.3 | 19.7 | 2.1 | 0.5 | 0.1 | 4.8 | 38.0 | 373.8 | 7.0 | 15.4 |

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

## Top outliers (of 95 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 107 | 6 | low_plates | run | - | 9.80 | -..2 | 3.9 |
| 103 | 6 | sea_ice_below_150 | run | - | 35.30 | -..10 | 2.53 |
| 103 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 105 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 101 | 6 | lake_max_mkm2 | 452-452 | 1 | 4.33 | -..1.0 | 0.693 |
| 107 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 107 | 6 | lake_max_mkm2 | 352-360 | 3 | 3.27 | -..1.0 | 0.509 |
| 101 | 6 | lake_max_mkm2 | 468-468 | 1 | 3.30 | -..1.0 | 0.478 |
| 105 | 6 | lake_max_mkm2 | 460-472 | 4 | 2.23 | -..1.0 | 0.285 |
| 103 | 6 | sea_ice_m | 300-344 | 12 | -478.80 | -250..- | 0.27 |
| 105 | 6 | lake_max_mkm2 | 412-412 | 1 | 2.06 | -..1.0 | 0.219 |
| 104 | 6 | lake_max_mkm2 | 364-364 | 1 | 1.96 | -..1.0 | 0.199 |
| 108 | 6 | inland_pct | 300-500 | 51 | 0.81 | 8..30 | 0.198 |
| 102 | 6 | inland_pct | 300-500 | 48 | 0.68 | 8..30 | 0.193 |
| 103 | 6 | lake_max_mkm2 | 300-324 | 7 | 1.74 | -..1.0 | 0.19 |
| 104 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 104 | 6 | inland_pct | 300-500 | 48 | 1.41 | 8..30 | 0.174 |
| 103 | 6 | sea_level | 300-344 | 12 | -559.80 | -250..300 | 0.166 |
| 105 | 6 | inland_pct | 300-460 | 39 | 2.13 | 8..30 | 0.136 |
| 107 | 6 | inland_pct | 364-500 | 34 | 1.74 | 8..30 | 0.134 |
| 103 | 6 | inland_pct | 328-500 | 41 | 2.42 | 8..30 | 0.133 |
| 103 | 6 | ice_pct | 300-340 | 11 | 14.20 | -..10 | 0.121 |
| 101 | 6 | trees_pct | 340-476 | 33 | 0.51 | 10..50 | 0.11 |
| 106 | 6 | inland_pct | 440-500 | 16 | 1.61 | 8..30 | 0.095 |
| 102 | 6 | sea_level | 488-500 | 4 | -465.60 | -250..300 | 0.091 |
| 101 | 6 | inland_pct | 448-500 | 13 | 1.81 | 8..30 | 0.085 |
| 103 | 6 | trees_pct | 400-500 | 24 | 1.41 | 10..50 | 0.084 |
| 105 | 6 | inland_pct | 476-500 | 7 | 0.81 | 8..30 | 0.084 |
| 102 | 6 | sea_ice_m | 492-500 | 3 | -339.50 | -250..- | 0.08 |
| 104 | 6 | lake_max_mkm2 | 304-304 | 1 | 1.38 | -..1.0 | 0.079 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 101, L6 (run 91531e)

![seed 101 L6](seed101_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.22 | 31.49 | 32.87 |  |
| cont_pct | 36.13 | 39.24 | 39.93 |  |
| cont_km | 34.17 | 34.59 | 37.17 |  |
| plates | 7.00 | 12.00 | 14.00 |  |
| ocean_age | 38.10 | 46.80 | 64.90 |  |
| speed | 3.01 | 4.52 | 6.03 |  |
| sea_level | -129.60 | 160.90 | 241.90 |  |
| sea_ice_m | -133.70 | -12.90 | -0.30 |  |
| sea_tect_m | -30.00 | 174.40 | 242.70 |  |
| ice_pct | 0.00 | 0.90 | 5.40 |  |
| temp | 10.80 | 16.10 | 20.90 |  |
| co2 | -2.08 | -0.75 | 0.39 |  |
| dry_pct | 13.18 | 34.30 | 46.00 | 412-412: 46.00 |
| inland_pct | 1.81 | 8.79 | 16.10 | 312-312: 5.72; 360-376: 3.80; 412-412: 7.40; 432-432: 7.41; +1 more |
| lake_pct | 0.18 | 0.47 | 3.96 | 416-416: 0.19; 432-432: 0.18; 452-452: 3.96; 468-468: 3.01 |
| lake_max_mkm2 | 0.03 | 0.11 | 4.33 | 452-452: 4.33; 468-468: 3.30 |
| max_elev_km | 5.42 | 7.29 | 8.34 |  |
| trees_pct | 0.51 | 6.78 | 30.36 | 340-476: 0.51; 488-500: 3.75 |
| npp | 63.80 | 220.00 | 329.10 | 352-384: 63.80; 424-440: 189.90 |
| landmasses | 3.00 | 7.00 | 12.00 |  |
| largest_pct | 22.60 | 24.70 | 31.90 |  |

### Seed 102, L6 (run 5faece)

![seed 102 L6](seed102_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.44 | 32.07 | 33.52 |  |
| cont_pct | 37.50 | 40.75 | 41.75 |  |
| cont_km | 32.81 | 33.49 | 35.76 |  |
| plates | 6.00 | 13.00 | 17.00 |  |
| ocean_age | 38.10 | 45.70 | 84.20 |  |
| speed | 1.87 | 4.03 | 5.01 | 500-500: 1.87 |
| sea_level | -465.60 | 182.70 | 232.60 | 488-500: -465.60 |
| sea_ice_m | -339.50 | -12.60 | -0.00 | 492-500: -339.50 |
| sea_tect_m | -126.00 | 191.80 | 233.10 |  |
| ice_pct | 0.00 | 0.80 | 10.60 | 500-500: 10.60 |
| temp | 8.70 | 13.20 | 16.80 |  |
| co2 | -1.44 | -0.30 | 0.26 |  |
| dry_pct | 15.49 | 23.91 | 32.81 |  |
| inland_pct | 0.68 | 4.29 | 10.35 | 300-500: 0.68 |
| lake_pct | 0.21 | 0.52 | 1.48 |  |
| lake_max_mkm2 | 0.03 | 0.15 | 1.34 | 424-424: 1.34 |
| max_elev_km | 4.53 | 5.86 | 8.20 |  |
| trees_pct | 9.11 | 26.58 | 48.72 | 492-500: 9.11 |
| npp | 159.50 | 267.05 | 389.60 | 344-348: 159.50 |
| landmasses | 6.00 | 10.00 | 13.00 |  |
| largest_pct | 9.90 | 20.00 | 34.50 |  |

### Seed 103, L6 (run 61c1c5)

![seed 103 L6](seed103_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 28.62 | 32.02 | 33.19 |  |
| cont_pct | 37.50 | 40.36 | 41.45 |  |
| cont_km | 32.81 | 33.57 | 36.35 |  |
| plates | 9.00 | 14.00 | 18.00 |  |
| ocean_age | 38.40 | 47.30 | 71.40 |  |
| speed | 3.02 | 5.03 | 5.51 |  |
| sea_level | -559.80 | 85.00 | 216.10 | 300-344: -559.80 |
| sea_ice_m | -478.80 | -63.10 | -7.00 | 300-344: -478.80 |
| sea_tect_m | -98.50 | 149.80 | 223.40 |  |
| ice_pct | 0.60 | 2.70 | 14.20 | 300-340: 14.20 |
| temp | 6.70 | 13.40 | 19.20 | 300-328: 6.70 |
| co2 | -1.14 | -0.35 | 0.42 |  |
| dry_pct | 19.56 | 25.07 | 32.70 |  |
| inland_pct | 2.42 | 5.21 | 15.72 | 308-316: 5.23; 328-500: 2.42 |
| lake_pct | 0.13 | 0.42 | 2.15 | 428-456: 0.13; 468-472: 0.16 |
| lake_max_mkm2 | 0.03 | 0.09 | 1.74 | 300-324: 1.74; 408-408: 1.06 |
| max_elev_km | 3.79 | 5.07 | 8.39 |  |
| trees_pct | 1.41 | 11.26 | 42.91 | 400-500: 1.41 |
| npp | 170.40 | 277.35 | 404.70 | 396-400: 170.40 |
| landmasses | 2.00 | 9.00 | 14.00 | 332-332: 2 |
| largest_pct | 8.70 | 15.30 | 33.50 |  |

### Seed 104, L6 (run 8dc103)

![seed 104 L6](seed104_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.97 | 34.31 | 35.44 |  |
| cont_pct | 39.45 | 40.10 | 41.25 |  |
| cont_km | 33.01 | 33.63 | 33.90 |  |
| plates | 9.00 | 11.00 | 16.00 |  |
| ocean_age | 52.00 | 59.80 | 70.30 |  |
| speed | 3.42 | 4.03 | 5.06 |  |
| sea_level | -68.80 | 52.20 | 96.10 |  |
| sea_ice_m | -13.20 | -6.70 | -0.00 |  |
| sea_tect_m | -68.60 | 57.60 | 108.60 |  |
| ice_pct | 0.00 | 0.50 | 1.10 |  |
| temp | 13.10 | 17.00 | 19.30 |  |
| co2 | -0.82 | 0.32 | 1.26 |  |
| dry_pct | 24.56 | 29.08 | 36.17 |  |
| inland_pct | 1.41 | 5.05 | 8.59 | 300-500: 1.41 |
| lake_pct | 0.14 | 0.40 | 1.73 | 384-384: 0.14 |
| lake_max_mkm2 | 0.03 | 0.10 | 1.96 | 304-304: 1.38; 320-320: 1.17; 364-364: 1.96 |
| max_elev_km | 3.96 | 4.68 | 7.69 |  |
| trees_pct | 5.55 | 27.00 | 38.85 | 300-308: 5.55 |
| npp | 140.50 | 302.00 | 382.90 | 312-336: 140.50 |
| landmasses | 5.00 | 6.00 | 11.00 |  |
| largest_pct | 12.20 | 24.00 | 33.80 |  |

### Seed 105, L6 (run aebbbe)

![seed 105 L6](seed105_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.24 | 32.24 | 34.61 |  |
| cont_pct | 40.22 | 40.52 | 41.36 |  |
| cont_km | 32.54 | 33.05 | 33.91 |  |
| plates | 6.00 | 12.00 | 16.00 |  |
| ocean_age | 43.00 | 50.60 | 73.50 |  |
| speed | 2.45 | 4.53 | 5.04 |  |
| sea_level | -338.30 | 91.40 | 156.70 | 496-500: -338.30 |
| sea_ice_m | -227.40 | -17.30 | -9.80 |  |
| sea_tect_m | -110.90 | 105.80 | 171.80 |  |
| ice_pct | 0.70 | 1.30 | 8.70 |  |
| temp | 8.30 | 16.60 | 21.80 |  |
| co2 | -0.72 | 0.48 | 1.74 |  |
| dry_pct | 9.92 | 28.16 | 32.03 | 464-500: 9.92 |
| inland_pct | 0.81 | 3.68 | 9.17 | 300-460: 2.13; 476-500: 0.81 |
| lake_pct | 0.21 | 0.60 | 1.95 |  |
| lake_max_mkm2 | 0.04 | 0.19 | 2.23 | 376-376: 1.27; 400-400: 1.34; 412-412: 2.06; 424-424: 1.08; +1 more |
| max_elev_km | 4.47 | 6.30 | 8.19 |  |
| trees_pct | 18.56 | 36.16 | 47.53 |  |
| npp | 241.60 | 355.35 | 504.20 |  |
| landmasses | 5.00 | 11.00 | 16.00 |  |
| largest_pct | 11.00 | 18.50 | 25.70 |  |

### Seed 106, L6 (run 5bf6cd)

![seed 106 L6](seed106_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.45 | 35.17 | 35.87 |  |
| cont_pct | 38.72 | 40.28 | 42.31 |  |
| cont_km | 32.96 | 34.01 | 35.11 |  |
| plates | 9.00 | 11.00 | 15.00 |  |
| ocean_age | 45.10 | 59.20 | 68.40 |  |
| speed | 3.46 | 5.57 | 6.79 |  |
| sea_level | -114.70 | 68.20 | 136.90 |  |
| sea_ice_m | -10.40 | -0.30 | -0.00 |  |
| sea_tect_m | -113.50 | 68.20 | 142.40 |  |
| ice_pct | 0.00 | 0.00 | 0.80 |  |
| temp | 12.60 | 17.90 | 20.50 |  |
| co2 | -0.17 | 0.63 | 1.23 |  |
| dry_pct | 19.27 | 33.13 | 46.81 | 352-372: 46.81 |
| inland_pct | 1.61 | 6.81 | 20.91 | 300-344: 3.65; 376-396: 5.18; 408-416: 6.81; 440-500: 1.61 |
| lake_pct | 0.05 | 0.23 | 0.57 | 300-312: 0.17; 324-328: 0.18; 340-348: 0.17; 360-384: 0.05; +3 more |
| lake_max_mkm2 | 0.03 | 0.05 | 0.51 |  |
| max_elev_km | 3.74 | 4.58 | 8.49 |  |
| trees_pct | 23.99 | 32.86 | 41.58 |  |
| npp | 225.60 | 312.50 | 394.10 |  |
| landmasses | 2.00 | 6.00 | 15.00 | 340-352: 2 |
| largest_pct | 13.70 | 35.00 | 35.70 | 300-380: 35.70; 396-408: 35.20 |

### Seed 107, L6 (run 0b9b5b)

![seed 107 L6](seed107_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.47 | 33.52 | 34.76 |  |
| cont_pct | 39.44 | 40.17 | 41.50 |  |
| cont_km | 33.15 | 33.81 | 34.15 |  |
| plates | 4.00 | 6.00 | 10.00 | 440-448: 4; 476-480: 4 |
| ocean_age | 47.70 | 71.10 | 89.50 |  |
| speed | 1.67 | 3.84 | 5.43 | 320-320: 1.67; 440-440: 1.95 |
| sea_level | -375.00 | -182.30 | 143.10 | 436-500: -375.00 |
| sea_ice_m | -152.30 | -76.80 | -7.00 |  |
| sea_tect_m | -245.70 | -143.40 | 159.30 |  |
| ice_pct | 0.60 | 3.00 | 6.10 |  |
| temp | 4.30 | 8.20 | 14.70 | 352-404: 4.30; 444-488: 5.50 |
| co2 | -2.48 | -1.13 | -0.04 |  |
| dry_pct | 23.67 | 29.49 | 38.81 |  |
| inland_pct | 1.74 | 4.18 | 11.73 | 300-348: 3.98; 364-500: 1.74 |
| lake_pct | 0.15 | 0.31 | 2.52 | 308-308: 0.15; 380-380: 0.15; 392-392: 0.19; 420-420: 0.19 |
| lake_max_mkm2 | 0.01 | 0.06 | 3.27 | 352-360: 3.27; 372-372: 1.01 |
| max_elev_km | 3.72 | 7.19 | 8.37 |  |
| trees_pct | 2.02 | 5.76 | 20.84 | 300-364: 2.02; 380-472: 3.46 |
| npp | 117.20 | 229.00 | 372.70 | 300-368: 117.20; 380-380: 158.20 |
| landmasses | 3.00 | 6.00 | 12.00 |  |
| largest_pct | 16.00 | 30.90 | 34.90 |  |

### Seed 108, L6 (run 7d52b4)

![seed 108 L6](seed108_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.54 | 32.99 | 34.38 |  |
| cont_pct | 39.79 | 41.16 | 41.88 |  |
| cont_km | 32.29 | 32.91 | 34.14 |  |
| plates | 9.00 | 12.00 | 15.00 |  |
| ocean_age | 46.30 | 55.70 | 64.90 |  |
| speed | 3.31 | 4.69 | 5.49 |  |
| sea_level | -73.90 | -10.40 | 109.10 |  |
| sea_ice_m | -119.60 | -30.50 | -9.30 |  |
| sea_tect_m | -16.40 | 45.00 | 139.10 |  |
| ice_pct | 0.80 | 1.90 | 5.00 |  |
| temp | 11.40 | 13.70 | 18.40 |  |
| co2 | -0.35 | 0.27 | 0.74 |  |
| dry_pct | 13.21 | 19.72 | 23.94 |  |
| inland_pct | 0.81 | 2.14 | 6.66 | 300-500: 0.81 |
| lake_pct | 0.21 | 0.52 | 1.18 |  |
| lake_max_mkm2 | 0.04 | 0.11 | 0.91 |  |
| max_elev_km | 3.98 | 4.83 | 7.51 |  |
| trees_pct | 23.78 | 37.98 | 54.44 | 340-372: 54.44 |
| npp | 274.40 | 373.80 | 432.50 |  |
| landmasses | 4.00 | 7.00 | 11.00 |  |
| largest_pct | 8.30 | 15.40 | 29.60 |  |

## Determinism

Seed 101 L6 re-run to 100 Myr (run c69006) against the sweep's run 91531e: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
