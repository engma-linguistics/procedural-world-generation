# Health sweep 2026-10-23 16:39

Commit None. 16 runs (default params, `--every 4`) at 6 workers x 3 numba threads; simulations 20.9 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 201 | 6 | 500 | b8371b | 424 | 140 / 412 | 9.4 | 0 | 11.8 | 0.971 | 37.3 | 0.0 | ok | ok | 66.7 |
| 202 | 6 | 500 | f31d9b | 444 | 132 / 368 | 7.1 | 0 | 31.4 | 0.956 | 0.0 | 0.0 | ok | ok | 29.4 |
| 203 | 6 | 500 | 43b5ea | 428 | 132 / 364 | 11.9 | 0 | 5.9 | 0.968 | 15.7 | 0.0 | ok | ok | 23.5 |
| 204 | 6 | 500 | 3c381b | 451 | 140 / 384 | 8.7 | 0 | 7.8 | 0.975 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 205 | 6 | 500 | 55e936 | 423 | 136 / 396 | 11.4 | 0 | 0.0 | 0.971 | 5.9 | 0.0 | ok | ok | 43.1 |
| 206 | 6 | 500 | 808ec4 | 494 | 124 / 332 | 7.1 | 0 | 0.0 | 0.978 | 0.0 | 0.0 | ok | ok | 5.9 |
| 207 | 6 | 500 | 501b93 | 453 | 124 / 364 | 7.9 | 0 | 15.7 | 0.989 | 2.0 | 0.0 | ok | F: icehouse 84% of the time, outside 5-70% | 84.3 |
| 208 | 6 | 500 | c66b00 | 378 | 136 / 384 | 11.0 | 0 | 7.8 | 0.963 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 209 | 6 | 500 | 5206a3 | 391 | 132 / 432 | 6.7 | 0 | 0.0 | 0.966 | 0.0 | 0.0 | ok | ok | 9.8 |
| 210 | 6 | 500 | dde451 | 370 | 128 / 400 | 9.0 | 0 | 2.0 | 0.974 | 0.0 | 0.0 | ok | ok | 25.5 |
| 211 | 6 | 500 | c3036c | 405 | 108 / 444 | 9.8 | 0 | 0.0 | 0.968 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 212 | 6 | 500 | da4a79 | 419 | 136 / 384 | 6.9 | 0 | 2.0 | 0.98 | 0.0 | 0.0 | ok | ok | 68.6 |
| 213 | 6 | 500 | 6fb3d3 | 366 | 120 / 404 | 8.3 | 0 | 2.0 | 0.968 | 45.1 | 0.0 | ok | ok | 62.7 |
| 214 | 6 | 500 | 1e3107 | 372 | 136 / 416 | 11.7 | 0 | 9.8 | 0.963 | 51.0 | 0.0 | ok | F: icehouse 78% of the time, outside 5-70% | 78.4 |
| 215 | 6 | 500 | f10501 | 415 | 144 / 428 | 10.6 | 0 | 9.8 | 0.965 | 2.0 | 21.6 | ok | F: icehouse 100% of the time, outside 5-70% | 100.0 |
| 216 | 6 | 500 | 74dde9 | 394 | 128 / 392 | 10.7 | 0 | 11.8 | 0.982 | 17.6 | 0.0 | ok | ok | 66.7 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 201 | 6 | 33.2 | 39.4 | 34.6 | 10.0 | 53.7 | 4.2 | -102.4 | -54.1 | 127.5 | 2.4 | 12.6 | 0.1 | 26.1 | 5.3 | 0.5 | 0.2 | 6.0 | 31.7 | 226.5 | 7.0 | 16.7 |
| 202 | 6 | 34.1 | 40.2 | 33.7 | 9.0 | 65.0 | 3.8 | -75.8 | -16.8 | -57.4 | 1.4 | 18.3 | 0.3 | 19.0 | 4.5 | 0.6 | 0.1 | 6.4 | 35.4 | 324.6 | 12.0 | 31.0 |
| 203 | 6 | 33.6 | 40.2 | 33.7 | 11.0 | 55.1 | 4.1 | 74.0 | -9.0 | 84.7 | 0.6 | 16.1 | 0.2 | 20.1 | 4.2 | 0.4 | 0.1 | 4.9 | 36.5 | 301.0 | 8.0 | 18.8 |
| 204 | 6 | 33.8 | 39.9 | 33.9 | 15.0 | 51.7 | 4.7 | 122.6 | -2.0 | 127.2 | 0.2 | 17.4 | 0.2 | 25.5 | 4.7 | 0.3 | 0.1 | 4.1 | 32.5 | 319.6 | 10.0 | 16.6 |
| 205 | 6 | 33.2 | 40.1 | 34.2 | 16.0 | 49.1 | 4.7 | 116.8 | -18.1 | 138.7 | 1.0 | 15.2 | -0.0 | 24.5 | 3.5 | 0.5 | 0.1 | 6.0 | 23.8 | 328.0 | 8.0 | 14.6 |
| 206 | 6 | 34.5 | 40.5 | 33.7 | 7.0 | 63.5 | 4.0 | -39.6 | -5.6 | -26.2 | 0.5 | 16.0 | -0.3 | 32.9 | 4.2 | 0.3 | 0.1 | 4.8 | 26.3 | 223.1 | 8.0 | 25.9 |
| 207 | 6 | 32.8 | 39.1 | 35.1 | 9.0 | 56.7 | 3.8 | -16.0 | -40.3 | 31.3 | 2.8 | 14.6 | 0.0 | 16.0 | 4.0 | 1.0 | 0.3 | 6.5 | 37.6 | 270.2 | 7.0 | 20.0 |
| 208 | 6 | 33.6 | 40.7 | 33.6 | 13.0 | 46.7 | 4.3 | 192.4 | -1.3 | 193.9 | 0.1 | 20.1 | -0.1 | 26.0 | 4.5 | 0.4 | 0.1 | 4.2 | 26.6 | 264.1 | 10.0 | 18.3 |
| 209 | 6 | 32.7 | 41.5 | 32.7 | 11.0 | 57.3 | 4.3 | 23.4 | -1.3 | 25.3 | 0.1 | 18.4 | -0.2 | 25.2 | 2.3 | 0.3 | 0.1 | 5.6 | 26.6 | 275.9 | 9.0 | 16.8 |
| 210 | 6 | 33.7 | 39.9 | 34.1 | 14.0 | 51.4 | 4.9 | 153.4 | -6.4 | 162.7 | 0.4 | 17.6 | 0.1 | 29.2 | 4.8 | 0.4 | 0.2 | 5.1 | 26.7 | 309.6 | 7.0 | 19.2 |
| 211 | 6 | 33.1 | 40.0 | 34.1 | 14.0 | 46.3 | 4.6 | 163.7 | -3.2 | 167.1 | 0.3 | 19.3 | 0.1 | 27.6 | 5.7 | 0.4 | 0.1 | 5.2 | 24.9 | 242.6 | 9.0 | 17.9 |
| 212 | 6 | 32.3 | 40.1 | 34.3 | 15.0 | 47.7 | 4.6 | 128.1 | -25.2 | 163.6 | 1.6 | 15.4 | 0.4 | 23.8 | 5.2 | 0.5 | 0.1 | 4.7 | 37.1 | 340.7 | 7.0 | 23.9 |
| 213 | 6 | 32.6 | 40.4 | 33.5 | 12.0 | 53.3 | 3.9 | 57.9 | -40.5 | 105.2 | 2.2 | 15.8 | 0.2 | 18.3 | 2.3 | 0.3 | 0.1 | 5.0 | 41.1 | 323.8 | 9.0 | 19.1 |
| 214 | 6 | 31.0 | 41.0 | 33.5 | 11.0 | 48.9 | 4.5 | -21.5 | -158.1 | 133.5 | 6.1 | 13.7 | 0.4 | 16.8 | 2.5 | 0.4 | 0.1 | 5.2 | 49.4 | 375.4 | 4.0 | 25.3 |
| 215 | 6 | 32.9 | 39.2 | 34.7 | 10.0 | 69.0 | 4.2 | -109.2 | -54.1 | -51.7 | 2.8 | 11.5 | -0.2 | 27.0 | 5.0 | 0.5 | 0.1 | 7.5 | 26.4 | 175.8 | 7.0 | 18.2 |
| 216 | 6 | 32.7 | 39.3 | 35.0 | 11.0 | 48.4 | 4.8 | 58.4 | -24.3 | 126.9 | 2.2 | 16.0 | 0.7 | 22.4 | 4.2 | 0.6 | 0.1 | 6.7 | 41.6 | 313.6 | 7.0 | 20.7 |

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

