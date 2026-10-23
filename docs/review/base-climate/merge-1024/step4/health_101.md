# Health sweep 2026-10-23 13:39

Commit 555883d. 8 runs (default params, `--every 4`) at 8 workers x 2 numba threads; simulations 12.5 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 500 | 39884d | 750 | 136 / 408 | 14.6 | 0 | 17.6 | 0.97 | 41.2 | 5.9 | F | ok | 51.0 |
| 102 | 6 | 500 | 7da3f4 | 640 | 140 / 392 | 5.9 | 0 | 5.9 | 0.966 | 0.0 | 0.0 | ok | ok | 27.5 |
| 103 | 6 | 500 | e1d450 | 692 | 128 / 424 | 10.9 | 0 | 3.9 | 0.984 | 37.3 | 0.0 | F | ok | 62.7 |
| 104 | 6 | 500 | 332a04 | 696 | 124 / 432 | 11.1 | 0 | 3.9 | 0.933 | 0.0 | 0.0 | ok | ok | 35.3 |
| 105 | 6 | 500 | 559a25 | 711 | 132 / 376 | 6.4 | 0 | 29.4 | 0.96 | 0.0 | 0.0 | ok | ok | 11.8 |
| 106 | 6 | 500 | 39bd85 | 647 | 132 / 396 | 11.7 | 0 | 3.9 | 0.982 | 47.1 | 0.0 | ok | F: icehouse 80% of the time, outside 5-70% | 80.4 |
| 107 | 6 | 500 | 57bfac | 700 | 132 / 404 | 6.4 | 0 | 3.9 | 0.957 | 23.5 | 0.0 | ok | F: icehouse 71% of the time, outside 5-70% | 70.6 |
| 108 | 6 | 500 | d57f66 | 749 | 128 / 376 | 10.2 | 0 | 21.6 | 0.973 | 11.8 | 0.0 | ok | F: icehouse 86% of the time, outside 5-70% | 86.3 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 6 | 33.0 | 40.8 | 33.7 | 11.0 | 57.7 | 3.5 | 48.6 | -35.0 | 83.5 | 1.8 | 11.8 | -1.4 | 24.4 | 5.8 | 0.5 | 0.1 | 5.6 | 7.8 | 185.4 | 9.0 | 25.4 |
| 102 | 6 | 32.8 | 40.7 | 33.2 | 11.0 | 47.1 | 4.1 | 147.9 | -12.6 | 171.1 | 0.9 | 15.7 | -0.0 | 29.3 | 5.0 | 0.4 | 0.1 | 4.7 | 30.9 | 314.5 | 9.0 | 15.6 |
| 103 | 6 | 31.0 | 38.6 | 34.9 | 15.0 | 43.7 | 4.7 | 152.5 | -25.4 | 175.3 | 1.5 | 14.9 | -0.2 | 26.9 | 3.7 | 0.5 | 0.1 | 5.7 | 20.1 | 357.0 | 10.0 | 11.5 |
| 104 | 6 | 32.1 | 41.1 | 32.7 | 10.0 | 63.2 | 4.0 | 5.4 | -4.6 | 24.6 | 0.4 | 17.4 | 0.2 | 22.8 | 3.8 | 0.3 | 0.1 | 5.4 | 26.5 | 369.1 | 10.0 | 15.4 |
| 105 | 6 | 34.0 | 40.7 | 33.2 | 11.0 | 60.2 | 4.5 | -7.1 | -13.5 | 4.2 | 1.2 | 16.5 | 0.4 | 22.0 | 4.6 | 0.6 | 0.2 | 5.6 | 32.7 | 352.4 | 8.0 | 19.0 |
| 106 | 6 | 32.9 | 39.6 | 34.2 | 10.0 | 60.8 | 5.6 | -109.0 | -77.6 | 31.8 | 3.8 | 14.4 | 0.1 | 20.8 | 3.6 | 0.4 | 0.1 | 6.1 | 38.0 | 346.8 | 6.0 | 19.0 |
| 107 | 6 | 32.7 | 39.9 | 33.7 | 11.0 | 62.6 | 4.0 | -64.4 | -63.2 | 22.3 | 2.3 | 12.4 | -0.1 | 27.0 | 5.0 | 0.5 | 0.1 | 6.4 | 32.2 | 298.4 | 6.0 | 27.8 |
| 108 | 6 | 33.4 | 40.3 | 33.9 | 13.0 | 52.2 | 4.3 | 10.7 | -59.0 | 112.5 | 3.2 | 14.9 | 0.4 | 20.1 | 4.9 | 0.5 | 0.1 | 5.0 | 33.7 | 336.8 | 5.0 | 17.9 |

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

