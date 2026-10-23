# Health sweep 2026-10-23 12:15

Commit None. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 13.6 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 500 | 3a6bcf | 736 | 136 / 408 | 6.2 | 0 | 0.0 | 0.971 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 102 | 6 | 500 | d8f484 | 812 | 140 / 392 | 6.0 | 0 | 5.9 | 0.967 | 0.0 | 0.0 | ok | ok | 5.9 |
| 103 | 6 | 500 | 9a529d | 741 | 128 / 424 | 11.5 | 0 | 2.0 | 0.962 | 27.5 | 0.0 | ok | ok | 68.6 |
| 104 | 6 | 500 | c3dc19 | 741 | 124 / 432 | 9.1 | 0 | 17.6 | 0.961 | 0.0 | 0.0 | ok | ok | 31.4 |
| 105 | 6 | 500 | fa13a3 | 786 | 132 / 376 | 4.8 | 0 | 7.8 | 0.999 | 0.0 | 0.0 | ok | ok | 58.8 |
| 106 | 6 | 500 | 4b705b | 667 | 132 / 396 | 8.5 | 0 | 15.7 | 0.967 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 107 | 6 | 500 | 4defed | 751 | 132 / 404 | 5.9 | 0 | 9.8 | 0.973 | 0.0 | 0.0 | ok | ok | 23.5 |
| 108 | 6 | 500 | 950c68 | 690 | 128 / 376 | 9.5 | 0 | 13.7 | 0.976 | 0.0 | 0.0 | ok | ok | 56.9 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 34.3 | 40.8 | 33.7 | 10.0 | 60.0 | 4.6 | -0.2 | -1.1 | 3.3 | 0.1 | 17.3 | -0.7 | 26.0 | 3.8 | 0.3 | 0.1 | 4.8 | 24.4 | 324.0 | 7.0 | 13.9 |
| 102 | 6 | 33.3 | 41.0 | 33.0 | 10.0 | 58.1 | 4.1 | 21.9 | -7.5 | 29.4 | 0.5 | 16.6 | 0.4 | 25.0 | 4.6 | 0.4 | 0.1 | 6.4 | 34.5 | 294.1 | 12.0 | 12.3 |
| 103 | 6 | 32.2 | 39.0 | 34.8 | 15.0 | 53.4 | 4.6 | 25.5 | -92.5 | 132.6 | 3.1 | 12.2 | -0.8 | 25.2 | 4.6 | 0.4 | 0.1 | 6.7 | 26.5 | 324.5 | 6.0 | 17.6 |
| 104 | 6 | 33.3 | 39.3 | 34.2 | 11.0 | 55.8 | 4.3 | 75.3 | -6.0 | 84.7 | 0.5 | 14.8 | 0.0 | 27.2 | 6.2 | 0.7 | 0.2 | 6.8 | 32.2 | 304.6 | 4.0 | 28.1 |
| 105 | 6 | 33.6 | 41.0 | 33.4 | 10.0 | 67.4 | 3.9 | -39.0 | -21.5 | -21.7 | 1.6 | 15.3 | 0.3 | 14.7 | 4.7 | 1.0 | 0.2 | 5.5 | 33.4 | 351.5 | 11.0 | 20.3 |
| 106 | 6 | 33.0 | 41.1 | 32.7 | 13.0 | 53.5 | 4.6 | 123.8 | -1.5 | 128.2 | 0.1 | 17.0 | 0.7 | 26.4 | 4.4 | 0.3 | 0.1 | 4.7 | 29.7 | 349.6 | 8.0 | 19.1 |
| 107 | 6 | 32.2 | 40.2 | 33.8 | 14.0 | 56.1 | 4.3 | 68.5 | -8.6 | 80.7 | 0.6 | 14.4 | -0.1 | 22.4 | 5.1 | 0.5 | 0.2 | 5.4 | 37.3 | 327.4 | 12.0 | 17.4 |
| 108 | 6 | 33.4 | 40.0 | 33.9 | 13.0 | 53.5 | 4.1 | 42.3 | -22.1 | 67.6 | 1.4 | 14.8 | 0.3 | 21.4 | 4.4 | 0.5 | 0.1 | 5.5 | 29.4 | 303.8 | 7.0 | 19.7 |

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

