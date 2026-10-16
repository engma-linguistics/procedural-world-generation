# Health sweep 2026-10-15 20:27

Commit 68769e1. 8 runs (default params, `--every 4`) at 8 workers x 1 numba threads; simulations 5.0 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | 0c4968 | 298 | 132 / 412 | 12.1 | 0 | 7.1 | 0.904 | 0.0 | 0.0 |
| 2 | 6 | 500 | 624f01 | 294 | 140 / 396 | 19.1 | 0 | 4.4 | 0.906 | 0.0 | 0.0 |
| 11 | 6 | 500 | ee2b8d | 285 | 128 / 372 | 15.0 | 0 | 7.1 | 0.919 | 0.0 | 0.0 |
| 21 | 6 | 500 | 635b1e | 288 | 136 / 404 | 10.1 | 0 | 14.2 | 0.905 | 0.0 | 0.0 |
| 3199 | 6 | 500 | b97f45 | 286 | 132 / 376 | 10.6 | 0 | 7.1 | 0.89 | 0.0 | 0.0 |
| 42 | 6 | 500 | de607e | 296 | 116 / 404 | 9.8 | 0 | 16.8 | 0.9 | 0.0 | 0.0 |
| 77 | 6 | 500 | e882a5 | 295 | 124 / 416 | 12.5 | 0 | 9.7 | 0.896 | 0.0 | 0.0 |
| 505 | 6 | 500 | c4e87e | 286 | 132 / 416 | 7.6 | 0 | 7.1 | 0.917 | 0.0 | 0.0 |

## Medians by seed (after 50 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 32.6 | 38.7 | 35.9 | 14.0 | 47.4 | 4.6 | 166.0 | -3.5 | 0.6 | 15.9 | -0.3 | 27.0 | 7.4 | 1.1 | 0.1 | 5.6 | 27.0 | 291.4 | 6.0 | 19.9 |
| 2 | 6 | 33.1 | 38.4 | 35.8 | 13.0 | 48.8 | 4.4 | 193.7 | -1.8 | 0.4 | 15.4 | -0.2 | 27.1 | 6.8 | 0.8 | 0.1 | 6.4 | 27.8 | 315.3 | 7.0 | 22.4 |
| 11 | 6 | 31.7 | 38.3 | 36.3 | 12.0 | 51.5 | 4.6 | 105.4 | -9.3 | 1.6 | 13.4 | -0.3 | 25.6 | 7.8 | 0.8 | 0.1 | 6.4 | 28.9 | 232.6 | 7.0 | 24.0 |
| 21 | 6 | 33.9 | 38.8 | 35.8 | 10.0 | 53.1 | 4.6 | 85.6 | -0.7 | 0.1 | 17.0 | -0.2 | 38.7 | 8.8 | 0.8 | 0.2 | 4.8 | 21.1 | 270.3 | 5.0 | 33.3 |
| 3199 | 6 | 34.0 | 38.8 | 36.2 | 9.0 | 61.7 | 4.8 | -27.9 | -7.0 | 1.2 | 15.5 | -0.1 | 36.5 | 9.7 | 0.8 | 0.2 | 6.8 | 23.3 | 263.3 | 5.0 | 28.4 |
| 42 | 6 | 32.9 | 38.9 | 35.5 | 14.0 | 59.4 | 4.5 | 134.2 | -5.2 | 1.0 | 14.0 | -0.3 | 24.5 | 6.6 | 0.7 | 0.2 | 5.4 | 30.9 | 352.6 | 6.0 | 20.6 |
| 77 | 6 | 33.4 | 39.7 | 35.1 | 12.0 | 52.5 | 4.4 | 27.7 | -3.6 | 0.7 | 12.7 | -0.1 | 30.5 | 6.3 | 1.0 | 0.2 | 6.2 | 30.7 | 291.2 | 6.0 | 22.5 |
| 505 | 6 | 33.9 | 39.7 | 34.8 | 11.0 | 54.2 | 4.2 | 155.9 | -2.8 | 0.5 | 15.6 | -0.2 | 28.3 | 5.3 | 0.5 | 0.1 | 6.1 | 26.9 | 381.2 | 6.0 | 20.7 |