## Top outliers (of 96 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 105 | 6 | giant_lake_frames | run | - | 29.40 | -..5 | 4.88 |
| 106 | 6 | sea_ice_below_150 | run | - | 47.10 | -..10 | 3.71 |
| 108 | 6 | giant_lake_frames | run | - | 21.60 | -..5 | 3.32 |
| 101 | 6 | sea_ice_below_150 | run | - | 41.20 | -..10 | 3.12 |
| 103 | 6 | sea_ice_below_150 | run | - | 37.30 | -..10 | 2.73 |
| 101 | 6 | giant_lake_frames | run | - | 17.60 | -..5 | 2.52 |
| 101 | 6 | low_plates | run | - | 5.90 | -..2 | 1.95 |
| 107 | 6 | sea_ice_below_150 | run | - | 23.50 | -..10 | 1.35 |
| 105 | 6 | lake_max_mkm2 | 464-500 | 10 | 5.63 | -..1.0 | 1.293 |
| 108 | 6 | lake_max_mkm2 | 392-392 | 1 | 7.17 | -..1.0 | 1.283 |
| 108 | 6 | lake_max_mkm2 | 308-336 | 8 | 4.96 | -..1.0 | 1.042 |
| 105 | 6 | lake_max_mkm2 | 452-452 | 1 | 3.26 | -..1.0 | 0.47 |
| 101 | 6 | lake_max_mkm2 | 336-348 | 3 | 3.05 | -..1.0 | 0.459 |
| 106 | 6 | lake_max_mkm2 | 300-300 | 1 | 2.84 | -..1.0 | 0.382 |
| 101 | 6 | lake_max_mkm2 | 416-416 | 1 | 2.73 | -..1.0 | 0.359 |
| 101 | 6 | sea_level | 420-500 | 21 | -758.80 | -250..300 | 0.339 |
| 101 | 6 | sea_ice_m | 420-500 | 21 | -444.70 | -250..- | 0.286 |
| 105 | 6 | lake_max_mkm2 | 424-424 | 1 | 2.14 | -..1.0 | 0.237 |
| 106 | 6 | inland_pct | 340-500 | 40 | 0.00 | 8..30 | 0.188 |
| 106 | 6 | lake_max_mkm2 | 440-440 | 1 | 1.88 | -..1.0 | 0.183 |
| 103 | 6 | inland_pct | 324-500 | 44 | 0.71 | 8..30 | 0.182 |
| 102 | 6 | giant_lake_frames | run | - | 5.90 | -..5 | 0.18 |
| 108 | 6 | sea_ice_below_150 | run | - | 11.80 | -..10 | 0.18 |
| 104 | 6 | inland_pct | 300-500 | 50 | 1.41 | 8..30 | 0.179 |
| 103 | 6 | lake_max_mkm2 | 320-320 | 1 | 1.85 | -..1.0 | 0.178 |
| 106 | 6 | sea_ice_m | 488-500 | 4 | -439.40 | -250..- | 0.176 |
| 108 | 6 | lake_pct | 392-392 | 1 | 5.21 | 0.2..3.0 | 0.164 |
| 105 | 6 | lake_max_mkm2 | 332-332 | 1 | 1.76 | -..1.0 | 0.157 |
| 108 | 6 | inland_pct | 340-500 | 39 | 1.30 | 8..30 | 0.155 |
| 105 | 6 | inland_pct | 324-460 | 32 | 0.86 | 8..30 | 0.147 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 101, L6 (run 39884d)

