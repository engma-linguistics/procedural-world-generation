# Health sweep 2026-10-23 15:22

Commit None. 16 runs (default params, `--every 4`) at 8 workers x 3 numba threads; simulations 13.5 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | 5e0e86 | 332 | 104 / 316 | 9.1 | 0 | 25.5 | 0.973 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 2 | 6 | 500 | 45146b | 368 | 116 / 268 | 11.1 | 0 | 0.0 | 0.965 | 0.0 | 0.0 | ok | ok | 51.0 |
| 11 | 6 | 500 | 442712 | 393 | 116 / 272 | 10.4 | 0 | 2.0 | 0.98 | 27.5 | 0.0 | ok | ok | 54.9 |
| 21 | 6 | 500 | 2de88e | 327 | 116 / 336 | 11.4 | 0 | 9.8 | 0.949 | 0.0 | 0.0 | ok | F: icehouse 2% of the time, outside 5-70% | 2.0 |
| 3199 | 6 | 500 | a8d15c | 349 | 112 / 344 | 8.9 | 0 | 2.0 | 0.96 | 0.0 | 0.0 | ok | F: icehouse 76% of the time, outside 5-70% | 76.5 |
| 42 | 6 | 500 | 2d28cf | 358 | 116 / 288 | 10.0 | 0 | 3.9 | 0.975 | 23.5 | 0.0 | ok | F: icehouse 71% of the time, outside 5-70% | 70.6 |
| 77 | 6 | 500 | f4a0ac | 397 | 112 / 272 | 13.7 | 0 | 2.0 | 0.966 | 88.2 | 2.0 | ok | F: deep era 300-476 Myr lasts 180 > 150; icehouse 100% of the time, outside 5-70% | 100.0 |
| 505 | 6 | 500 | f6a0a8 | 374 | 108 / 328 | 7.2 | 0 | 5.9 | 0.969 | 0.0 | 0.0 | ok | ok | 13.7 |
| 101 | 6 | 500 | fd219b | 434 | 116 / 352 | 10.1 | 0 | 3.9 | 0.977 | 0.0 | 0.0 | ok | ok | 37.3 |
| 102 | 6 | 500 | 18835e | 377 | 116 / 344 | 8.1 | 0 | 2.0 | 0.978 | 9.8 | 0.0 | ok | ok | 41.2 |
| 103 | 6 | 500 | 8e9e6c | 362 | 116 / 336 | 12.5 | 0 | 15.7 | 0.969 | 35.3 | 0.0 | F | ok | 62.7 |
| 104 | 6 | 500 | 17eba9 | 370 | 116 / 312 | 6.2 | 0 | 5.9 | 0.968 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 105 | 6 | 500 | ebb60c | 432 | 108 / 312 | 13.5 | 0 | 15.7 | 0.956 | 3.9 | 0.0 | ok | ok | 43.1 |
| 106 | 6 | 500 | 04a616 | 365 | 116 / 312 | 7.9 | 0 | 0.0 | 0.977 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 107 | 6 | 500 | 22cf35 | 406 | 100 / 300 | 10.4 | 0 | 7.8 | 0.951 | 3.9 | 9.8 | ok | F: icehouse 84% of the time, outside 5-70% | 84.3 |
| 108 | 6 | 500 | 6839c3 | 415 | 104 / 320 | 7.0 | 0 | 0.0 | 0.96 | 0.0 | 0.0 | ok | F: icehouse 78% of the time, outside 5-70% | 78.4 |

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

## Top outliers (of 196 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 77 | 6 | sea_ice_below_150 | run | - | 88.20 | -..10 | 7.82 |
| 1 | 6 | giant_lake_frames | run | - | 25.50 | -..5 | 4.1 |
| 107 | 6 | low_plates | run | - | 9.80 | -..2 | 3.9 |
| 1 | 6 | lake_max_mkm2 | 340-352 | 4 | 12.29 | -..1.0 | 2.616 |
| 103 | 6 | sea_ice_below_150 | run | - | 35.30 | -..10 | 2.53 |
| 1 | 6 | lake_max_mkm2 | 424-440 | 5 | 10.16 | -..1.0 | 2.196 |
| 103 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 105 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 11 | 6 | sea_ice_below_150 | run | - | 27.50 | -..10 | 1.75 |
| 1 | 6 | lake_max_mkm2 | 404-412 | 2 | 9.04 | -..1.0 | 1.736 |
| 1 | 6 | lake_max_mkm2 | 452-452 | 1 | 9.24 | -..1.0 | 1.713 |
| 42 | 6 | sea_ice_below_150 | run | - | 23.50 | -..10 | 1.35 |
| 21 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 101 | 6 | lake_max_mkm2 | 452-452 | 1 | 4.33 | -..1.0 | 0.693 |
| 21 | 6 | lake_max_mkm2 | 484-484 | 1 | 3.76 | -..1.0 | 0.574 |
| 107 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 107 | 6 | lake_max_mkm2 | 352-360 | 3 | 3.27 | -..1.0 | 0.509 |
| 77 | 6 | sea_level | 316-500 | 47 | -718.70 | -250..300 | 0.488 |
| 101 | 6 | lake_max_mkm2 | 468-468 | 1 | 3.30 | -..1.0 | 0.478 |
| 1 | 6 | lake_max_mkm2 | 388-388 | 1 | 2.96 | -..1.0 | 0.408 |
| 1 | 6 | lake_pct | 340-352 | 4 | 7.45 | 0.2..3.0 | 0.368 |
| 21 | 6 | lake_max_mkm2 | 300-308 | 3 | 2.44 | -..1.0 | 0.323 |
| 77 | 6 | sea_ice_m | 304-472 | 43 | -389.50 | -250..- | 0.302 |
| 105 | 6 | lake_max_mkm2 | 460-472 | 4 | 2.23 | -..1.0 | 0.285 |
| 103 | 6 | sea_ice_m | 300-344 | 12 | -478.80 | -250..- | 0.27 |
| 21 | 6 | lake_max_mkm2 | 468-468 | 1 | 2.19 | -..1.0 | 0.248 |
| 1 | 6 | lake_pct | 424-432 | 3 | 6.00 | 0.2..3.0 | 0.24 |
| 1 | 6 | lake_pct | 452-452 | 1 | 6.13 | 0.2..3.0 | 0.232 |
| 105 | 6 | lake_max_mkm2 | 412-412 | 1 | 2.06 | -..1.0 | 0.219 |
| 1 | 6 | lake_pct | 412-412 | 1 | 5.81 | 0.2..3.0 | 0.209 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run 5e0e86)

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

### Seed 2, L6 (run 45146b)

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

### Seed 11, L6 (run 442712)

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

### Seed 21, L6 (run 2de88e)

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

### Seed 3199, L6 (run a8d15c)

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

### Seed 42, L6 (run 2d28cf)

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

### Seed 77, L6 (run f4a0ac)

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

### Seed 505, L6 (run f6a0a8)

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

### Seed 101, L6 (run fd219b)

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

### Seed 102, L6 (run 18835e)

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

### Seed 103, L6 (run 8e9e6c)

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

### Seed 104, L6 (run 17eba9)

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

### Seed 105, L6 (run ebb60c)

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

### Seed 106, L6 (run 04a616)

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

### Seed 107, L6 (run 22cf35)

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

### Seed 108, L6 (run 6839c3)

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

(not run)