Measured on the run's keyframes (no slicing). Caveats: a keyframe's lakes and `downstream` come from the terrain before that step's erosion and deposition (PW-239), so `inland_raw_pct` (every routed end on land, as highlights counts it) runs ~2-3x `inland_pct` (ends that are closed lakes, salt pans or real pits on the frame's own elevation); lake shares are the run's lakes during the step. Land ice and land shares use cells (near-equal area).

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
| land ice, % of surface (`ice_pct`) | - | 10 | 3.10 | Earth 3.1% now (earth.EARTH_ICE), ~7-8% at the LGM |
| global mean temperature, C (`temp`) | 8 | 30 | 14.50 | Earth 14.5 C; LGM ~8 C (Tierney et al. 2020); Phanerozoic hothouses to ~30 C (Scotese et al. 2021) |
| CO2 index (ln source/sink) (`co2`) | -1.5 | 1.5 | 0.00 | the forcing's clip in earth.py (+-1.5); Earth 0 |
| arid (Koppen B), % of land (`dry_pct`) | 12 | 45 | 30 | tests/test_envelopes.py (12-45%); Earth ~30% (Beck et al. 2018) |
| land draining inland, % of ice-free land (to a closed lake, salt pan or real pit) (`inland_pct`) | 8 | 30 | 18 | Earth ~18% (overview 2.9); L6 known ~9.5-11% (PW-054, PW-243). `inland_raw_pct` (not checked) follows the stored `downstream` to any end, as highlights does: stale by a step (PW-239) |
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

## Top outliers (of 162 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 42 | 6 | giant_lake_frames | run | - | 16.80 | -..5 | 2.36 |
| 21 | 6 | giant_lake_frames | run | - | 14.20 | -..5 | 1.84 |
| 3199 | 6 | lake_max_mkm2 | 92-92 | 1 | 7.78 | -..1.0 | 1.41 |
| 3199 | 6 | lake_max_mkm2 | 76-76 | 1 | 7.35 | -..1.0 | 1.32 |
| 77 | 6 | giant_lake_frames | run | - | 9.70 | -..5 | 0.94 |
| 42 | 6 | lake_max_mkm2 | 232-240 | 3 | 4.36 | -..1.0 | 0.752 |
| 3199 | 6 | lake_max_mkm2 | 112-112 | 1 | 3.85 | -..1.0 | 0.592 |
| 2 | 6 | lake_max_mkm2 | 56-60 | 2 | 3.41 | -..1.0 | 0.521 |
| 1 | 6 | giant_lake_frames | run | - | 7.10 | -..5 | 0.42 |
| 11 | 6 | giant_lake_frames | run | - | 7.10 | -..5 | 0.42 |
| 3199 | 6 | giant_lake_frames | run | - | 7.10 | -..5 | 0.42 |
| 505 | 6 | giant_lake_frames | run | - | 7.10 | -..5 | 0.42 |
| 21 | 6 | lake_max_mkm2 | 56-64 | 3 | 2.55 | -..1.0 | 0.348 |
| 3199 | 6 | lake_max_mkm2 | 64-64 | 1 | 2.34 | -..1.0 | 0.279 |
| 3199 | 6 | lake_max_mkm2 | 124-132 | 3 | 2.24 | -..1.0 | 0.278 |
| 505 | 6 | lake_max_mkm2 | 52-96 | 8 | 2.04 | -..1.0 | 0.275 |
| 1 | 6 | lake_max_mkm2 | 152-152 | 1 | 2.29 | -..1.0 | 0.268 |
| 42 | 6 | lake_max_mkm2 | 160-172 | 4 | 2.14 | -..1.0 | 0.265 |
| 1 | 6 | lake_max_mkm2 | 408-424 | 4 | 2.13 | -..1.0 | 0.262 |
| 21 | 6 | lake_max_mkm2 | 480-500 | 5 | 2.02 | -..1.0 | 0.244 |
| 2 | 6 | lake_max_mkm2 | 244-248 | 2 | 2.12 | -..1.0 | 0.241 |
| 11 | 6 | lake_max_mkm2 | 224-224 | 1 | 2.14 | -..1.0 | 0.237 |
| 505 | 6 | inland_pct | 288-500 | 53 | 1.15 | 8..30 | 0.193 |
| 77 | 6 | inland_pct | 284-500 | 52 | 1.39 | 8..30 | 0.184 |
| 77 | 6 | lake_max_mkm2 | 64-100 | 6 | 1.72 | -..1.0 | 0.178 |
| 3199 | 6 | dry_pct | 52-88 | 10 | 64.37 | 12..45 | 0.164 |
| 42 | 6 | lake_max_mkm2 | 260-260 | 1 | 1.78 | -..1.0 | 0.162 |
| 77 | 6 | lake_max_mkm2 | 112-112 | 1 | 1.76 | -..1.0 | 0.157 |
| 2 | 6 | lake_pct | 56-56 | 1 | 5.10 | 0.2..3.0 | 0.156 |
| 42 | 6 | lake_max_mkm2 | 52-56 | 2 | 1.72 | -..1.0 | 0.155 |

