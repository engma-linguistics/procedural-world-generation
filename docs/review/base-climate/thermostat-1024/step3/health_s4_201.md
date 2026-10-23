# Health sweep 2026-10-23 16:18

Commit None. 16 runs (default params, `--every 4`) at 6 workers x 3 numba threads; simulations 21.9 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 201 | 6 | 500 | 0649d3 | 416 | 140 / 412 | 8.3 | 0 | 13.7 | 0.981 | 0.0 | 0.0 | ok | ok | 66.7 |
| 202 | 6 | 500 | 0c87fe | 386 | 132 / 368 | 5.7 | 0 | 0.0 | 0.967 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 203 | 6 | 500 | 95fa44 | 386 | 132 / 364 | 11.4 | 0 | 21.6 | 0.966 | 49.0 | 15.7 | F | ok | 68.6 |
| 204 | 6 | 500 | 5389fb | 471 | 140 / 384 | 7.8 | 0 | 7.8 | 0.963 | 0.0 | 0.0 | ok | ok | 58.8 |
| 205 | 6 | 500 | 4e9665 | 396 | 136 / 396 | 13.4 | 0 | 3.9 | 0.971 | 0.0 | 0.0 | ok | ok | 37.3 |
| 206 | 6 | 500 | 246968 | 414 | 124 / 332 | 10.2 | 0 | 2.0 | 0.981 | 0.0 | 0.0 | ok | ok | 9.8 |
| 207 | 6 | 500 | ccafc7 | 490 | 124 / 364 | 9.4 | 0 | 5.9 | 0.981 | 25.5 | 0.0 | ok | F: icehouse 75% of the time, outside 5-70% | 74.5 |
| 208 | 6 | 500 | 615d75 | 413 | 136 / 384 | 13.4 | 0 | 2.0 | 0.967 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 209 | 6 | 500 | 548bba | 414 | 132 / 432 | 6.2 | 0 | 5.9 | 0.966 | 0.0 | 0.0 | ok | ok | 5.9 |
| 210 | 6 | 500 | 82ed18 | 483 | 128 / 400 | 7.8 | 0 | 19.6 | 0.95 | 0.0 | 0.0 | ok | ok | 45.1 |
| 211 | 6 | 500 | 04185f | 539 | 108 / 444 | 12.4 | 0 | 5.9 | 0.974 | 7.8 | 0.0 | ok | F: icehouse 76% of the time, outside 5-70% | 76.5 |
| 212 | 6 | 500 | 7531a7 | 494 | 136 / 384 | 10.2 | 0 | 0.0 | 0.975 | 35.3 | 0.0 | ok | F: icehouse 84% of the time, outside 5-70% | 84.3 |
| 213 | 6 | 500 | 550c21 | 413 | 120 / 404 | 8.2 | 0 | 2.0 | 0.967 | 0.0 | 0.0 | ok | ok | 37.3 |
| 214 | 6 | 500 | 43e321 | 406 | 136 / 416 | 12.4 | 0 | 7.8 | 0.956 | 7.8 | 0.0 | ok | ok | 43.1 |
| 215 | 6 | 500 | 2438b9 | 392 | 144 / 428 | 9.0 | 0 | 5.9 | 0.977 | 0.0 | 0.0 | ok | ok | 5.9 |
| 216 | 6 | 500 | a8474f | 414 | 128 / 392 | 10.5 | 0 | 5.9 | 0.975 | 31.4 | 0.0 | ok | F: icehouse 98% of the time, outside 5-70% | 98.0 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 201 | 6 | 33.0 | 40.2 | 34.4 | 13.0 | 57.7 | 4.4 | 47.0 | -24.3 | 72.5 | 1.9 | 17.2 | 0.7 | 26.5 | 5.8 | 0.6 | 0.1 | 5.0 | 34.0 | 346.2 | 10.0 | 30.2 |
| 202 | 6 | 33.6 | 40.6 | 33.8 | 13.0 | 50.8 | 4.8 | 89.0 | -7.0 | 97.7 | 0.5 | 17.6 | 0.3 | 18.9 | 3.6 | 0.4 | 0.1 | 4.6 | 29.3 | 316.9 | 13.0 | 14.0 |
| 203 | 6 | 33.4 | 41.5 | 32.5 | 7.0 | 84.1 | 5.2 | -387.4 | -140.4 | -238.6 | 4.4 | 13.2 | 0.0 | 27.8 | 5.1 | 0.6 | 0.2 | 5.6 | 25.7 | 365.3 | 6.0 | 25.1 |
| 204 | 6 | 33.4 | 40.4 | 33.9 | 9.0 | 64.0 | 3.9 | -46.7 | -23.0 | -20.0 | 1.9 | 16.9 | 0.2 | 17.3 | 3.1 | 0.6 | 0.1 | 6.9 | 36.2 | 352.9 | 9.0 | 22.2 |
| 205 | 6 | 32.9 | 40.8 | 33.4 | 14.0 | 62.1 | 4.2 | 63.0 | -17.7 | 78.0 | 1.5 | 17.6 | 0.7 | 22.9 | 2.9 | 0.4 | 0.1 | 5.8 | 37.7 | 373.2 | 11.0 | 11.3 |
| 206 | 6 | 33.8 | 40.0 | 34.0 | 15.0 | 51.0 | 4.5 | 104.3 | -7.7 | 115.8 | 0.7 | 18.5 | 0.1 | 31.8 | 5.8 | 0.3 | 0.1 | 4.4 | 23.8 | 234.7 | 7.0 | 18.4 |
| 207 | 6 | 32.2 | 38.0 | 35.6 | 11.0 | 63.6 | 4.2 | -126.7 | -69.0 | -35.6 | 3.5 | 14.3 | -0.0 | 25.2 | 7.1 | 0.6 | 0.1 | 7.0 | 35.8 | 252.3 | 7.0 | 16.5 |
| 208 | 6 | 32.9 | 40.1 | 33.5 | 15.0 | 53.9 | 4.4 | 108.2 | -4.9 | 114.8 | 0.5 | 18.6 | -0.1 | 22.9 | 2.7 | 0.3 | 0.1 | 6.8 | 24.6 | 304.6 | 9.0 | 17.0 |
| 209 | 6 | 33.3 | 40.1 | 33.6 | 11.0 | 57.6 | 4.4 | 29.8 | -6.9 | 38.5 | 0.5 | 18.6 | -0.0 | 24.6 | 3.7 | 0.5 | 0.1 | 6.3 | 28.6 | 255.8 | 9.0 | 19.7 |
| 210 | 6 | 33.0 | 41.9 | 32.0 | 9.0 | 63.5 | 4.0 | -54.9 | -17.1 | -21.9 | 1.3 | 16.8 | 0.1 | 18.1 | 2.2 | 0.6 | 0.2 | 6.2 | 39.6 | 334.2 | 6.0 | 23.4 |
| 211 | 6 | 33.2 | 41.4 | 33.0 | 10.0 | 61.1 | 4.1 | -84.7 | -55.4 | 12.7 | 2.6 | 15.9 | -0.1 | 24.2 | 3.8 | 0.4 | 0.1 | 5.6 | 21.8 | 212.3 | 8.0 | 23.1 |
| 212 | 6 | 32.6 | 39.4 | 34.7 | 13.0 | 49.1 | 4.3 | 133.6 | -68.2 | 163.5 | 3.9 | 14.8 | 0.5 | 18.6 | 4.4 | 0.4 | 0.1 | 5.6 | 33.5 | 304.2 | 9.0 | 17.1 |
| 213 | 6 | 33.4 | 41.5 | 32.8 | 12.0 | 49.3 | 4.9 | 93.2 | -12.3 | 115.1 | 1.0 | 14.7 | 0.1 | 25.0 | 2.4 | 0.3 | 0.1 | 5.4 | 33.4 | 317.4 | 9.0 | 31.3 |
| 214 | 6 | 32.6 | 41.1 | 32.6 | 10.0 | 59.3 | 4.1 | -7.1 | -15.0 | 25.0 | 0.9 | 14.8 | 0.6 | 19.5 | 3.2 | 0.6 | 0.2 | 4.9 | 41.5 | 345.3 | 6.0 | 16.4 |
| 215 | 6 | 34.2 | 40.0 | 34.1 | 13.0 | 44.8 | 4.9 | 145.5 | -1.5 | 159.1 | 0.1 | 14.5 | -0.0 | 31.6 | 4.5 | 0.3 | 0.1 | 5.0 | 23.5 | 287.2 | 5.0 | 19.6 |
| 216 | 6 | 32.9 | 40.6 | 33.8 | 13.0 | 49.4 | 4.1 | 95.7 | -73.5 | 148.0 | 2.7 | 13.8 | 0.0 | 26.3 | 3.9 | 0.4 | 0.1 | 4.9 | 34.0 | 251.5 | 10.0 | 15.4 |

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