## Top outliers (of 169 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 215 | 6 | low_plates | run | - | 21.60 | -..2 | 9.8 |
| 202 | 6 | giant_lake_frames | run | - | 31.40 | -..5 | 5.28 |
| 214 | 6 | sea_ice_below_150 | run | - | 51.00 | -..10 | 4.1 |
| 213 | 6 | sea_ice_below_150 | run | - | 45.10 | -..10 | 3.51 |
| 201 | 6 | sea_ice_below_150 | run | - | 37.30 | -..10 | 2.73 |
| 202 | 6 | lake_max_mkm2 | 308-324 | 5 | 11.57 | -..1.0 | 2.533 |
| 207 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 201 | 6 | giant_lake_frames | run | - | 11.80 | -..5 | 1.36 |
| 216 | 6 | giant_lake_frames | run | - | 11.80 | -..5 | 1.36 |
| 202 | 6 | lake_max_mkm2 | 340-360 | 4 | 6.29 | -..1.0 | 1.225 |
| 214 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 215 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 216 | 6 | sea_ice_below_150 | run | - | 17.60 | -..10 | 0.76 |
| 215 | 6 | lake_max_mkm2 | 300-304 | 2 | 4.33 | -..1.0 | 0.72 |
| 213 | 6 | lake_max_mkm2 | 344-344 | 1 | 4.42 | -..1.0 | 0.711 |
| 216 | 6 | lake_max_mkm2 | 340-356 | 5 | 3.54 | -..1.0 | 0.608 |
| 204 | 6 | lake_max_mkm2 | 356-364 | 2 | 3.71 | -..1.0 | 0.585 |
| 203 | 6 | sea_ice_below_150 | run | - | 15.70 | -..10 | 0.57 |
| 204 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 208 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 207 | 6 | lake_max_mkm2 | 344-356 | 3 | 3.30 | -..1.0 | 0.515 |
| 204 | 6 | lake_max_mkm2 | 300-304 | 2 | 3.15 | -..1.0 | 0.464 |
| 207 | 6 | lake_max_mkm2 | 424-424 | 1 | 2.93 | -..1.0 | 0.4 |
| 203 | 6 | lake_max_mkm2 | 396-396 | 1 | 2.86 | -..1.0 | 0.388 |
| 202 | 6 | lake_max_mkm2 | 460-460 | 1 | 2.64 | -..1.0 | 0.341 |
| 202 | 6 | lake_pct | 308-324 | 5 | 6.85 | 0.2..3.0 | 0.329 |
| 201 | 6 | lake_max_mkm2 | 484-488 | 2 | 2.52 | -..1.0 | 0.327 |
| 203 | 6 | lake_max_mkm2 | 408-412 | 2 | 2.49 | -..1.0 | 0.322 |
| 210 | 6 | lake_max_mkm2 | 396-396 | 1 | 2.53 | -..1.0 | 0.318 |
| 207 | 6 | lake_max_mkm2 | 396-396 | 1 | 2.30 | -..1.0 | 0.271 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 201, L6 (run b8371b)