## Per seed: min / median / max after the 50 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run 0c4968)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.29 | 32.65 | 38.63 |  |
| cont_pct | 36.44 | 38.71 | 43.10 |  |
| cont_km | 34.43 | 35.93 | 38.52 |  |
| plates | 8.00 | 14.00 | 19.00 |  |
| ocean_age | 32.50 | 47.40 | 62.00 |  |
| speed | 3.23 | 4.62 | 7.77 |  |
| sea_level | 2.20 | 166.00 | 215.90 |  |
| sea_ice_m | -33.20 | -3.50 | -0.00 |  |
| ice_pct | 0.00 | 0.60 | 2.80 |  |
| temp | 8.40 | 15.90 | 20.50 |  |
| co2 | -0.98 | -0.30 | 0.12 |  |
| dry_pct | 11.58 | 26.99 | 50.26 | 204-220: 50.26; 312-320: 11.58 |
| inland_pct | 2.52 | 7.37 | 23.46 | 68-68: 5.88; 80-124: 2.55; 272-324: 2.52; 340-492: 3.37 |
| lake_pct | 0.06 | 1.10 | 2.50 | 84-84: 0.11; 100-104: 0.06 |
| lake_max_mkm2 | 0.01 | 0.15 | 2.29 | 60-60: 1.41; 152-152: 2.29; 336-336: 1.12; 376-376: 1.05; +1 more |
| max_elev_km | 2.04 | 5.62 | 8.26 |  |
| trees_pct | 15.22 | 27.03 | 40.27 |  |
| npp | 187.80 | 291.40 | 307.50 | 412-416: 187.80 |
| landmasses | 2.00 | 6.00 | 11.00 | 52-52: 2 |
| largest_pct | 12.10 | 19.90 | 33.30 |  |