## Top outliers (of 156 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 203 | 6 | low_plates | run | - | 15.70 | -..2 | 6.85 |
| 203 | 6 | sea_ice_below_150 | run | - | 49.00 | -..10 | 3.9 |
| 203 | 6 | giant_lake_frames | run | - | 21.60 | -..5 | 3.32 |
| 210 | 6 | giant_lake_frames | run | - | 19.60 | -..5 | 2.92 |
| 212 | 6 | sea_ice_below_150 | run | - | 35.30 | -..10 | 2.53 |
| 216 | 6 | sea_ice_below_150 | run | - | 31.40 | -..10 | 2.14 |
| 203 | 6 | lake_max_mkm2 | 372-372 | 1 | 11.14 | -..1.0 | 2.11 |
| 201 | 6 | giant_lake_frames | run | - | 13.70 | -..5 | 1.74 |
| 207 | 6 | sea_ice_below_150 | run | - | 25.50 | -..10 | 1.55 |
| 210 | 6 | lake_max_mkm2 | 328-352 | 7 | 6.86 | -..1.0 | 1.498 |
| 211 | 6 | lake_max_mkm2 | 328-328 | 1 | 6.46 | -..1.0 | 1.136 |
| 203 | 6 | lake_max_mkm2 | 304-340 | 10 | 4.50 | -..1.0 | 0.976 |
| 204 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 214 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 203 | 6 | sea_level | 316-436 | 31 | -798.00 | -250..300 | 0.444 |
| 203 | 6 | sea_ice_m | 328-404 | 20 | -525.50 | -250..- | 0.395 |
| 207 | 6 | lake_max_mkm2 | 364-368 | 2 | 2.76 | -..1.0 | 0.381 |
| 211 | 6 | lake_pct | 328-328 | 1 | 6.96 | 0.2..3.0 | 0.294 |
| 201 | 6 | lake_max_mkm2 | 360-380 | 4 | 2.27 | -..1.0 | 0.293 |
| 201 | 6 | lake_max_mkm2 | 324-336 | 3 | 2.29 | -..1.0 | 0.289 |
| 203 | 6 | lake_pct | 372-372 | 1 | 6.84 | 0.2..3.0 | 0.285 |
| 216 | 6 | lake_max_mkm2 | 320-320 | 1 | 2.15 | -..1.0 | 0.24 |
| 204 | 6 | lake_max_mkm2 | 412-412 | 1 | 2.06 | -..1.0 | 0.219 |
| 209 | 6 | lake_max_mkm2 | 368-368 | 1 | 1.99 | -..1.0 | 0.206 |
| 205 | 6 | lake_max_mkm2 | 312-312 | 1 | 1.98 | -..1.0 | 0.204 |
| 202 | 6 | inland_pct | 300-492 | 49 | 0.41 | 8..30 | 0.203 |
| 209 | 6 | inland_pct | 300-500 | 50 | 0.72 | 8..30 | 0.197 |
| 204 | 6 | inland_pct | 300-500 | 50 | 0.89 | 8..30 | 0.193 |
| 205 | 6 | inland_pct | 300-500 | 51 | 1.00 | 8..30 | 0.192 |
| 208 | 6 | inland_pct | 316-500 | 46 | 0.62 | 8..30 | 0.19 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 201, L6 (run 0649d3)