## Top outliers (of 74 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 104 | 6 | giant_lake_frames | run | - | 17.60 | -..5 | 2.52 |
| 106 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 106 | 6 | lake_max_mkm2 | 492-500 | 3 | 10.35 | -..1.0 | 2.092 |
| 103 | 6 | sea_ice_below_150 | run | - | 27.50 | -..10 | 1.75 |
| 108 | 6 | giant_lake_frames | run | - | 13.70 | -..5 | 1.74 |
| 104 | 6 | lake_max_mkm2 | 312-312 | 1 | 7.89 | -..1.0 | 1.434 |
| 107 | 6 | lake_max_mkm2 | 412-428 | 4 | 5.52 | -..1.0 | 1.047 |
| 107 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 106 | 6 | lake_max_mkm2 | 384-384 | 1 | 4.12 | -..1.0 | 0.649 |
| 105 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 102 | 6 | lake_max_mkm2 | 488-488 | 1 | 2.89 | -..1.0 | 0.393 |
| 102 | 6 | lake_max_mkm2 | 320-320 | 1 | 2.34 | -..1.0 | 0.279 |
| 106 | 6 | lake_pct | 492-500 | 3 | 6.47 | 0.2..3.0 | 0.278 |
| 104 | 6 | lake_max_mkm2 | 440-456 | 5 | 2.08 | -..1.0 | 0.259 |
| 106 | 6 | lake_max_mkm2 | 328-328 | 1 | 2.19 | -..1.0 | 0.248 |
| 108 | 6 | lake_max_mkm2 | 360-368 | 3 | 2.04 | -..1.0 | 0.233 |
| 108 | 6 | lake_max_mkm2 | 344-348 | 2 | 1.98 | -..1.0 | 0.212 |
| 101 | 6 | inland_pct | 300-500 | 51 | 1.12 | 8..30 | 0.189 |
| 102 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 105 | 6 | inland_pct | 300-500 | 51 | 1.52 | 8..30 | 0.178 |
| 107 | 6 | inland_pct | 328-500 | 41 | 0.83 | 8..30 | 0.171 |
| 106 | 6 | lake_max_mkm2 | 464-476 | 3 | 1.73 | -..1.0 | 0.164 |
| 108 | 6 | inland_pct | 308-500 | 46 | 1.65 | 8..30 | 0.163 |
| 103 | 6 | inland_pct | 344-500 | 39 | 1.15 | 8..30 | 0.159 |
| 104 | 6 | lake_pct | 312-312 | 1 | 5.06 | 0.2..3.0 | 0.153 |
| 102 | 6 | inland_pct | 328-484 | 37 | 1.65 | 8..30 | 0.142 |
| 106 | 6 | inland_pct | 300-380 | 19 | 0.46 | 8..30 | 0.12 |
| 108 | 6 | lake_max_mkm2 | 300-304 | 2 | 1.52 | -..1.0 | 0.112 |
| 106 | 6 | inland_pct | 392-468 | 20 | 1.47 | 8..30 | 0.106 |
| 107 | 6 | lake_max_mkm2 | 468-468 | 1 | 1.49 | -..1.0 | 0.103 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 101, L6 (run 3a6bcf)