### Seed 2, L6 (run 624f01)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.08 | 33.06 | 37.91 |  |
| cont_pct | 37.18 | 38.36 | 43.07 |  |
| cont_km | 34.34 | 35.83 | 37.94 |  |
| plates | 8.00 | 13.00 | 19.00 |  |
| ocean_age | 32.10 | 48.80 | 64.60 |  |
| speed | 2.90 | 4.40 | 7.65 |  |
| sea_level | 63.60 | 193.70 | 233.80 |  |
| sea_ice_m | -50.40 | -1.80 | -0.00 |  |
| ice_pct | 0.00 | 0.40 | 4.60 |  |
| temp | 4.50 | 15.40 | 23.60 | 480-500: 4.50 |
| co2 | -1.06 | -0.21 | 0.40 |  |
| dry_pct | 13.38 | 27.11 | 51.95 | 52-60: 51.95; 80-88: 47.39 |
| inland_pct | 2.26 | 6.82 | 35.91 | 56-156: 35.91; 176-176: 6.30; 304-340: 4.17; 364-500: 2.29 |
| lake_pct | 0.14 | 0.81 | 5.10 | 56-56: 5.10; 76-76: 0.14; 92-92: 0.15; 244-248: 3.75 |
| lake_max_mkm2 | 0.03 | 0.15 | 3.41 | 56-60: 3.41; 220-220: 1.06; 244-248: 2.12 |
| max_elev_km | 1.84 | 6.38 | 7.38 |  |
| trees_pct | 9.87 | 27.77 | 47.81 | 280-280: 9.87 |
| npp | 221.60 | 315.30 | 366.30 |  |
| landmasses | 2.00 | 7.00 | 13.00 | 52-68: 2; 200-200: 2 |
| largest_pct | 9.90 | 22.40 | 34.00 |  |

### Seed 11, L6 (run ee2b8d)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.66 | 31.67 | 38.21 |  |
| cont_pct | 36.30 | 38.29 | 42.82 |  |
| cont_km | 34.99 | 36.28 | 38.57 |  |
| plates | 5.00 | 12.00 | 18.00 |  |
| ocean_age | 33.10 | 51.50 | 83.80 |  |
| speed | 3.24 | 4.58 | 8.23 |  |
| sea_level | -170.40 | 105.40 | 215.80 |  |
| sea_ice_m | -70.50 | -9.30 | -0.00 |  |
| ice_pct | 0.00 | 1.60 | 6.80 |  |
| temp | 4.90 | 13.40 | 19.90 | 172-200: 4.90 |
| co2 | -1.20 | -0.32 | 0.15 |  |
| dry_pct | 16.38 | 25.65 | 47.15 | 60-64: 47.15 |
| inland_pct | 1.87 | 7.76 | 22.28 | 72-84: 2.75; 100-156: 3.67; 168-168: 6.85; 284-296: 7.23; +4 more |
| lake_pct | 0.22 | 0.77 | 2.53 |  |
| lake_max_mkm2 | 0.03 | 0.11 | 2.14 | 60-72: 1.42; 180-184: 1.66; 224-224: 2.14; 272-272: 1.68 |
| max_elev_km | 1.66 | 6.44 | 7.97 |  |
| trees_pct | 14.30 | 28.93 | 41.15 |  |
| npp | 199.80 | 232.60 | 316.20 | 384-384: 199.80 |
| landmasses | 2.00 | 7.00 | 16.00 | 112-112: 2; 124-128: 2 |
| largest_pct | 14.10 | 24.00 | 36.80 | 112-112: 36.80 |

### Seed 21, L6 (run 635b1e)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.02 | 33.87 | 37.97 |  |
| cont_pct | 37.85 | 38.79 | 43.43 |  |
| cont_km | 34.27 | 35.83 | 36.82 |  |
| plates | 8.00 | 10.00 | 15.00 |  |
| ocean_age | 33.20 | 53.10 | 69.30 |  |
| speed | 3.27 | 4.63 | 7.08 |  |
| sea_level | -54.00 | 85.60 | 211.70 |  |
| sea_ice_m | -6.10 | -0.70 | -0.00 |  |
| ice_pct | 0.00 | 0.10 | 1.30 |  |
| temp | 12.40 | 17.00 | 22.50 |  |
| co2 | -0.60 | -0.21 | 0.42 |  |
| dry_pct | 27.07 | 38.67 | 53.99 | 52-60: 47.85; 88-100: 51.33; 284-296: 46.38; 368-400: 53.99 |
| inland_pct | 3.69 | 8.83 | 22.58 | 52-56: 6.00; 72-72: 6.80; 84-92: 4.39; 104-112: 6.82; +9 more |
| lake_pct | 0.24 | 0.80 | 2.62 |  |
| lake_max_mkm2 | 0.03 | 0.25 | 2.55 | 56-64: 2.55; 148-164: 1.16; 180-184: 1.06; 216-216: 1.28; +3 more |
| max_elev_km | 1.94 | 4.82 | 8.37 |  |
| trees_pct | 11.57 | 21.09 | 28.26 |  |
| npp | 162.70 | 270.30 | 341.40 | 404-408: 162.70 |
| landmasses | 2.00 | 5.00 | 14.00 | 64-64: 2; 384-400: 2 |
| largest_pct | 13.30 | 33.30 | 34.10 |  |