![seed 201 L6](seed201_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.36 | 33.19 | 34.02 |  |
| cont_pct | 38.78 | 39.40 | 39.86 |  |
| cont_km | 34.10 | 34.62 | 35.36 |  |
| plates | 5.00 | 10.00 | 15.00 |  |
| ocean_age | 39.70 | 53.70 | 93.80 |  |
| speed | 2.58 | 4.23 | 5.01 |  |
| sea_level | -274.30 | -102.40 | 215.40 | 456-464: -266.30; 476-496: -274.30 |
| sea_ice_m | -264.00 | -54.10 | -3.90 | 404-432: -264.00 |
| sea_tect_m | -228.60 | 127.50 | 222.30 |  |
| ice_pct | 0.20 | 2.40 | 7.80 |  |
| temp | 9.30 | 12.60 | 18.70 |  |
| co2 | -1.62 | 0.15 | 0.97 |  |
| dry_pct | 19.54 | 26.15 | 32.30 |  |
| inland_pct | 2.35 | 5.28 | 12.18 | 336-500: 2.35 |
| lake_pct | 0.15 | 0.49 | 2.51 | 352-360: 0.15 |
| lake_max_mkm2 | 0.03 | 0.16 | 2.52 | 384-392: 1.49; 472-472: 1.27; 484-488: 2.52 |
| max_elev_km | 4.50 | 6.05 | 7.39 |  |
| trees_pct | 3.22 | 31.70 | 39.88 | 448-484: 3.22 |
| npp | 196.80 | 226.50 | 389.70 | 476-480: 196.80 |
| landmasses | 4.00 | 7.00 | 16.00 |  |
| largest_pct | 12.30 | 16.70 | 27.00 |  |

### Seed 202, L6 (run f31d9b)

![seed 202 L6](seed202_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.60 | 34.08 | 35.49 |  |
| cont_pct | 38.45 | 40.20 | 41.30 |  |
| cont_km | 32.75 | 33.70 | 34.79 |  |
| plates | 6.00 | 9.00 | 11.00 |  |
| ocean_age | 58.50 | 65.00 | 80.30 |  |
| speed | 2.78 | 3.83 | 5.54 |  |
| sea_level | -139.40 | -75.80 | -42.60 |  |
| sea_ice_m | -35.60 | -16.80 | -1.80 |  |
| sea_tect_m | -125.10 | -57.40 | -30.10 |  |
| ice_pct | 0.10 | 1.40 | 2.40 |  |
| temp | 14.90 | 18.30 | 22.00 |  |
| co2 | -0.42 | 0.26 | 1.01 |  |
| dry_pct | 16.74 | 19.02 | 30.51 |  |
| inland_pct | 1.07 | 4.52 | 17.90 | 300-312: 2.92; 328-344: 1.93; 356-476: 1.07; 488-488: 3.80; +1 more |
| lake_pct | 0.18 | 0.61 | 6.85 | 308-324: 6.85; 340-340: 4.54; 352-352: 3.04; 404-404: 0.18; +1 more |
| lake_max_mkm2 | 0.03 | 0.15 | 11.57 | 308-324: 11.57; 340-360: 6.29; 424-424: 1.23; 448-448: 1.68; +2 more |
| max_elev_km | 3.85 | 6.40 | 8.50 |  |
| trees_pct | 20.12 | 35.39 | 52.58 | 384-396: 52.58 |
| npp | 254.60 | 324.60 | 354.90 |  |
| landmasses | 7.00 | 12.00 | 16.00 |  |
| largest_pct | 12.60 | 31.00 | 35.10 | 304-304: 35.10 |

### Seed 203, L6 (run 43b5ea)

![seed 203 L6](seed203_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.11 | 33.58 | 34.53 |  |
| cont_pct | 38.68 | 40.24 | 40.76 |  |
| cont_km | 33.27 | 33.70 | 34.98 |  |
| plates | 9.00 | 11.00 | 15.00 |  |
| ocean_age | 41.90 | 55.10 | 69.20 |  |
| speed | 3.19 | 4.12 | 5.76 |  |
| sea_level | -292.40 | 74.00 | 178.00 | 468-488: -292.40 |
| sea_ice_m | -224.20 | -9.00 | -0.00 |  |
| sea_tect_m | -70.80 | 84.70 | 178.00 |  |
| ice_pct | 0.00 | 0.60 | 7.70 |  |
| temp | 10.50 | 16.10 | 22.40 |  |
| co2 | -0.80 | 0.19 | 1.32 |  |
| dry_pct | 16.45 | 20.15 | 31.03 |  |
| inland_pct | 0.89 | 4.24 | 9.03 | 300-336: 2.97; 348-460: 0.89; 480-500: 3.27 |
| lake_pct | 0.16 | 0.42 | 1.95 | 352-352: 0.18; 404-404: 0.16; 432-432: 0.18 |
| lake_max_mkm2 | 0.03 | 0.10 | 2.86 | 396-396: 2.86; 408-412: 2.49 |
| max_elev_km | 3.90 | 4.94 | 8.48 |  |
| trees_pct | 11.34 | 36.47 | 42.54 |  |
| npp | 174.40 | 301.00 | 411.30 | 372-384: 174.40 |
| landmasses | 3.00 | 8.00 | 11.00 |  |
| largest_pct | 10.70 | 18.80 | 29.50 |  |

### Seed 204, L6 (run 3c381b)

![seed 204 L6](seed204_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.17 | 33.78 | 34.16 |  |
| cont_pct | 37.85 | 39.92 | 40.64 |  |
| cont_km | 33.25 | 33.94 | 35.54 |  |
| plates | 11.00 | 15.00 | 18.00 |  |
| ocean_age | 46.00 | 51.70 | 60.00 |  |
| speed | 2.91 | 4.71 | 6.06 |  |
| sea_level | 67.10 | 122.60 | 153.70 |  |
| sea_ice_m | -17.50 | -2.00 | -0.00 |  |
| sea_tect_m | 75.30 | 127.20 | 153.70 |  |
| ice_pct | 0.00 | 0.20 | 1.70 |  |
| temp | 13.70 | 17.40 | 22.40 |  |
| co2 | -0.24 | 0.18 | 0.98 |  |
| dry_pct | 13.01 | 25.53 | 35.60 |  |
| inland_pct | 1.01 | 4.73 | 21.68 | 308-308: 6.64; 324-500: 1.01 |
| lake_pct | 0.10 | 0.35 | 2.53 | 384-400: 0.12; 412-432: 0.10; 448-452: 0.14 |
| lake_max_mkm2 | 0.01 | 0.06 | 3.71 | 300-304: 3.15; 356-364: 3.71 |
| max_elev_km | 2.86 | 4.11 | 7.04 |  |
| trees_pct | 23.51 | 32.50 | 40.22 |  |
| npp | 171.50 | 319.60 | 395.90 | 384-396: 171.50 |
| landmasses | 3.00 | 10.00 | 14.00 |  |
| largest_pct | 13.60 | 16.60 | 33.10 |  |

### Seed 205, L6 (run 55e936)

![seed 205 L6](seed205_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.40 | 33.18 | 34.05 |  |
| cont_pct | 38.92 | 40.08 | 40.70 |  |
| cont_km | 33.74 | 34.17 | 35.45 |  |
| plates | 9.00 | 16.00 | 19.00 |  |
| ocean_age | 42.10 | 49.10 | 66.80 |  |
| speed | 2.98 | 4.73 | 5.50 |  |
| sea_level | -198.70 | 116.80 | 182.20 |  |
| sea_ice_m | -200.60 | -18.10 | -0.00 |  |
| sea_tect_m | -4.80 | 138.70 | 187.10 |  |
| ice_pct | 0.00 | 1.00 | 6.50 |  |
| temp | 8.50 | 15.20 | 19.90 |  |
| co2 | -0.75 | -0.00 | 0.72 |  |
| dry_pct | 17.67 | 24.46 | 36.93 |  |
| inland_pct | 1.05 | 3.49 | 9.57 | 300-500: 1.05 |
| lake_pct | 0.17 | 0.49 | 1.05 | 360-372: 0.17 |
| lake_max_mkm2 | 0.04 | 0.12 | 0.86 |  |
| max_elev_km | 3.74 | 6.02 | 7.31 |  |
| trees_pct | 12.79 | 23.76 | 33.29 |  |
| npp | 161.20 | 328.00 | 406.50 | 400-412: 161.20 |
| landmasses | 3.00 | 8.00 | 14.00 |  |
| largest_pct | 9.90 | 14.60 | 31.30 |  |

### Seed 206, L6 (run 808ec4)

![seed 206 L6](seed206_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.05 | 34.47 | 35.06 |  |
| cont_pct | 38.37 | 40.51 | 42.76 |  |
| cont_km | 32.28 | 33.73 | 35.08 |  |
| plates | 6.00 | 7.00 | 10.00 |  |
| ocean_age | 52.70 | 63.50 | 75.60 |  |
| speed | 3.17 | 3.97 | 5.37 |  |
| sea_level | -181.20 | -39.60 | 65.10 |  |
| sea_ice_m | -31.30 | -5.60 | -1.20 |  |
| sea_tect_m | -168.50 | -26.20 | 68.90 |  |
| ice_pct | 0.10 | 0.50 | 1.30 |  |
| temp | 13.50 | 16.00 | 20.60 |  |
| co2 | -1.95 | -0.28 | 0.89 |  |
| dry_pct | 15.37 | 32.91 | 38.22 |  |
| inland_pct | 0.21 | 4.19 | 14.19 | 300-348: 3.74; 360-376: 4.24; 388-500: 0.21 |
| lake_pct | 0.13 | 0.31 | 0.56 | 412-412: 0.13 |
| lake_max_mkm2 | 0.01 | 0.05 | 0.21 |  |
| max_elev_km | 3.98 | 4.83 | 8.54 |  |
| trees_pct | 2.63 | 26.31 | 42.98 | 416-500: 2.63 |
| npp | 99.70 | 223.10 | 312.50 | 352-356: 181.40; 384-384: 188.30; 400-444: 99.70 |
| landmasses | 2.00 | 8.00 | 12.00 | 300-300: 2 |
| largest_pct | 24.80 | 25.90 | 33.50 |  |

### Seed 207, L6 (run 501b93)

![seed 207 L6](seed207_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.68 | 32.77 | 33.68 |  |
| cont_pct | 37.84 | 39.09 | 40.84 |  |
| cont_km | 34.04 | 35.11 | 35.64 |  |
| plates | 7.00 | 9.00 | 11.00 |  |
| ocean_age | 49.20 | 56.70 | 59.40 |  |
| speed | 3.16 | 3.80 | 5.05 |  |
| sea_level | -122.10 | -16.00 | 38.80 |  |
| sea_ice_m | -154.90 | -40.30 | -12.40 |  |
| sea_tect_m | -60.00 | 31.30 | 82.10 |  |
| ice_pct | 1.20 | 2.80 | 7.10 |  |
| temp | 11.80 | 14.60 | 19.70 |  |
| co2 | -0.82 | 0.03 | 1.09 |  |
| dry_pct | 9.98 | 16.03 | 22.62 | 460-496: 9.98 |
| inland_pct | 0.99 | 4.02 | 9.76 | 300-500: 0.99 |
| lake_pct | 0.42 | 0.96 | 4.55 | 344-344: 4.55 |
| lake_max_mkm2 | 0.03 | 0.34 | 3.30 | 344-356: 3.30; 396-396: 2.30; 424-424: 2.93; 476-484: 2.04 |
| max_elev_km | 5.58 | 6.55 | 7.80 |  |
| trees_pct | 13.24 | 37.64 | 50.86 | 364-364: 50.86 |
| npp | 109.50 | 270.20 | 376.70 | 424-432: 109.50 |
| landmasses | 3.00 | 7.00 | 12.00 |  |
| largest_pct | 15.90 | 20.00 | 30.10 |  |

### Seed 208, L6 (run c66b00)

![seed 208 L6](seed208_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.04 | 33.63 | 34.49 |  |
| cont_pct | 39.21 | 40.71 | 41.28 |  |
| cont_km | 33.17 | 33.58 | 34.92 |  |
| plates | 12.00 | 13.00 | 16.00 |  |
| ocean_age | 39.10 | 46.70 | 73.60 |  |
| speed | 3.52 | 4.35 | 5.63 |  |
| sea_level | -70.30 | 192.40 | 218.90 |  |
| sea_ice_m | -6.80 | -1.30 | -0.00 |  |
| sea_tect_m | -67.10 | 193.90 | 219.80 |  |
| ice_pct | 0.00 | 0.10 | 0.60 |  |
| temp | 12.00 | 20.10 | 23.00 |  |
| co2 | -1.07 | -0.07 | 0.91 |  |
| dry_pct | 24.52 | 26.03 | 36.43 |  |
| inland_pct | 1.99 | 4.50 | 14.25 | 312-372: 2.56; 384-500: 1.99 |
| lake_pct | 0.21 | 0.39 | 1.31 |  |
| lake_max_mkm2 | 0.03 | 0.06 | 1.64 | 300-300: 1.64; 376-388: 1.56 |
| max_elev_km | 3.53 | 4.23 | 8.22 |  |
| trees_pct | 0.87 | 26.63 | 42.34 | 412-440: 0.87 |
| npp | 81.50 | 264.10 | 345.90 | 396-420: 81.50 |
| landmasses | 5.00 | 10.00 | 14.00 |  |
| largest_pct | 13.20 | 18.30 | 32.70 |  |

### Seed 209, L6 (run 5206a3)

![seed 209 L6](seed209_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.21 | 32.68 | 33.61 |  |
| cont_pct | 37.81 | 41.50 | 41.99 |  |
| cont_km | 32.29 | 32.72 | 35.52 |  |
| plates | 7.00 | 11.00 | 15.00 |  |
| ocean_age | 40.50 | 57.30 | 74.50 |  |
| speed | 3.22 | 4.35 | 5.72 |  |
| sea_level | -214.00 | 23.40 | 153.10 |  |
| sea_ice_m | -105.90 | -1.30 | -0.00 |  |
| sea_tect_m | -114.40 | 25.30 | 153.20 |  |
| ice_pct | 0.00 | 0.10 | 5.10 |  |
| temp | 13.60 | 18.40 | 20.30 |  |
| co2 | -1.86 | -0.17 | 1.04 |  |
| dry_pct | 19.00 | 25.16 | 32.75 |  |
| inland_pct | 0.82 | 2.30 | 10.82 | 300-500: 0.82 |
| lake_pct | 0.12 | 0.29 | 1.16 | 324-324: 0.12; 360-360: 0.18; 492-500: 0.12 |
| lake_max_mkm2 | 0.01 | 0.06 | 0.93 |  |
| max_elev_km | 4.32 | 5.60 | 8.29 |  |
| trees_pct | 0.60 | 26.63 | 41.73 | 420-500: 0.60 |
| npp | 97.80 | 275.95 | 299.40 | 432-432: 97.80 |
| landmasses | 4.00 | 9.00 | 17.00 |  |
| largest_pct | 10.70 | 16.80 | 25.30 |  |

### Seed 210, L6 (run dde451)

![seed 210 L6](seed210_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.65 | 33.73 | 34.38 |  |
| cont_pct | 38.58 | 39.86 | 40.55 |  |
| cont_km | 33.86 | 34.14 | 35.36 |  |
| plates | 11.00 | 14.00 | 18.00 |  |
| ocean_age | 38.10 | 51.40 | 60.60 |  |
| speed | 3.69 | 4.89 | 5.53 |  |
| sea_level | -116.60 | 153.40 | 242.40 |  |
| sea_ice_m | -132.80 | -6.40 | -0.00 |  |
| sea_tect_m | 3.90 | 162.70 | 242.40 |  |
| ice_pct | 0.00 | 0.40 | 4.30 |  |
| temp | 12.40 | 17.60 | 21.40 |  |
| co2 | -0.48 | 0.13 | 1.19 |  |
| dry_pct | 21.37 | 29.17 | 39.45 |  |
| inland_pct | 2.25 | 4.79 | 13.16 | 304-424: 2.25; 436-500: 3.26 |
| lake_pct | 0.10 | 0.42 | 1.88 | 308-308: 0.19; 340-340: 0.20; 352-380: 0.10 |
| lake_max_mkm2 | 0.01 | 0.20 | 2.53 | 396-396: 2.53 |
| max_elev_km | 3.46 | 5.08 | 7.57 |  |
| trees_pct | 18.62 | 26.67 | 41.78 |  |
| npp | 140.30 | 309.55 | 401.90 | 412-432: 140.30 |
| landmasses | 3.00 | 7.00 | 12.00 |  |
| largest_pct | 11.90 | 19.20 | 34.40 |  |

### Seed 211, L6 (run c3036c)

![seed 211 L6](seed211_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.57 | 33.14 | 33.79 |  |
| cont_pct | 38.84 | 40.02 | 40.93 |  |
| cont_km | 33.43 | 34.10 | 35.22 |  |
| plates | 9.00 | 14.00 | 19.00 |  |
| ocean_age | 39.30 | 46.30 | 60.80 |  |
| speed | 3.32 | 4.61 | 5.11 |  |
| sea_level | -4.90 | 163.70 | 222.40 |  |
| sea_ice_m | -13.60 | -3.20 | -0.00 |  |
| sea_tect_m | -1.50 | 167.10 | 224.00 |  |
| ice_pct | 0.00 | 0.30 | 0.70 |  |
| temp | 13.70 | 19.30 | 23.50 |  |
| co2 | -1.28 | 0.11 | 1.07 |  |
| dry_pct | 21.00 | 27.60 | 37.06 |  |
| inland_pct | 1.07 | 5.69 | 17.98 | 300-420: 1.07; 452-452: 7.77; 496-496: 7.97 |
| lake_pct | 0.16 | 0.38 | 0.94 | 416-416: 0.19; 440-452: 0.16; 496-496: 0.19 |
| lake_max_mkm2 | 0.01 | 0.11 | 0.71 |  |
| max_elev_km | 3.44 | 5.25 | 8.31 |  |
| trees_pct | 0.75 | 24.95 | 38.06 | 448-500: 0.75 |
| npp | 211.40 | 242.60 | 298.10 |  |
| landmasses | 3.00 | 9.00 | 18.00 |  |
| largest_pct | 11.00 | 17.90 | 29.30 |  |

### Seed 212, L6 (run da4a79)

![seed 212 L6](seed212_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.62 | 32.32 | 34.13 |  |
| cont_pct | 38.48 | 40.13 | 41.12 |  |
| cont_km | 33.40 | 34.33 | 35.73 |  |
| plates | 10.00 | 15.00 | 17.00 |  |
| ocean_age | 40.10 | 47.70 | 55.60 |  |
| speed | 3.34 | 4.58 | 5.29 |  |
| sea_level | 53.50 | 128.10 | 224.20 |  |
| sea_ice_m | -43.00 | -25.20 | -0.00 |  |
| sea_tect_m | 82.70 | 163.60 | 224.20 |  |
| ice_pct | 0.00 | 1.60 | 2.70 |  |
| temp | 12.20 | 15.40 | 19.10 |  |
| co2 | -1.02 | 0.40 | 1.09 |  |
| dry_pct | 10.42 | 23.83 | 33.19 | 348-356: 10.42 |
| inland_pct | 1.69 | 5.18 | 10.92 | 304-304: 6.38; 316-380: 1.69; 392-500: 2.23 |
| lake_pct | 0.12 | 0.50 | 1.03 | 404-404: 0.12; 416-416: 0.12 |
| lake_max_mkm2 | 0.03 | 0.12 | 1.11 | 356-356: 1.11 |
| max_elev_km | 3.93 | 4.67 | 5.91 |  |
| trees_pct | 4.77 | 37.15 | 53.19 | 368-400: 53.19; 496-496: 4.77 |
| npp | 222.30 | 340.70 | 416.20 |  |
| landmasses | 1.00 | 7.00 | 15.00 | 304-336: 1 |
| largest_pct | 12.10 | 23.90 | 34.10 |  |

### Seed 213, L6 (run 6fb3d3)

![seed 213 L6](seed213_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.66 | 32.57 | 33.82 |  |
| cont_pct | 39.35 | 40.35 | 41.28 |  |
| cont_km | 32.84 | 33.45 | 34.25 |  |
| plates | 9.00 | 12.00 | 14.00 |  |
| ocean_age | 37.70 | 53.30 | 60.50 |  |
| speed | 2.22 | 3.89 | 5.58 |  |
| sea_level | -187.20 | 57.90 | 202.30 |  |
| sea_ice_m | -255.20 | -40.50 | -6.10 | 420-424: -255.20 |
| sea_tect_m | 4.70 | 105.20 | 213.60 |  |
| ice_pct | 0.40 | 2.20 | 7.00 |  |
| temp | 10.30 | 15.80 | 18.60 |  |
| co2 | -0.77 | 0.20 | 1.20 |  |
| dry_pct | 12.82 | 18.32 | 23.85 |  |
| inland_pct | 0.76 | 2.32 | 7.82 | 300-500: 0.76 |
| lake_pct | 0.15 | 0.34 | 3.48 | 344-344: 3.48; 472-476: 0.15; 496-496: 0.16 |
| lake_max_mkm2 | 0.01 | 0.07 | 4.42 | 344-344: 4.42 |
| max_elev_km | 3.13 | 5.03 | 7.25 |  |
| trees_pct | 9.39 | 41.07 | 48.46 | 500-500: 9.39 |
| npp | 259.40 | 323.80 | 373.10 |  |
| landmasses | 2.00 | 9.00 | 14.00 | 300-300: 2 |
| largest_pct | 11.60 | 19.10 | 32.40 |  |

### Seed 214, L6 (run 1e3107)

![seed 214 L6](seed214_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 28.38 | 31.00 | 32.57 |  |
| cont_pct | 39.29 | 41.03 | 41.99 |  |
| cont_km | 32.72 | 33.54 | 34.72 |  |
| plates | 10.00 | 11.00 | 14.00 |  |
| ocean_age | 43.00 | 48.90 | 53.90 |  |
| speed | 2.58 | 4.47 | 5.12 |  |
| sea_level | -208.30 | -21.50 | 141.40 |  |
| sea_ice_m | -319.70 | -158.10 | -10.50 | 348-404: -319.70; 416-416: -250.80 |
| sea_tect_m | 74.80 | 133.50 | 167.40 |  |
| ice_pct | 0.90 | 6.10 | 10.50 | 352-368: 10.50 |
| temp | 6.10 | 13.70 | 17.80 | 348-372: 6.10 |
| co2 | -0.94 | 0.40 | 0.96 |  |
| dry_pct | 14.99 | 16.84 | 24.54 |  |
| inland_pct | 0.77 | 2.51 | 8.07 | 300-500: 0.77 |
| lake_pct | 0.17 | 0.38 | 1.50 | 376-376: 0.19; 396-400: 0.17 |
| lake_max_mkm2 | 0.03 | 0.12 | 2.08 | 300-300: 1.21; 312-324: 2.08; 436-436: 1.03 |
| max_elev_km | 4.57 | 5.18 | 7.77 |  |
| trees_pct | 3.82 | 49.44 | 60.31 | 352-384: 51.93; 400-452: 60.31; 484-484: 9.65; 496-500: 3.82 |
| npp | 268.40 | 375.40 | 449.20 |  |
| landmasses | 2.00 | 4.00 | 13.00 | 324-328: 2; 348-356: 2; 392-392: 2 |
| largest_pct | 11.40 | 25.30 | 33.00 |  |

### Seed 215, L6 (run f10501)

![seed 215 L6](seed215_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.65 | 32.88 | 34.58 |  |
| cont_pct | 38.22 | 39.16 | 40.81 |  |
| cont_km | 33.66 | 34.67 | 35.37 |  |
| plates | 3.00 | 10.00 | 14.00 | 452-492: 3 |
| ocean_age | 49.30 | 69.00 | 101.80 |  |
| speed | 2.07 | 4.16 | 6.03 |  |
| sea_level | -449.90 | -109.20 | 67.70 | 468-500: -449.90 |
| sea_ice_m | -159.00 | -54.10 | -30.10 |  |
| sea_tect_m | -300.70 | -51.70 | 106.50 | 488-500: -300.70 |
| ice_pct | 1.60 | 2.80 | 6.80 |  |
| temp | 5.10 | 11.50 | 15.70 | 436-436: 7.60; 460-500: 5.10 |
| co2 | -3.14 | -0.24 | 0.58 |  |
| dry_pct | 20.46 | 27.02 | 31.23 |  |
| inland_pct | 2.14 | 5.02 | 17.84 | 312-424: 3.23; 444-500: 2.14 |
| lake_pct | 0.26 | 0.48 | 3.96 | 300-304: 3.96 |
| lake_max_mkm2 | 0.04 | 0.11 | 4.33 | 300-304: 4.33; 340-340: 1.08; 432-432: 2.10; 500-500: 1.25 |
| max_elev_km | 4.28 | 7.53 | 8.61 |  |
| trees_pct | 3.79 | 26.41 | 43.01 | 448-496: 3.79 |
| npp | 157.00 | 175.80 | 244.80 | 436-496: 157.00 |
| landmasses | 1.00 | 7.00 | 13.00 | 468-500: 1 |
| largest_pct | 16.80 | 18.20 | 34.60 |  |

### Seed 216, L6 (run 74dde9)

![seed 216 L6](seed216_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.69 | 32.69 | 33.93 |  |
| cont_pct | 36.96 | 39.26 | 40.88 |  |
| cont_km | 33.72 | 34.99 | 36.61 |  |
| plates | 8.00 | 11.00 | 14.00 |  |
| ocean_age | 41.60 | 48.40 | 82.50 |  |
| speed | 2.94 | 4.78 | 6.12 |  |
| sea_level | -272.30 | 58.40 | 173.10 | 300-304: -272.30 |
| sea_ice_m | -288.80 | -24.30 | -9.60 | 472-500: -288.80 |
| sea_tect_m | -248.20 | 126.90 | 198.10 |  |
| ice_pct | 0.80 | 2.20 | 10.30 | 480-492: 10.30 |
| temp | 10.10 | 16.00 | 20.80 |  |
| co2 | -0.30 | 0.67 | 1.19 |  |
| dry_pct | 12.59 | 22.40 | 36.56 |  |
| inland_pct | 1.19 | 4.21 | 19.84 | 300-308: 7.43; 320-332: 3.82; 348-348: 5.60; 360-500: 1.19 |
| lake_pct | 0.19 | 0.56 | 2.62 | 408-408: 0.19 |
| lake_max_mkm2 | 0.01 | 0.09 | 3.54 | 312-312: 1.01; 340-356: 3.54 |
| max_elev_km | 4.35 | 6.69 | 8.46 |  |
| trees_pct | 31.31 | 41.62 | 53.37 | 388-440: 53.37 |
| npp | 271.60 | 313.55 | 437.00 |  |
| landmasses | 3.00 | 7.00 | 14.00 |  |
| largest_pct | 8.00 | 20.70 | 33.70 |  |

## Determinism

(not run)