![seed 101 L6](seed101_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.47 | 34.27 | 35.49 |  |
| cont_pct | 38.99 | 40.78 | 42.28 |  |
| cont_km | 32.77 | 33.69 | 35.01 |  |
| plates | 7.00 | 10.00 | 11.00 |  |
| ocean_age | 51.70 | 60.00 | 66.80 |  |
| speed | 3.28 | 4.58 | 5.59 |  |
| sea_level | -49.50 | -0.20 | 84.90 |  |
| sea_ice_m | -17.20 | -1.10 | -0.00 |  |
| sea_tect_m | -37.80 | 3.30 | 85.00 |  |
| ice_pct | 0.00 | 0.10 | 1.40 |  |
| temp | 13.80 | 17.30 | 20.00 |  |
| co2 | -1.28 | -0.69 | 0.10 |  |
| dry_pct | 19.61 | 26.00 | 35.15 |  |
| inland_pct | 1.12 | 3.75 | 6.87 | 300-500: 1.12 |
| lake_pct | 0.12 | 0.30 | 1.13 | 320-320: 0.17; 340-344: 0.12; 360-384: 0.16; 408-416: 0.15; +1 more |
| lake_max_mkm2 | 0.01 | 0.05 | 0.75 |  |
| max_elev_km | 3.71 | 4.81 | 8.72 |  |
| trees_pct | 15.24 | 24.44 | 38.79 |  |
| npp | 219.20 | 324.05 | 334.50 |  |
| landmasses | 4.00 | 7.00 | 12.00 |  |
| largest_pct | 13.40 | 13.90 | 28.50 |  |

### Seed 102, L6 (run d8f484)

![seed 102 L6](seed102_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.95 | 33.34 | 34.98 |  |
| cont_pct | 39.97 | 41.05 | 41.85 |  |
| cont_km | 32.39 | 32.97 | 34.17 |  |
| plates | 7.00 | 10.00 | 13.00 |  |
| ocean_age | 51.20 | 58.10 | 94.70 |  |
| speed | 3.09 | 4.10 | 5.50 |  |
| sea_level | -271.50 | 21.90 | 106.80 | 300-332: -271.50 |
| sea_ice_m | -25.40 | -7.50 | -0.80 |  |
| sea_tect_m | -251.10 | 29.40 | 111.00 | 312-320: -251.10 |
| ice_pct | 0.10 | 0.50 | 1.90 |  |
| temp | 12.80 | 16.60 | 18.80 |  |
| co2 | -0.62 | 0.42 | 1.49 |  |
| dry_pct | 18.91 | 24.98 | 27.75 |  |
| inland_pct | 1.65 | 4.56 | 12.28 | 300-316: 3.47; 328-484: 1.65; 496-500: 5.87 |
| lake_pct | 0.15 | 0.41 | 2.03 | 376-376: 0.15 |
| lake_max_mkm2 | 0.03 | 0.11 | 2.89 | 320-320: 2.34; 452-452: 1.01; 488-488: 2.89 |
| max_elev_km | 4.87 | 6.38 | 7.57 |  |
| trees_pct | 26.87 | 34.51 | 46.67 |  |
| npp | 217.00 | 294.15 | 334.30 |  |
| landmasses | 6.00 | 12.00 | 16.00 |  |
| largest_pct | 7.00 | 12.30 | 34.80 |  |

### Seed 103, L6 (run 9a529d)

![seed 103 L6](seed103_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.64 | 32.19 | 33.84 |  |
| cont_pct | 37.18 | 38.95 | 40.00 |  |
| cont_km | 34.30 | 34.81 | 36.19 |  |
| plates | 10.00 | 15.00 | 16.00 |  |
| ocean_age | 47.50 | 53.40 | 68.70 |  |
| speed | 3.44 | 4.63 | 5.58 |  |
| sea_level | -316.00 | 25.50 | 154.70 | 496-500: -316.00 |
| sea_ice_m | -317.20 | -92.50 | -6.40 | 316-336: -317.20; 500-500: -271.50 |
| sea_tect_m | -44.50 | 132.60 | 161.10 |  |
| ice_pct | 0.40 | 3.10 | 8.90 |  |
| temp | 8.40 | 12.20 | 19.90 |  |
| co2 | -1.75 | -0.75 | 0.94 |  |
| dry_pct | 17.10 | 25.20 | 32.41 |  |
| inland_pct | 1.15 | 4.61 | 9.77 | 300-300: 7.56; 312-324: 5.52; 344-500: 1.15 |
| lake_pct | 0.17 | 0.43 | 1.27 | 348-348: 0.19; 420-420: 0.17 |
| lake_max_mkm2 | 0.03 | 0.09 | 1.43 | 412-412: 1.43 |
| max_elev_km | 4.53 | 6.71 | 9.19 |  |
| trees_pct | 14.11 | 26.47 | 46.75 |  |
| npp | 314.00 | 324.50 | 348.00 |  |
| landmasses | 3.00 | 6.00 | 10.00 |  |
| largest_pct | 10.40 | 17.60 | 33.70 |  |

### Seed 104, L6 (run c3dc19)

![seed 104 L6](seed104_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.45 | 33.29 | 34.17 |  |
| cont_pct | 37.26 | 39.32 | 39.92 |  |
| cont_km | 33.95 | 34.22 | 36.08 |  |
| plates | 9.00 | 11.00 | 13.00 |  |
| ocean_age | 41.20 | 55.80 | 72.00 |  |
| speed | 3.45 | 4.28 | 6.72 |  |
| sea_level | -187.50 | 75.30 | 221.50 |  |
| sea_ice_m | -82.40 | -6.00 | -0.00 |  |
| sea_tect_m | -106.50 | 84.70 | 221.60 |  |
| ice_pct | 0.00 | 0.50 | 4.10 |  |
| temp | 11.30 | 14.80 | 20.40 |  |
| co2 | -1.01 | 0.02 | 0.64 |  |
| dry_pct | 19.00 | 27.25 | 40.43 |  |
| inland_pct | 2.30 | 6.20 | 16.91 | 316-360: 2.72; 372-380: 5.58; 392-424: 3.22; 436-500: 2.30 |
| lake_pct | 0.26 | 0.68 | 5.06 | 312-312: 5.06 |
| lake_max_mkm2 | 0.03 | 0.24 | 7.89 | 312-312: 7.89; 360-360: 1.05; 388-388: 1.20; 428-428: 1.46; +1 more |
| max_elev_km | 4.21 | 6.85 | 8.40 |  |
| trees_pct | 18.38 | 32.20 | 37.95 |  |
| npp | 192.10 | 304.60 | 338.40 | 432-436: 192.10 |
| landmasses | 1.00 | 4.00 | 9.00 | 300-340: 1; 352-356: 2; 376-376: 2 |
| largest_pct | 17.70 | 28.10 | 34.20 |  |

### Seed 105, L6 (run fa13a3)

![seed 105 L6](seed105_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.90 | 33.59 | 34.79 |  |
| cont_pct | 38.18 | 41.05 | 42.75 |  |
| cont_km | 32.72 | 33.39 | 34.92 |  |
| plates | 8.00 | 10.00 | 14.00 |  |
| ocean_age | 52.10 | 67.40 | 72.10 |  |
| speed | 2.00 | 3.85 | 4.86 |  |
| sea_level | -133.10 | -39.00 | 45.30 |  |
| sea_ice_m | -54.00 | -21.50 | -9.40 |  |
| sea_tect_m | -82.90 | -21.70 | 64.30 |  |
| ice_pct | 0.80 | 1.60 | 3.10 |  |
| temp | 12.60 | 15.30 | 17.40 |  |
| co2 | -0.30 | 0.29 | 1.32 |  |
| dry_pct | 12.14 | 14.71 | 22.85 |  |
| inland_pct | 1.52 | 4.65 | 7.71 | 300-500: 1.52 |
| lake_pct | 0.42 | 0.99 | 1.83 |  |
| lake_max_mkm2 | 0.04 | 0.20 | 1.21 | 404-404: 1.08; 468-476: 1.18; 496-496: 1.21 |
| max_elev_km | 4.45 | 5.55 | 8.43 |  |
| trees_pct | 28.85 | 33.36 | 43.63 |  |
| npp | 290.10 | 351.50 | 365.50 |  |
| landmasses | 5.00 | 11.00 | 17.00 |  |
| largest_pct | 12.50 | 20.30 | 27.30 |  |

### Seed 106, L6 (run 4b705b)

![seed 106 L6](seed106_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.91 | 33.05 | 34.66 |  |
| cont_pct | 39.88 | 41.12 | 42.05 |  |
| cont_km | 31.87 | 32.68 | 33.73 |  |
| plates | 11.00 | 13.00 | 17.00 |  |
| ocean_age | 40.70 | 53.50 | 72.50 |  |
| speed | 3.04 | 4.58 | 6.03 |  |
| sea_level | -43.80 | 123.80 | 203.00 |  |
| sea_ice_m | -13.10 | -1.50 | -0.00 |  |
| sea_tect_m | -41.90 | 128.20 | 209.10 |  |
| ice_pct | 0.00 | 0.10 | 1.40 |  |
| temp | 12.40 | 17.00 | 20.90 |  |
| co2 | -0.20 | 0.69 | 1.38 |  |
| dry_pct | 19.00 | 26.37 | 39.25 |  |
| inland_pct | 0.46 | 4.44 | 15.31 | 300-380: 0.46; 392-468: 1.47; 480-488: 4.89 |
| lake_pct | 0.06 | 0.27 | 6.47 | 332-352: 0.12; 364-376: 0.14; 388-428: 0.06; 492-500: 6.47 |
| lake_max_mkm2 | 0.01 | 0.06 | 10.35 | 328-328: 2.19; 384-384: 4.12; 464-476: 1.73; 492-500: 10.35 |
| max_elev_km | 3.57 | 4.67 | 8.39 |  |
| trees_pct | 19.27 | 29.70 | 37.34 |  |
| npp | 221.20 | 349.60 | 369.40 |  |
| landmasses | 4.00 | 8.00 | 16.00 |  |
| largest_pct | 10.10 | 19.10 | 30.60 |  |

### Seed 107, L6 (run 4defed)

![seed 107 L6](seed107_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.16 | 32.19 | 33.07 |  |
| cont_pct | 38.31 | 40.20 | 41.35 |  |
| cont_km | 33.15 | 33.82 | 35.54 |  |
| plates | 10.00 | 14.00 | 18.00 |  |
| ocean_age | 45.20 | 56.10 | 72.80 |  |
| speed | 3.37 | 4.34 | 5.41 |  |
| sea_level | -51.00 | 68.50 | 182.70 |  |
| sea_ice_m | -68.10 | -8.60 | -0.00 |  |
| sea_tect_m | -50.70 | 80.70 | 183.70 |  |
| ice_pct | 0.00 | 0.60 | 3.90 |  |
| temp | 11.10 | 14.40 | 17.00 |  |
| co2 | -0.61 | -0.15 | 0.90 |  |
| dry_pct | 13.30 | 22.37 | 38.08 |  |
| inland_pct | 0.83 | 5.14 | 13.41 | 304-304: 7.93; 328-500: 0.83 |
| lake_pct | 0.13 | 0.47 | 3.56 | 304-312: 0.13; 332-340: 0.16; 356-364: 0.14; 384-384: 0.15; +1 more |
| lake_max_mkm2 | 0.01 | 0.19 | 5.52 | 412-428: 5.52; 468-468: 1.49 |
| max_elev_km | 4.12 | 5.38 | 8.51 |  |
| trees_pct | 20.88 | 37.29 | 44.83 |  |
| npp | 259.20 | 327.40 | 346.80 |  |
| landmasses | 7.00 | 12.00 | 19.00 |  |
| largest_pct | 9.70 | 17.40 | 25.70 |  |

### Seed 108, L6 (run 950c68)

![seed 108 L6](seed108_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.57 | 33.42 | 34.33 |  |
| cont_pct | 39.09 | 39.96 | 40.80 |  |
| cont_km | 33.38 | 33.90 | 34.89 |  |
| plates | 10.00 | 13.00 | 16.00 |  |
| ocean_age | 46.20 | 53.50 | 74.30 |  |
| speed | 2.80 | 4.13 | 5.25 |  |
| sea_level | -122.50 | 42.30 | 131.60 |  |
| sea_ice_m | -48.10 | -22.10 | -5.60 |  |
| sea_tect_m | -114.30 | 67.60 | 141.10 |  |
| ice_pct | 0.40 | 1.40 | 3.00 |  |
| temp | 10.60 | 14.80 | 20.10 |  |
| co2 | -0.60 | 0.29 | 1.51 |  |
| dry_pct | 13.71 | 21.37 | 32.88 |  |
| inland_pct | 1.65 | 4.43 | 12.13 | 308-500: 1.65 |
| lake_pct | 0.21 | 0.50 | 2.29 |  |
| lake_max_mkm2 | 0.03 | 0.10 | 2.04 | 300-304: 1.52; 344-348: 1.98; 360-368: 2.04 |
| max_elev_km | 4.09 | 5.52 | 8.48 |  |
| trees_pct | 19.74 | 29.39 | 52.31 | 360-372: 52.31 |
| npp | 247.50 | 303.80 | 329.80 |  |
| landmasses | 4.00 | 7.00 | 9.00 |  |
| largest_pct | 15.70 | 19.70 | 26.40 |  |

## Determinism

Seed 101 L6 re-run to 100 Myr (run 31f57a) against the sweep's run 3a6bcf: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