### Seed 3199, L6 (run b97f45)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.36 | 34.03 | 38.81 |  |
| cont_pct | 36.57 | 38.76 | 42.83 |  |
| cont_km | 34.59 | 36.16 | 37.52 |  |
| plates | 6.00 | 9.00 | 12.00 |  |
| ocean_age | 35.10 | 61.70 | 74.90 |  |
| speed | 2.10 | 4.84 | 7.63 |  |
| sea_level | -117.50 | -27.90 | 187.90 |  |
| sea_ice_m | -11.60 | -7.00 | -0.00 |  |
| ice_pct | 0.00 | 1.20 | 2.00 |  |
| temp | 10.20 | 15.50 | 20.80 |  |
| co2 | -0.63 | -0.06 | 0.37 |  |
| dry_pct | 16.85 | 36.55 | 64.37 | 52-88: 64.37; 236-240: 45.99; 260-272: 45.74 |
| inland_pct | 1.97 | 9.69 | 21.73 | 80-80: 7.71; 96-120: 1.98; 136-144: 5.54; 324-400: 5.10; +1 more |
| lake_pct | 0.10 | 0.84 | 4.57 | 76-76: 4.16; 92-96: 4.57 |
| lake_max_mkm2 | 0.04 | 0.21 | 7.78 | 64-64: 2.34; 76-76: 7.35; 92-92: 7.78; 112-112: 3.85; +2 more |
| max_elev_km | 1.60 | 6.82 | 8.17 |  |
| trees_pct | 7.67 | 23.29 | 36.84 | 132-148: 7.67 |
| npp | 232.00 | 263.30 | 272.40 |  |
| landmasses | 2.00 | 5.00 | 9.00 | 52-72: 2; 152-156: 2; 192-192: 2 |
| largest_pct | 10.20 | 28.40 | 35.10 | 180-180: 35.10 |

### Seed 42, L6 (run de607e)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.28 | 32.94 | 38.24 |  |
| cont_pct | 37.53 | 38.94 | 42.82 |  |
| cont_km | 33.64 | 35.48 | 37.48 |  |
| plates | 8.00 | 14.00 | 18.00 |  |
| ocean_age | 40.50 | 59.40 | 83.30 |  |
| speed | 2.65 | 4.46 | 7.53 |  |
| sea_level | -117.40 | 134.20 | 217.60 |  |
| sea_ice_m | -15.30 | -5.20 | -0.00 |  |
| ice_pct | 0.00 | 1.00 | 2.10 |  |
| temp | 9.90 | 14.00 | 19.70 |  |
| co2 | -1.10 | -0.28 | 0.23 |  |
| dry_pct | 14.95 | 24.46 | 40.33 |  |
| inland_pct | 1.40 | 6.63 | 15.44 | 64-88: 2.80; 100-128: 1.40; 188-188: 4.82; 204-224: 6.27; +4 more |
| lake_pct | 0.17 | 0.72 | 3.28 | 64-72: 0.17; 240-240: 3.28; 452-452: 0.18 |
| lake_max_mkm2 | 0.01 | 0.19 | 4.36 | 52-56: 1.72; 92-96: 1.72; 140-140: 1.13; 160-172: 2.14; +6 more |
| max_elev_km | 1.54 | 5.38 | 8.40 |  |
| trees_pct | 22.11 | 30.87 | 39.59 |  |
| npp | 260.50 | 352.60 | 384.90 |  |
| landmasses | 2.00 | 6.00 | 14.00 | 116-116: 2 |
| largest_pct | 7.80 | 20.60 | 32.00 |  |