![seed 101 L6](seed101_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.09 | 33.00 | 34.82 |  |
| cont_pct | 38.22 | 40.76 | 41.28 |  |
| cont_km | 33.07 | 33.69 | 35.84 |  |
| plates | 4.00 | 11.00 | 16.00 | 464-472: 4 |
| ocean_age | 37.80 | 57.70 | 125.50 | 496-500: 125.50 |
| speed | 1.21 | 3.46 | 5.35 | 472-500: 1.21 |
| sea_level | -758.80 | 48.60 | 214.10 | 420-500: -758.80 |
| sea_ice_m | -444.70 | -35.00 | -6.80 | 420-500: -444.70 |
| sea_tect_m | -340.60 | 83.50 | 221.40 | 460-500: -340.60 |
| ice_pct | 0.50 | 1.80 | 12.70 | 428-500: 12.70 |
| temp | 3.70 | 11.80 | 18.30 | 428-496: 3.70 |
| co2 | -2.90 | -1.40 | -0.18 |  |
| dry_pct | 13.77 | 24.42 | 38.06 |  |
| inland_pct | 2.34 | 5.83 | 17.16 | 300-340: 2.80; 352-464: 2.34; 480-500: 2.68 |
| lake_pct | 0.23 | 0.46 | 2.54 |  |
| lake_max_mkm2 | 0.03 | 0.14 | 3.05 | 336-348: 3.05; 416-416: 2.73; 452-476: 1.51 |
| max_elev_km | 4.83 | 5.62 | 9.06 |  |
| trees_pct | 1.84 | 7.76 | 21.11 | 324-428: 1.84 |
| npp | 121.00 | 185.45 | 206.30 | 408-408: 121.00; 424-500: 180.20 |
| landmasses | 5.00 | 9.00 | 13.00 |  |
| largest_pct | 14.00 | 25.40 | 29.30 |  |

### Seed 102, L6 (run 7da3f4)

![seed 102 L6](seed102_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.53 | 32.84 | 33.51 |  |
| cont_pct | 39.19 | 40.72 | 41.37 |  |
| cont_km | 32.62 | 33.24 | 34.64 |  |
| plates | 8.00 | 11.00 | 16.00 |  |
| ocean_age | 42.40 | 47.10 | 58.00 |  |
| speed | 3.24 | 4.06 | 5.28 |  |
| sea_level | 46.20 | 147.90 | 186.50 |  |
| sea_ice_m | -38.10 | -12.60 | -2.60 |  |
| sea_tect_m | 53.40 | 171.10 | 199.00 |  |
| ice_pct | 0.20 | 0.90 | 1.60 |  |
| temp | 11.50 | 15.70 | 17.40 |  |
| co2 | -0.62 | -0.02 | 0.53 |  |
| dry_pct | 25.26 | 29.30 | 40.70 |  |
| inland_pct | 2.48 | 5.03 | 12.09 | 300-500: 2.48 |
| lake_pct | 0.12 | 0.36 | 2.11 | 380-380: 0.20; 412-420: 0.12; 444-444: 0.19; 456-456: 0.18 |
| lake_max_mkm2 | 0.01 | 0.06 | 1.51 | 344-344: 1.06; 432-440: 1.51 |
| max_elev_km | 2.81 | 4.67 | 7.26 |  |
| trees_pct | 15.75 | 30.87 | 48.92 |  |
| npp | 212.60 | 314.55 | 372.70 |  |
| landmasses | 4.00 | 9.00 | 13.00 |  |
| largest_pct | 9.40 | 15.60 | 31.80 |  |

### Seed 103, L6 (run e1d450)

![seed 103 L6](seed103_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.10 | 30.99 | 33.53 |  |
| cont_pct | 36.18 | 38.61 | 40.86 |  |
| cont_km | 33.69 | 34.92 | 37.39 |  |
| plates | 10.00 | 15.00 | 18.00 |  |
| ocean_age | 38.20 | 43.70 | 64.10 |  |
| speed | 3.26 | 4.66 | 5.42 |  |
| sea_level | -387.70 | 152.50 | 202.40 | 300-344: -387.70 |
| sea_ice_m | -355.20 | -25.40 | -0.80 | 304-344: -355.20 |
| sea_tect_m | -98.30 | 175.30 | 211.20 |  |
| ice_pct | 0.10 | 1.50 | 10.20 | 320-328: 10.20 |
| temp | 8.00 | 14.90 | 18.90 |  |
| co2 | -1.31 | -0.20 | 0.86 |  |
| dry_pct | 13.70 | 26.95 | 33.48 |  |
| inland_pct | 0.71 | 3.71 | 23.62 | 324-500: 0.71 |
| lake_pct | 0.17 | 0.45 | 2.21 | 436-436: 0.17 |
| lake_max_mkm2 | 0.01 | 0.06 | 1.85 | 304-304: 1.66; 320-320: 1.85 |
| max_elev_km | 3.86 | 5.71 | 8.49 |  |
| trees_pct | 1.12 | 20.06 | 37.64 | 400-468: 1.12 |
| npp | 280.90 | 357.05 | 466.10 |  |
| landmasses | 4.00 | 10.00 | 17.00 |  |
| largest_pct | 8.60 | 11.50 | 32.90 |  |

### Seed 104, L6 (run 332a04)

![seed 104 L6](seed104_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.64 | 32.10 | 34.08 |  |
| cont_pct | 39.36 | 41.11 | 42.82 |  |
| cont_km | 31.59 | 32.71 | 33.57 |  |
| plates | 7.00 | 10.00 | 12.00 |  |
| ocean_age | 48.20 | 63.20 | 90.70 |  |
| speed | 2.77 | 3.96 | 4.85 |  |
| sea_level | -254.90 | 5.40 | 161.90 | 500-500: -254.90 |
| sea_ice_m | -63.80 | -4.60 | -0.00 |  |
| sea_tect_m | -203.00 | 24.60 | 161.90 |  |
| ice_pct | 0.00 | 0.40 | 3.70 |  |
| temp | 10.80 | 17.40 | 21.90 |  |
| co2 | -0.89 | 0.16 | 1.03 |  |
| dry_pct | 19.48 | 22.81 | 28.35 |  |
| inland_pct | 1.41 | 3.83 | 9.21 | 300-500: 1.41 |
| lake_pct | 0.11 | 0.33 | 1.39 | 308-308: 0.18; 336-336: 0.20; 348-348: 0.18; 384-424: 0.11 |
| lake_max_mkm2 | 0.01 | 0.05 | 1.40 | 340-340: 1.36; 452-452: 1.40 |
| max_elev_km | 4.48 | 5.43 | 8.54 |  |
| trees_pct | 10.81 | 26.51 | 50.73 | 436-436: 50.73 |
| npp | 180.30 | 369.10 | 421.20 | 456-456: 180.30 |
| landmasses | 4.00 | 10.00 | 15.00 |  |
| largest_pct | 9.60 | 15.40 | 22.00 |  |

### Seed 105, L6 (run 559a25)

![seed 105 L6](seed105_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.42 | 33.95 | 34.80 |  |
| cont_pct | 39.63 | 40.72 | 41.33 |  |
| cont_km | 32.61 | 33.25 | 34.34 |  |
| plates | 7.00 | 11.00 | 13.00 |  |
| ocean_age | 41.90 | 60.20 | 76.10 |  |
| speed | 3.40 | 4.51 | 5.52 |  |
| sea_level | -172.50 | -7.10 | 147.60 |  |
| sea_ice_m | -27.60 | -13.50 | -9.40 |  |
| sea_tect_m | -154.60 | 4.20 | 157.80 |  |
| ice_pct | 0.70 | 1.20 | 2.30 |  |
| temp | 13.30 | 16.50 | 19.70 |  |
| co2 | -0.24 | 0.45 | 1.62 |  |
| dry_pct | 16.90 | 21.97 | 33.88 |  |
| inland_pct | 0.86 | 4.61 | 19.54 | 300-300: 6.29; 312-312: 7.21; 324-460: 0.86 |
| lake_pct | 0.26 | 0.58 | 4.18 | 452-452: 3.16; 464-468: 3.05; 480-500: 4.18 |
| lake_max_mkm2 | 0.04 | 0.17 | 5.63 | 320-320: 1.66; 332-332: 1.76; 392-392: 1.03; 424-424: 2.14; +2 more |
| max_elev_km | 4.00 | 5.56 | 7.03 |  |
| trees_pct | 23.17 | 32.68 | 47.94 |  |
| npp | 325.90 | 352.35 | 398.50 |  |
| landmasses | 4.00 | 8.00 | 11.00 |  |
| largest_pct | 10.00 | 19.00 | 24.40 |  |

### Seed 106, L6 (run 39bd85)

![seed 106 L6](seed106_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.76 | 32.89 | 34.27 |  |
| cont_pct | 37.56 | 39.63 | 40.96 |  |
| cont_km | 33.02 | 34.20 | 35.83 |  |
| plates | 5.00 | 10.00 | 12.00 |  |
| ocean_age | 47.90 | 60.80 | 82.40 |  |
| speed | 1.27 | 5.63 | 6.30 | 488-500: 1.27 |
| sea_level | -500.90 | -109.00 | 21.30 | 488-500: -500.90 |
| sea_ice_m | -439.40 | -77.60 | -1.10 | 488-500: -439.40 |
| sea_tect_m | -160.50 | 31.80 | 121.40 |  |
| ice_pct | 0.10 | 3.80 | 14.50 | 488-500: 14.50 |
| temp | 7.70 | 14.40 | 19.40 | 496-500: 7.70 |
| co2 | -0.68 | 0.12 | 1.12 |  |
| dry_pct | 13.86 | 20.80 | 41.21 |  |
| inland_pct | 0.00 | 3.58 | 18.14 | 308-328: 3.66; 340-500: 0.00 |
| lake_pct | 0.15 | 0.36 | 1.84 | 308-308: 0.19; 412-420: 0.15; 436-436: 0.18 |
| lake_max_mkm2 | 0.03 | 0.09 | 2.84 | 300-300: 2.84; 440-440: 1.88 |
| max_elev_km | 4.13 | 6.12 | 8.87 |  |
| trees_pct | 21.38 | 37.98 | 53.57 | 408-416: 53.57 |
| npp | 218.60 | 346.80 | 450.60 |  |
| landmasses | 3.00 | 6.00 | 13.00 |  |
| largest_pct | 10.90 | 19.00 | 34.90 |  |

### Seed 107, L6 (run 57bfac)

![seed 107 L6](seed107_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.19 | 32.74 | 33.77 |  |
| cont_pct | 38.95 | 39.85 | 41.33 |  |
| cont_km | 32.97 | 33.72 | 34.24 |  |
| plates | 9.00 | 11.00 | 14.00 |  |
| ocean_age | 43.30 | 62.60 | 78.90 |  |
| speed | 2.53 | 3.99 | 5.49 |  |
| sea_level | -154.70 | -64.40 | 88.20 |  |
| sea_ice_m | -259.90 | -63.20 | -10.20 | 388-396: -259.90 |
| sea_tect_m | -85.90 | 22.30 | 157.50 |  |
| ice_pct | 0.70 | 2.30 | 7.20 |  |
| temp | 9.60 | 12.40 | 16.00 |  |
| co2 | -1.61 | -0.13 | 0.26 |  |
| dry_pct | 19.64 | 26.97 | 37.80 |  |
| inland_pct | 1.45 | 4.95 | 9.70 | 300-384: 1.45; 400-500: 2.62 |
| lake_pct | 0.22 | 0.49 | 1.71 |  |
| lake_max_mkm2 | 0.03 | 0.10 | 1.06 | 388-388: 1.06; 484-484: 1.06 |
| max_elev_km | 4.07 | 6.43 | 7.96 |  |
| trees_pct | 6.36 | 32.17 | 45.53 | 320-320: 7.45; 440-440: 6.36 |
| npp | 207.60 | 298.40 | 377.30 |  |
| landmasses | 2.00 | 6.00 | 10.00 | 428-428: 2 |
| largest_pct | 17.20 | 27.80 | 33.80 |  |

### Seed 108, L6 (run d57f66)

![seed 108 L6](seed108_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.01 | 33.42 | 34.17 |  |
| cont_pct | 38.58 | 40.33 | 41.29 |  |
| cont_km | 33.09 | 33.92 | 35.10 |  |
| plates | 12.00 | 13.00 | 15.00 |  |
| ocean_age | 39.40 | 52.20 | 62.60 |  |
| speed | 3.14 | 4.31 | 5.21 |  |
| sea_level | -57.60 | 10.70 | 204.90 |  |
| sea_ice_m | -174.80 | -59.00 | -8.90 |  |
| sea_tect_m | -13.60 | 112.50 | 217.30 |  |
| ice_pct | 0.80 | 3.20 | 6.10 |  |
| temp | 10.10 | 14.90 | 20.30 |  |
| co2 | -0.40 | 0.35 | 1.41 |  |
| dry_pct | 13.02 | 20.05 | 27.66 |  |
| inland_pct | 1.30 | 4.91 | 20.00 | 300-308: 4.28; 340-500: 1.30 |
| lake_pct | 0.22 | 0.52 | 5.21 | 308-316: 4.82; 336-336: 3.52; 392-392: 5.21 |
| lake_max_mkm2 | 0.04 | 0.15 | 7.17 | 308-336: 4.96; 392-392: 7.17; 424-424: 1.11; 444-444: 1.32 |
| max_elev_km | 4.15 | 5.05 | 6.17 |  |
| trees_pct | 22.29 | 33.66 | 55.38 | 360-376: 55.38 |
| npp | 233.20 | 336.80 | 417.70 |  |
| landmasses | 2.00 | 5.00 | 9.00 | 300-300: 2 |
| largest_pct | 11.70 | 17.90 | 34.20 |  |

## Determinism

Seed 101 L6 re-run to 100 Myr (run 213cb6) against the sweep's run 39884d: 26 keyframes x 44 layers, **bit-identical** (layer hashes and frame stats).