![seed 201 L6](seed201_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.57 | 32.96 | 33.80 |  |
| cont_pct | 38.36 | 40.17 | 40.80 |  |
| cont_km | 33.64 | 34.40 | 35.95 |  |
| plates | 11.00 | 13.00 | 15.00 |  |
| ocean_age | 46.10 | 57.70 | 66.50 |  |
| speed | 3.45 | 4.37 | 5.56 |  |
| sea_level | -21.10 | 47.00 | 164.00 |  |
| sea_ice_m | -70.20 | -24.30 | -0.00 |  |
| sea_tect_m | 48.80 | 72.50 | 164.30 |  |
| ice_pct | 0.00 | 1.90 | 4.00 |  |
| temp | 11.50 | 17.20 | 19.80 |  |
| co2 | -0.95 | 0.75 | 1.72 |  |
| dry_pct | 24.15 | 26.47 | 28.97 |  |
| inland_pct | 2.60 | 5.82 | 10.69 | 308-384: 2.60; 396-500: 2.75 |
| lake_pct | 0.27 | 0.57 | 2.11 |  |
| lake_max_mkm2 | 0.03 | 0.12 | 2.29 | 324-336: 2.29; 360-380: 2.27 |
| max_elev_km | 4.45 | 5.03 | 7.86 |  |
| trees_pct | 3.60 | 34.01 | 43.69 | 468-484: 3.60 |
| npp | 242.60 | 346.20 | 381.70 |  |
| landmasses | 6.00 | 10.00 | 22.00 |  |
| largest_pct | 18.50 | 30.20 | 33.60 |  |

### Seed 202, L6 (run 0c87fe)

![seed 202 L6](seed202_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.04 | 33.62 | 34.80 |  |
| cont_pct | 38.94 | 40.62 | 41.97 |  |
| cont_km | 32.52 | 33.77 | 34.69 |  |
| plates | 7.00 | 13.00 | 15.00 |  |
| ocean_age | 42.80 | 50.80 | 70.90 |  |
| speed | 2.88 | 4.82 | 5.46 |  |
| sea_level | -122.60 | 89.00 | 169.60 |  |
| sea_ice_m | -13.80 | -7.00 | -2.80 |  |
| sea_tect_m | -110.80 | 97.70 | 174.90 |  |
| ice_pct | 0.20 | 0.50 | 1.00 |  |
| temp | 14.70 | 17.60 | 20.40 |  |
| co2 | -1.36 | 0.34 | 0.89 |  |
| dry_pct | 9.81 | 18.87 | 34.57 | 412-436: 9.81 |
| inland_pct | 0.41 | 3.57 | 9.59 | 300-492: 0.41 |
| lake_pct | 0.17 | 0.39 | 1.32 | 320-320: 0.19; 428-428: 0.17 |
| lake_max_mkm2 | 0.03 | 0.09 | 0.83 |  |
| max_elev_km | 3.60 | 4.62 | 8.41 |  |
| trees_pct | 1.98 | 29.32 | 55.51 | 376-404: 55.51; 468-468: 6.14; 492-500: 1.98 |
| npp | 218.10 | 316.85 | 376.60 |  |
| landmasses | 3.00 | 13.00 | 20.00 |  |
| largest_pct | 7.50 | 14.00 | 28.70 |  |

### Seed 203, L6 (run 95fa44)

![seed 203 L6](seed203_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.08 | 33.41 | 35.51 |  |
| cont_pct | 38.02 | 41.55 | 42.52 |  |
| cont_km | 31.92 | 32.51 | 35.28 |  |
| plates | 4.00 | 7.00 | 10.00 | 300-304: 4; 324-344: 4 |
| ocean_age | 50.60 | 84.10 | 107.80 |  |
| speed | 2.19 | 5.18 | 6.09 |  |
| sea_level | -798.00 | -387.40 | 12.30 | 316-436: -798.00 |
| sea_ice_m | -525.50 | -140.40 | -4.50 | 328-404: -525.50 |
| sea_tect_m | -323.40 | -238.60 | 23.30 | 336-424: -323.40 |
| ice_pct | 0.40 | 4.40 | 12.50 | 332-364: 12.50 |
| temp | 6.60 | 13.20 | 18.00 | 332-340: 6.60 |
| co2 | -2.18 | 0.00 | 0.83 |  |
| dry_pct | 23.92 | 27.79 | 33.11 |  |
| inland_pct | 2.50 | 5.06 | 32.67 | 328-336: 32.67; 376-500: 2.50 |
| lake_pct | 0.18 | 0.64 | 6.84 | 308-312: 3.43; 328-328: 3.51; 372-372: 6.84; 500-500: 0.18 |
| lake_max_mkm2 | 0.03 | 0.22 | 11.14 | 304-340: 4.50; 372-372: 11.14 |
| max_elev_km | 4.30 | 5.64 | 9.31 |  |
| trees_pct | 4.80 | 25.69 | 34.84 | 300-308: 5.83; 328-360: 4.80 |
| npp | 95.60 | 365.30 | 420.80 | 364-392: 95.60 |
| landmasses | 2.00 | 6.00 | 14.00 | 352-352: 2; 368-368: 2 |
| largest_pct | 11.30 | 25.10 | 36.00 | 328-376: 36.00 |

### Seed 204, L6 (run 5389fb)

![seed 204 L6](seed204_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.50 | 33.38 | 34.24 |  |
| cont_pct | 38.54 | 40.40 | 41.69 |  |
| cont_km | 32.58 | 33.93 | 34.83 |  |
| plates | 6.00 | 9.00 | 13.00 |  |
| ocean_age | 48.50 | 64.00 | 85.70 |  |
| speed | 3.03 | 3.92 | 5.06 |  |
| sea_level | -230.90 | -46.70 | 95.60 |  |
| sea_ice_m | -98.40 | -23.00 | -13.50 |  |
| sea_tect_m | -168.00 | -20.00 | 118.50 |  |
| ice_pct | 1.20 | 1.90 | 6.00 |  |
| temp | 12.10 | 16.90 | 19.90 |  |
| co2 | -0.38 | 0.22 | 0.87 |  |
| dry_pct | 15.13 | 17.30 | 27.45 |  |
| inland_pct | 0.89 | 3.14 | 8.44 | 300-500: 0.89 |
| lake_pct | 0.22 | 0.59 | 2.54 |  |
| lake_max_mkm2 | 0.04 | 0.11 | 2.06 | 308-308: 1.64; 320-320: 1.16; 344-344: 1.02; 412-412: 2.06 |
| max_elev_km | 5.23 | 6.94 | 7.96 |  |
| trees_pct | 29.01 | 36.24 | 45.44 |  |
| npp | 172.50 | 352.90 | 402.20 | 384-388: 172.50; 404-404: 199.20 |
| landmasses | 6.00 | 9.00 | 16.00 |  |
| largest_pct | 11.90 | 22.20 | 26.70 |  |

### Seed 205, L6 (run 4e9665)

![seed 205 L6](seed205_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.24 | 32.91 | 34.20 |  |
| cont_pct | 39.32 | 40.80 | 41.48 |  |
| cont_km | 32.95 | 33.35 | 34.71 |  |
| plates | 9.00 | 14.00 | 16.00 |  |
| ocean_age | 54.20 | 62.10 | 80.40 |  |
| speed | 2.46 | 4.24 | 5.27 |  |
| sea_level | -177.30 | 63.00 | 100.70 |  |
| sea_ice_m | -146.50 | -17.70 | -13.00 |  |
| sea_tect_m | -133.30 | 78.00 | 114.00 |  |
| ice_pct | 0.90 | 1.50 | 5.20 |  |
| temp | 10.10 | 17.60 | 23.50 |  |
| co2 | -0.46 | 0.66 | 1.36 |  |
| dry_pct | 18.14 | 22.91 | 27.00 |  |
| inland_pct | 1.00 | 2.90 | 5.96 | 300-500: 1.00 |
| lake_pct | 0.18 | 0.35 | 1.98 | 404-412: 0.18 |
| lake_max_mkm2 | 0.03 | 0.09 | 1.98 | 300-300: 1.05; 312-312: 1.98 |
| max_elev_km | 4.20 | 5.79 | 8.53 |  |
| trees_pct | 21.33 | 37.72 | 49.08 |  |
| npp | 260.50 | 373.20 | 429.30 |  |
| landmasses | 5.00 | 11.00 | 15.00 |  |
| largest_pct | 10.90 | 11.30 | 19.00 |  |

### Seed 206, L6 (run 246968)

![seed 206 L6](seed206_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.47 | 33.77 | 34.21 |  |
| cont_pct | 39.48 | 39.98 | 41.65 |  |
| cont_km | 33.00 | 33.98 | 34.59 |  |
| plates | 12.00 | 15.00 | 18.00 |  |
| ocean_age | 46.60 | 51.00 | 59.90 |  |
| speed | 3.49 | 4.55 | 5.27 |  |
| sea_level | 28.50 | 104.30 | 142.20 |  |
| sea_ice_m | -30.70 | -7.70 | -0.00 |  |
| sea_tect_m | 30.30 | 115.80 | 142.20 |  |
| ice_pct | 0.00 | 0.70 | 1.50 |  |
| temp | 13.20 | 18.50 | 23.40 |  |
| co2 | -0.53 | 0.05 | 0.64 |  |
| dry_pct | 20.11 | 31.81 | 36.37 |  |
| inland_pct | 3.28 | 5.82 | 15.29 | 300-308: 4.41; 320-332: 4.47; 344-380: 4.37; 392-436: 4.11; +1 more |
| lake_pct | 0.11 | 0.30 | 1.75 | 464-464: 0.19; 480-492: 0.11 |
| lake_max_mkm2 | 0.03 | 0.05 | 1.20 | 304-304: 1.20 |
| max_elev_km | 3.52 | 4.42 | 7.08 |  |
| trees_pct | 9.99 | 23.79 | 46.86 | 444-444: 9.99 |
| npp | 129.80 | 234.70 | 396.90 | 348-372: 137.70; 384-384: 173.00; 436-444: 129.80 |
| landmasses | 4.00 | 7.00 | 11.00 |  |
| largest_pct | 9.20 | 18.40 | 26.50 |  |

### Seed 207, L6 (run ccafc7)

![seed 207 L6](seed207_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.43 | 32.23 | 34.42 |  |
| cont_pct | 36.79 | 38.05 | 39.60 |  |
| cont_km | 34.67 | 35.65 | 36.78 |  |
| plates | 8.00 | 11.00 | 14.00 |  |
| ocean_age | 52.40 | 63.60 | 78.40 |  |
| speed | 3.01 | 4.24 | 4.74 |  |
| sea_level | -291.20 | -126.70 | 59.70 | 468-484: -291.20 |
| sea_ice_m | -182.70 | -69.00 | -9.40 |  |
| sea_tect_m | -133.70 | -35.60 | 69.30 |  |
| ice_pct | 0.80 | 3.50 | 7.10 |  |
| temp | 10.90 | 14.30 | 20.30 |  |
| co2 | -1.01 | -0.01 | 0.96 |  |
| dry_pct | 20.27 | 25.20 | 30.54 |  |
| inland_pct | 3.25 | 7.09 | 13.25 | 300-356: 3.25; 372-440: 3.98; 452-496: 5.75 |
| lake_pct | 0.31 | 0.58 | 2.25 |  |
| lake_max_mkm2 | 0.04 | 0.11 | 2.76 | 364-368: 2.76; 448-448: 1.11 |
| max_elev_km | 5.41 | 6.98 | 8.08 |  |
| trees_pct | 2.49 | 35.75 | 48.00 | 432-444: 2.49 |
| npp | 102.00 | 252.30 | 370.60 | 412-444: 102.00 |
| landmasses | 4.00 | 7.00 | 14.00 |  |
| largest_pct | 15.70 | 16.50 | 34.40 |  |

### Seed 208, L6 (run 615d75)

![seed 208 L6](seed208_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.95 | 32.85 | 33.49 |  |
| cont_pct | 38.91 | 40.15 | 40.71 |  |
| cont_km | 33.30 | 33.54 | 34.50 |  |
| plates | 12.00 | 15.00 | 17.00 |  |
| ocean_age | 47.60 | 53.90 | 61.60 |  |
| speed | 2.49 | 4.44 | 5.83 |  |
| sea_level | -51.10 | 108.20 | 148.40 |  |
| sea_ice_m | -18.40 | -4.90 | -0.00 |  |
| sea_tect_m | -42.60 | 114.80 | 148.50 |  |
| ice_pct | 0.00 | 0.50 | 1.20 |  |
| temp | 11.10 | 18.60 | 24.50 |  |
| co2 | -1.02 | -0.12 | 1.42 |  |
| dry_pct | 16.61 | 22.90 | 46.42 | 304-312: 46.42 |
| inland_pct | 0.62 | 2.72 | 13.05 | 316-500: 0.62 |
| lake_pct | 0.17 | 0.33 | 1.59 | 324-324: 0.17 |
| lake_max_mkm2 | 0.03 | 0.06 | 1.31 | 484-484: 1.31 |
| max_elev_km | 4.41 | 6.76 | 8.37 |  |
| trees_pct | 2.35 | 24.59 | 45.77 | 376-420: 2.35 |
| npp | 102.00 | 304.65 | 387.10 | 384-420: 102.00 |
| landmasses | 3.00 | 9.00 | 14.00 |  |
| largest_pct | 9.20 | 17.00 | 33.40 |  |

### Seed 209, L6 (run 548bba)

![seed 209 L6](seed209_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.49 | 33.31 | 33.86 |  |
| cont_pct | 38.89 | 40.13 | 40.90 |  |
| cont_km | 32.76 | 33.61 | 34.78 |  |
| plates | 9.00 | 11.00 | 13.00 |  |
| ocean_age | 52.70 | 57.60 | 61.90 |  |
| speed | 3.35 | 4.44 | 5.04 |  |
| sea_level | 1.80 | 29.80 | 77.80 |  |
| sea_ice_m | -20.80 | -6.90 | -0.10 |  |
| sea_tect_m | 6.00 | 38.50 | 83.80 |  |
| ice_pct | 0.00 | 0.50 | 1.90 |  |
| temp | 15.50 | 18.60 | 21.70 |  |
| co2 | -1.70 | -0.03 | 0.92 |  |
| dry_pct | 13.86 | 24.58 | 38.11 |  |
| inland_pct | 0.72 | 3.71 | 8.29 | 300-500: 0.72 |
| lake_pct | 0.16 | 0.51 | 1.42 | 344-344: 0.19; 364-364: 0.16; 408-408: 0.19 |
| lake_max_mkm2 | 0.03 | 0.14 | 1.99 | 368-368: 1.99; 420-420: 1.32; 436-436: 1.11 |
| max_elev_km | 4.88 | 6.32 | 8.34 |  |
| trees_pct | 0.88 | 28.61 | 43.10 | 432-500: 0.88 |
| npp | 108.50 | 255.75 | 369.70 | 432-432: 108.50 |
| landmasses | 4.00 | 9.00 | 19.00 |  |
| largest_pct | 17.40 | 19.70 | 27.80 |  |

### Seed 210, L6 (run 82ed18)

![seed 210 L6](seed210_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.05 | 33.04 | 35.21 |  |
| cont_pct | 40.51 | 41.91 | 43.22 |  |
| cont_km | 31.40 | 32.02 | 33.51 |  |
| plates | 6.00 | 9.00 | 10.00 |  |
| ocean_age | 57.70 | 63.50 | 81.20 |  |
| speed | 3.26 | 4.04 | 4.80 |  |
| sea_level | -168.70 | -54.90 | -29.50 |  |
| sea_ice_m | -78.10 | -17.10 | -2.60 |  |
| sea_tect_m | -166.10 | -21.90 | -4.40 |  |
| ice_pct | 0.20 | 1.30 | 4.40 |  |
| temp | 12.60 | 16.80 | 20.40 |  |
| co2 | -0.76 | 0.10 | 0.95 |  |
| dry_pct | 8.60 | 18.10 | 22.67 | 388-424: 8.60 |
| inland_pct | 0.23 | 2.25 | 16.52 | 300-332: 1.51; 356-500: 0.23 |
| lake_pct | 0.24 | 0.59 | 4.96 | 332-348: 4.96 |
| lake_max_mkm2 | 0.04 | 0.24 | 6.86 | 312-312: 1.03; 328-352: 6.86; 412-416: 1.51 |
| max_elev_km | 4.78 | 6.21 | 7.91 |  |
| trees_pct | 14.16 | 39.62 | 63.17 | 392-412: 63.17 |
| npp | 175.40 | 334.20 | 439.00 | 424-432: 175.40 |
| landmasses | 3.00 | 6.00 | 12.00 |  |
| largest_pct | 16.70 | 23.40 | 28.60 |  |

### Seed 211, L6 (run 04185f)

![seed 211 L6](seed211_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.05 | 33.24 | 34.64 |  |
| cont_pct | 38.04 | 41.44 | 42.72 |  |
| cont_km | 32.57 | 32.99 | 35.69 |  |
| plates | 6.00 | 10.00 | 13.00 |  |
| ocean_age | 41.70 | 61.10 | 71.60 |  |
| speed | 3.28 | 4.12 | 5.82 |  |
| sea_level | -298.30 | -84.70 | 172.40 | 468-476: -298.30 |
| sea_ice_m | -260.60 | -55.40 | -0.00 | 468-468: -260.60 |
| sea_tect_m | -121.10 | 12.70 | 174.00 |  |
| ice_pct | 0.00 | 2.60 | 7.90 |  |
| temp | 10.00 | 15.90 | 22.40 |  |
| co2 | -1.63 | -0.11 | 0.74 |  |
| dry_pct | 20.48 | 24.16 | 46.20 | 300-304: 46.20 |
| inland_pct | 0.86 | 3.84 | 9.85 | 316-500: 0.86 |
| lake_pct | 0.21 | 0.39 | 6.96 | 328-328: 6.96 |
| lake_max_mkm2 | 0.03 | 0.10 | 6.46 | 328-328: 6.46; 344-348: 1.10 |
| max_elev_km | 3.92 | 5.63 | 8.32 |  |
| trees_pct | 2.26 | 21.82 | 37.83 | 324-332: 7.27; 444-500: 2.26 |
| npp | 196.70 | 212.30 | 237.20 | 464-464: 196.70 |
| landmasses | 4.00 | 8.00 | 16.00 |  |
| largest_pct | 12.50 | 23.10 | 34.50 |  |

### Seed 212, L6 (run 7531a7)

![seed 212 L6](seed212_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.98 | 32.60 | 33.37 |  |
| cont_pct | 38.05 | 39.38 | 40.98 |  |
| cont_km | 33.49 | 34.69 | 35.84 |  |
| plates | 10.00 | 13.00 | 17.00 |  |
| ocean_age | 43.00 | 49.10 | 64.50 |  |
| speed | 3.55 | 4.32 | 5.37 |  |
| sea_level | -269.70 | 133.60 | 176.80 | 456-464: -269.70 |
| sea_ice_m | -299.10 | -68.20 | -17.60 | 444-464: -299.10 |
| sea_tect_m | -1.50 | 163.50 | 214.60 |  |
| ice_pct | 1.30 | 3.90 | 10.70 | 444-464: 10.70 |
| temp | 8.60 | 14.80 | 18.80 |  |
| co2 | -0.71 | 0.55 | 1.08 |  |
| dry_pct | 10.43 | 18.61 | 32.25 | 392-400: 10.43; 412-412: 11.40 |
| inland_pct | 0.97 | 4.41 | 9.27 | 300-464: 0.97; 476-500: 2.11 |
| lake_pct | 0.15 | 0.45 | 1.04 | 360-368: 0.15 |
| lake_max_mkm2 | 0.01 | 0.07 | 0.49 |  |
| max_elev_km | 4.26 | 5.61 | 8.44 |  |
| trees_pct | 14.20 | 33.51 | 54.28 | 376-404: 54.28 |
| npp | 207.80 | 304.25 | 407.60 |  |
| landmasses | 4.00 | 9.00 | 13.00 |  |
| largest_pct | 11.20 | 17.10 | 26.40 |  |

### Seed 213, L6 (run 550c21)

![seed 213 L6](seed213_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.77 | 33.39 | 34.70 |  |
| cont_pct | 39.22 | 41.51 | 42.15 |  |
| cont_km | 31.86 | 32.77 | 34.37 |  |
| plates | 9.00 | 12.00 | 15.00 |  |
| ocean_age | 45.60 | 49.30 | 54.60 |  |
| speed | 3.65 | 4.88 | 5.59 |  |
| sea_level | -88.40 | 93.20 | 155.40 |  |
| sea_ice_m | -73.10 | -12.30 | -0.00 |  |
| sea_tect_m | -16.60 | 115.10 | 161.70 |  |
| ice_pct | 0.00 | 1.00 | 2.90 |  |
| temp | 11.70 | 14.70 | 19.90 |  |
| co2 | -0.27 | 0.09 | 0.57 |  |
| dry_pct | 19.64 | 24.96 | 38.33 |  |
| inland_pct | 0.50 | 2.43 | 10.61 | 304-316: 4.88; 328-500: 0.50 |
| lake_pct | 0.13 | 0.27 | 0.77 | 300-308: 0.18; 360-360: 0.13; 396-396: 0.17; 428-440: 0.15 |
| lake_max_mkm2 | 0.03 | 0.06 | 1.03 | 412-412: 1.03 |
| max_elev_km | 4.10 | 5.38 | 7.57 |  |
| trees_pct | 23.79 | 33.42 | 45.55 |  |
| npp | 244.60 | 317.40 | 389.60 |  |
| landmasses | 2.00 | 9.00 | 14.00 | 300-300: 2 |
| largest_pct | 20.40 | 31.30 | 34.40 |  |

### Seed 214, L6 (run 43e321)

![seed 214 L6](seed214_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.18 | 32.56 | 33.35 |  |
| cont_pct | 40.51 | 41.15 | 42.44 |  |
| cont_km | 31.74 | 32.58 | 33.09 |  |
| plates | 9.00 | 10.00 | 12.00 |  |
| ocean_age | 52.20 | 59.30 | 67.10 |  |
| speed | 3.19 | 4.13 | 4.86 |  |
| sea_level | -137.40 | -7.10 | 25.40 |  |
| sea_ice_m | -177.70 | -15.00 | -1.10 |  |
| sea_tect_m | -129.40 | 25.00 | 81.80 |  |
| ice_pct | 0.10 | 0.90 | 6.10 |  |
| temp | 9.70 | 14.80 | 22.10 |  |
| co2 | -0.47 | 0.57 | 1.35 |  |
| dry_pct | 15.74 | 19.46 | 23.06 |  |
| inland_pct | 1.52 | 3.23 | 6.96 | 300-500: 1.52 |
| lake_pct | 0.35 | 0.62 | 2.01 |  |
| lake_max_mkm2 | 0.07 | 0.20 | 1.82 | 372-384: 1.82 |
| max_elev_km | 4.19 | 4.87 | 5.96 |  |
| trees_pct | 20.65 | 41.54 | 53.42 | 360-380: 53.42; 400-404: 51.94; 420-444: 53.37 |
| npp | 185.20 | 345.30 | 419.90 | 448-448: 185.20 |
| landmasses | 3.00 | 6.00 | 10.00 |  |
| largest_pct | 10.20 | 16.40 | 21.30 |  |

### Seed 215, L6 (run 2438b9)

![seed 215 L6](seed215_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.10 | 34.18 | 34.63 |  |
| cont_pct | 37.93 | 40.05 | 40.85 |  |
| cont_km | 33.49 | 34.15 | 35.72 |  |
| plates | 11.00 | 13.00 | 15.00 |  |
| ocean_age | 36.00 | 44.80 | 58.70 |  |
| speed | 3.40 | 4.86 | 5.16 |  |
| sea_level | -31.80 | 145.50 | 245.30 |  |
| sea_ice_m | -26.20 | -1.50 | -0.00 |  |
| sea_tect_m | -26.40 | 159.10 | 245.40 |  |
| ice_pct | 0.00 | 0.10 | 1.20 |  |
| temp | 10.90 | 14.50 | 19.90 |  |
| co2 | -0.54 | -0.03 | 1.01 |  |
| dry_pct | 26.80 | 31.58 | 41.59 |  |
| inland_pct | 1.72 | 4.46 | 25.03 | 304-304: 5.55; 324-328: 5.70; 344-412: 1.72; 424-500: 1.91 |
| lake_pct | 0.15 | 0.34 | 2.02 | 324-324: 0.16; 344-364: 0.15; 404-408: 0.17; 464-468: 0.16 |
| lake_max_mkm2 | 0.03 | 0.07 | 1.64 | 416-416: 1.16; 440-448: 1.64 |
| max_elev_km | 3.87 | 5.01 | 8.38 |  |
| trees_pct | 14.00 | 23.46 | 37.65 |  |
| npp | 242.40 | 287.20 | 346.60 |  |
| landmasses | 2.00 | 5.00 | 10.00 | 316-316: 2; 492-500: 2 |
| largest_pct | 18.90 | 19.60 | 34.40 |  |

### Seed 216, L6 (run a8474f)

![seed 216 L6](seed216_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.58 | 32.92 | 34.35 |  |
| cont_pct | 38.61 | 40.65 | 41.15 |  |
| cont_km | 33.18 | 33.79 | 35.21 |  |
| plates | 10.00 | 13.00 | 18.00 |  |
| ocean_age | 40.50 | 49.40 | 68.70 |  |
| speed | 3.25 | 4.08 | 5.20 |  |
| sea_level | -290.80 | 95.70 | 178.90 | 456-500: -290.80 |
| sea_ice_m | -220.60 | -73.50 | -17.80 |  |
| sea_tect_m | -71.60 | 148.00 | 211.40 |  |
| ice_pct | 1.30 | 2.70 | 7.60 |  |
| temp | 8.60 | 13.80 | 19.10 |  |
| co2 | -0.83 | 0.03 | 1.39 |  |
| dry_pct | 19.14 | 26.27 | 31.84 |  |
| inland_pct | 1.72 | 3.88 | 13.74 | 304-312: 4.83; 324-500: 1.72 |
| lake_pct | 0.15 | 0.43 | 2.29 | 404-412: 0.15 |
| lake_max_mkm2 | 0.03 | 0.06 | 2.15 | 320-320: 2.15; 340-340: 1.37; 460-460: 1.59 |
| max_elev_km | 3.69 | 4.87 | 9.13 |  |
| trees_pct | 13.86 | 33.97 | 42.82 |  |
| npp | 108.70 | 251.50 | 395.60 | 396-444: 108.70 |
| landmasses | 4.00 | 10.00 | 13.00 |  |
| largest_pct | 11.30 | 15.40 | 25.90 |  |

## Determinism

(not run)