### Seed 77, L6 (run e882a5)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.62 | 33.44 | 38.55 |  |
| cont_pct | 37.48 | 39.72 | 42.83 |  |
| cont_km | 34.05 | 35.12 | 37.72 |  |
| plates | 5.00 | 12.00 | 17.00 |  |
| ocean_age | 34.10 | 52.50 | 75.80 |  |
| speed | 3.16 | 4.44 | 8.26 |  |
| sea_level | -178.10 | 27.70 | 190.30 |  |
| sea_ice_m | -18.70 | -3.60 | -0.00 |  |
| ice_pct | 0.00 | 0.70 | 2.20 |  |
| temp | 6.00 | 12.70 | 18.50 | 136-152: 6.00 |
| co2 | -1.40 | -0.14 | 0.14 |  |
| dry_pct | 12.64 | 30.47 | 43.84 |  |
| inland_pct | 1.39 | 6.33 | 19.06 | 80-88: 4.47; 104-108: 5.26; 120-160: 3.04; 244-244: 7.85; +1 more |
| lake_pct | 0.17 | 0.96 | 2.90 | 84-84: 0.17 |
| lake_max_mkm2 | 0.04 | 0.17 | 1.76 | 64-100: 1.72; 112-112: 1.76; 232-232: 1.23; 428-428: 1.46; +1 more |
| max_elev_km | 1.85 | 6.22 | 8.39 |  |
| trees_pct | 23.58 | 30.73 | 40.87 |  |
| npp | 249.00 | 291.25 | 305.10 |  |
| landmasses | 1.00 | 6.00 | 13.00 | 52-64: 2; 112-132: 1; 192-196: 2; 484-484: 2 |
| largest_pct | 7.10 | 22.50 | 35.70 | 124-124: 35.70 |

### Seed 505, L6 (run c4e87e)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.39 | 33.91 | 38.14 |  |
| cont_pct | 37.34 | 39.68 | 43.42 |  |
| cont_km | 33.95 | 34.84 | 37.79 |  |
| plates | 6.00 | 11.00 | 16.00 |  |
| ocean_age | 33.50 | 54.20 | 69.50 |  |
| speed | 2.81 | 4.15 | 7.72 |  |
| sea_level | -10.20 | 155.90 | 232.30 |  |
| sea_ice_m | -8.40 | -2.80 | -0.00 |  |
| ice_pct | 0.00 | 0.50 | 1.80 |  |
| temp | 11.70 | 15.60 | 19.30 |  |
| co2 | -0.63 | -0.24 | 0.12 |  |
| dry_pct | 22.90 | 28.33 | 41.55 |  |
| inland_pct | 1.15 | 5.27 | 24.74 | 68-164: 2.69; 176-176: 7.69; 192-196: 7.56; 232-232: 5.64; +3 more |
| lake_pct | 0.09 | 0.51 | 2.37 | 92-92: 0.14; 112-116: 0.09; 128-128: 0.20; 360-360: 0.20; +2 more |
| lake_max_mkm2 | 0.03 | 0.10 | 2.04 | 52-96: 2.04 |
| max_elev_km | 1.99 | 6.11 | 8.34 |  |
| trees_pct | 13.90 | 26.88 | 40.82 |  |
| npp | 184.40 | 381.25 | 416.80 | 424-432: 184.40 |
| landmasses | 2.00 | 6.00 | 12.00 | 60-60: 2 |
| largest_pct | 10.60 | 20.70 | 34.00 |  |

## Determinism

(not run)
