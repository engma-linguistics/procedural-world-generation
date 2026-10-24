# Health sweep 2026-10-23 17:50

Commit None. 32 runs (default params, `--every 4`) at 6 workers x 3 numba threads; simulations 37.2 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | 055c46 | 339 | 104 / 316 | 12.0 | 0 | 5.9 | 0.968 | 13.7 | 0.0 | ok | ok | 64.7 |
| 2 | 6 | 500 | 793b2e | 342 | 116 / 268 | 15.3 | 0 | 2.0 | 0.972 | 17.6 | 0.0 | F | F: icehouse 71% of the time, outside 5-70% | 70.6 |
| 11 | 6 | 500 | ecbe27 | 403 | 116 / 272 | 13.6 | 0 | 3.9 | 0.98 | 33.3 | 0.0 | ok | ok | 52.9 |
| 21 | 6 | 500 | 146f5f | 322 | 116 / 336 | 8.8 | 0 | 2.0 | 0.958 | 0.0 | 0.0 | ok | ok | 56.9 |
| 3199 | 6 | 500 | e3ea9f | 300 | 112 / 344 | 8.9 | 0 | 0.0 | 0.932 | 0.0 | 0.0 | ok | ok | 9.8 |
| 42 | 6 | 500 | a5d12f | 321 | 116 / 288 | 13.8 | 0 | 23.5 | 0.967 | 49.0 | 0.0 | ok | ok | 66.7 |
| 77 | 6 | 500 | f8ed4c | 338 | 112 / 272 | 9.5 | 0 | 0.0 | 0.965 | 0.0 | 0.0 | ok | ok | 13.7 |
| 505 | 6 | 500 | 05c659 | 299 | 108 / 328 | 7.0 | 0 | 2.0 | 0.96 | 0.0 | 0.0 | ok | F: icehouse 4% of the time, outside 5-70% | 3.9 |
| 101 | 6 | 500 | 6bb00d | 337 | 116 / 352 | 9.6 | 0 | 0.0 | 0.978 | 0.0 | 0.0 | ok | ok | 23.5 |
| 102 | 6 | 500 | 54ea2f | 390 | 116 / 344 | 5.1 | 0 | 3.9 | 0.971 | 19.6 | 0.0 | ok | F: icehouse 100% of the time, outside 5-70% | 100.0 |
| 103 | 6 | 500 | 1b84d1 | 394 | 116 / 336 | 11.1 | 0 | 5.9 | 0.953 | 5.9 | 0.0 | ok | ok | 54.9 |
| 104 | 6 | 500 | e8c3a5 | 345 | 116 / 312 | 8.6 | 0 | 0.0 | 0.974 | 0.0 | 0.0 | ok | ok | 9.8 |
| 105 | 6 | 500 | 3d42ce | 410 | 108 / 312 | 10.1 | 0 | 0.0 | 0.965 | 25.5 | 0.0 | ok | ok | 31.4 |
| 106 | 6 | 500 | c491e9 | 365 | 116 / 312 | 13.2 | 0 | 7.8 | 0.971 | 21.6 | 0.0 | ok | ok | 66.7 |
| 107 | 6 | 500 | 41bd87 | 435 | 100 / 300 | 6.9 | 0 | 21.6 | 0.971 | 15.7 | 0.0 | ok | ok | 54.9 |
| 108 | 6 | 500 | 2306db | 473 | 104 / 320 | 6.1 | 0 | 17.6 | 0.985 | 17.6 | 0.0 | ok | F: icehouse 96% of the time, outside 5-70% | 96.1 |
| 201 | 6 | 500 | e38080 | 534 | 120 / 344 | 8.5 | 0 | 19.6 | 0.978 | 2.0 | 0.0 | ok | F: icehouse 71% of the time, outside 5-70% | 70.6 |
| 202 | 6 | 500 | 5dc5d0 | 466 | 116 / 328 | 8.3 | 0 | 0.0 | 0.956 | 5.9 | 0.0 | ok | ok | 25.5 |
| 203 | 6 | 500 | 3bca03 | 504 | 112 / 260 | 9.1 | 0 | 7.8 | 0.982 | 0.0 | 0.0 | ok | ok | 19.6 |
| 204 | 6 | 500 | 13a3fc | 526 | 116 / 348 | 11.1 | 0 | 2.0 | 0.949 | 9.8 | 0.0 | ok | F: icehouse 76% of the time, outside 5-70% | 76.5 |
| 205 | 6 | 500 | ce4649 | 467 | 104 / 312 | 10.8 | 0 | 5.9 | 0.97 | 0.0 | 0.0 | ok | ok | 17.6 |
| 206 | 6 | 500 | 6ed4ea | 433 | 116 / 332 | 11.4 | 0 | 15.7 | 0.965 | 13.7 | 0.0 | ok | ok | 19.6 |
| 207 | 6 | 500 | 264f96 | 416 | 116 / 360 | 7.8 | 0 | 5.9 | 0.98 | 27.5 | 0.0 | ok | F: icehouse 73% of the time, outside 5-70% | 72.5 |
| 208 | 6 | 500 | bd5556 | 450 | 116 / 344 | 7.0 | 0 | 5.9 | 0.952 | 0.0 | 0.0 | ok | ok | 5.9 |
| 209 | 6 | 500 | 24926e | 358 | 116 / 324 | 8.9 | 0 | 3.9 | 0.961 | 0.0 | 0.0 | ok | ok | 33.3 |
| 210 | 6 | 500 | 1a1b8b | 358 | 116 / 356 | 10.2 | 0 | 7.8 | 0.987 | 0.0 | 0.0 | ok | ok | 37.3 |
| 211 | 6 | 500 | 0156d2 | 354 | 96 / 328 | 8.0 | 0 | 5.9 | 0.938 | 0.0 | 0.0 | ok | F: icehouse 2% of the time, outside 5-70% | 2.0 |
| 212 | 6 | 500 | 477df0 | 365 | 112 / 340 | 9.3 | 0 | 9.8 | 0.948 | 0.0 | 0.0 | ok | ok | 62.7 |
| 213 | 6 | 500 | b7e213 | 351 | 112 / 360 | 8.4 | 0 | 25.5 | 0.975 | 0.0 | 0.0 | ok | ok | 5.9 |
| 214 | 6 | 500 | 16fdb1 | 350 | 108 / 244 | 8.5 | 0 | 2.0 | 0.967 | 74.5 | 0.0 | ok | F: deep era 348-496 Myr lasts 152 > 150; icehouse 98% of the time, outside 5-70% | 98.0 |
| 215 | 6 | 500 | bc0075 | 281 | 96 / 332 | 10.4 | 0 | 0.0 | 0.978 | 0.0 | 0.0 | ok | ok | 11.8 |
| 216 | 6 | 500 | 4840ac | 318 | 104 / 336 | 7.0 | 0 | 13.7 | 0.968 | 0.0 | 0.0 | ok | ok | 66.7 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 32.0 | 41.3 | 32.9 | 12.0 | 60.5 | 4.2 | -35.5 | -44.9 | 11.9 | 2.3 | 14.3 | -0.2 | 19.3 | 2.6 | 0.4 | 0.1 | 5.2 | 29.0 | 329.9 | 8.0 | 10.2 |
| 2 | 6 | 33.6 | 40.0 | 33.9 | 12.0 | 57.9 | 3.6 | 51.1 | -49.2 | 76.9 | 2.3 | 15.4 | 0.6 | 23.4 | 2.6 | 0.4 | 0.1 | 5.3 | 37.1 | 336.8 | 8.0 | 28.6 |
| 11 | 6 | 33.0 | 40.1 | 34.1 | 12.0 | 55.3 | 4.1 | -7.6 | -40.4 | 58.6 | 2.0 | 15.2 | -0.1 | 21.9 | 4.9 | 0.7 | 0.3 | 4.9 | 32.7 | 271.4 | 10.0 | 14.0 |
| 21 | 6 | 34.2 | 41.7 | 32.3 | 12.0 | 60.4 | 4.1 | -4.2 | -29.4 | 14.5 | 1.2 | 14.1 | -0.5 | 25.4 | 2.4 | 0.3 | 0.1 | 5.6 | 11.6 | 322.5 | 9.0 | 21.8 |
| 3199 | 6 | 33.0 | 41.2 | 32.5 | 11.0 | 52.6 | 4.3 | 123.4 | -4.0 | 127.2 | 0.3 | 15.9 | 0.5 | 23.6 | 3.3 | 0.3 | 0.1 | 3.6 | 35.1 | 373.6 | 9.0 | 19.9 |
| 42 | 6 | 32.5 | 40.6 | 33.6 | 13.0 | 49.3 | 4.5 | -5.2 | -148.0 | 106.6 | 4.9 | 13.4 | 0.2 | 20.8 | 4.2 | 0.6 | 0.2 | 4.3 | 34.7 | 374.1 | 7.0 | 17.4 |
| 77 | 6 | 33.1 | 39.8 | 34.1 | 15.0 | 47.4 | 4.6 | 144.1 | -11.0 | 157.2 | 0.7 | 17.8 | 0.5 | 21.0 | 5.7 | 0.5 | 0.1 | 4.4 | 38.3 | 316.1 | 7.0 | 18.5 |
| 505 | 6 | 34.0 | 39.8 | 34.1 | 11.0 | 54.3 | 4.6 | 76.3 | -5.0 | 80.6 | 0.5 | 15.7 | -0.3 | 27.2 | 5.1 | 0.3 | 0.1 | 7.0 | 18.5 | 326.2 | 8.0 | 22.5 |
| 101 | 6 | 33.3 | 39.9 | 34.3 | 11.0 | 51.1 | 4.3 | 98.6 | -1.0 | 112.1 | 0.1 | 17.7 | -0.2 | 30.8 | 4.1 | 0.3 | 0.1 | 5.4 | 18.7 | 286.5 | 7.0 | 26.4 |
| 102 | 6 | 31.3 | 40.3 | 33.9 | 14.0 | 51.1 | 4.1 | -10.0 | -132.1 | 117.9 | 5.1 | 13.1 | -0.1 | 21.1 | 3.3 | 0.5 | 0.1 | 5.2 | 30.4 | 366.4 | 12.0 | 19.0 |
| 103 | 6 | 31.9 | 42.4 | 31.9 | 13.0 | 57.6 | 4.1 | 5.3 | -30.5 | 53.3 | 1.5 | 13.6 | -0.6 | 26.6 | 2.2 | 0.3 | 0.1 | 3.9 | 18.2 | 275.8 | 11.0 | 19.4 |
| 104 | 6 | 34.7 | 40.2 | 33.7 | 10.0 | 56.8 | 4.5 | 36.4 | -7.2 | 58.3 | 0.5 | 15.9 | 0.2 | 29.2 | 3.6 | 0.3 | 0.1 | 4.8 | 30.0 | 307.0 | 4.0 | 22.8 |
| 105 | 6 | 32.6 | 41.0 | 32.9 | 13.0 | 59.8 | 4.0 | 82.7 | -7.2 | 86.9 | 0.5 | 15.5 | 0.2 | 17.9 | 2.4 | 0.4 | 0.1 | 5.0 | 42.7 | 315.2 | 10.0 | 20.5 |
| 106 | 6 | 32.7 | 40.7 | 33.4 | 15.0 | 45.5 | 4.4 | 158.8 | -22.6 | 173.9 | 1.8 | 15.3 | 0.1 | 20.0 | 3.4 | 0.3 | 0.1 | 5.6 | 28.3 | 322.1 | 11.0 | 13.1 |
| 107 | 6 | 32.6 | 39.9 | 34.1 | 12.0 | 57.0 | 4.3 | 69.6 | -26.0 | 88.9 | 1.6 | 12.3 | -0.2 | 25.8 | 4.5 | 0.8 | 0.3 | 6.9 | 22.8 | 280.5 | 7.0 | 21.2 |
| 108 | 6 | 31.6 | 39.9 | 34.1 | 17.0 | 46.4 | 3.8 | 55.2 | -111.0 | 194.8 | 5.0 | 12.2 | 0.0 | 22.2 | 4.2 | 0.7 | 0.3 | 5.4 | 32.5 | 338.2 | 8.0 | 14.6 |
| 201 | 6 | 32.1 | 40.6 | 33.8 | 12.0 | 59.2 | 4.5 | -22.6 | -47.7 | 40.3 | 2.4 | 15.6 | 0.4 | 20.2 | 6.9 | 1.1 | 0.4 | 5.7 | 37.2 | 356.1 | 10.0 | 17.4 |
| 202 | 6 | 33.2 | 40.2 | 33.3 | 12.0 | 50.9 | 4.4 | 106.1 | -15.7 | 119.5 | 1.3 | 15.8 | -0.0 | 21.7 | 2.4 | 0.4 | 0.1 | 5.1 | 30.8 | 289.5 | 8.0 | 17.8 |
| 203 | 6 | 34.1 | 39.6 | 34.7 | 12.0 | 49.7 | 4.7 | 102.0 | -14.5 | 111.7 | 1.2 | 14.1 | -0.3 | 34.8 | 6.5 | 0.3 | 0.1 | 5.3 | 12.2 | 254.2 | 4.0 | 31.2 |
| 204 | 6 | 32.6 | 40.7 | 33.0 | 8.0 | 59.4 | 4.2 | -87.3 | -28.6 | -26.8 | 2.2 | 15.4 | -0.1 | 27.1 | 3.1 | 0.4 | 0.1 | 5.9 | 22.9 | 298.3 | 6.0 | 15.8 |
| 205 | 6 | 33.9 | 40.4 | 33.8 | 12.0 | 52.0 | 4.6 | 106.7 | -5.9 | 117.5 | 0.5 | 17.4 | 0.3 | 22.0 | 4.0 | 0.5 | 0.1 | 4.2 | 37.1 | 345.1 | 7.0 | 20.6 |
| 206 | 6 | 33.3 | 40.6 | 33.6 | 8.0 | 53.2 | 4.4 | 35.5 | -5.8 | 39.6 | 0.5 | 17.8 | 0.2 | 22.1 | 3.0 | 0.4 | 0.1 | 6.2 | 36.8 | 297.6 | 7.0 | 25.4 |
| 207 | 6 | 33.3 | 39.6 | 34.4 | 12.0 | 59.8 | 4.0 | 41.6 | -34.7 | 60.9 | 2.4 | 16.0 | 0.4 | 20.1 | 3.3 | 0.5 | 0.1 | 5.6 | 34.6 | 286.6 | 10.0 | 19.6 |
| 208 | 6 | 32.6 | 40.7 | 33.2 | 15.0 | 47.8 | 4.2 | 136.5 | -7.5 | 147.4 | 0.6 | 20.3 | 0.4 | 18.1 | 2.4 | 0.5 | 0.2 | 5.2 | 35.1 | 380.6 | 8.0 | 12.8 |
| 209 | 6 | 32.8 | 40.7 | 33.6 | 12.0 | 53.0 | 4.1 | 72.0 | -10.5 | 86.5 | 0.8 | 17.9 | -0.3 | 25.9 | 4.2 | 0.3 | 0.1 | 6.3 | 16.8 | 241.1 | 7.0 | 19.5 |
| 210 | 6 | 34.9 | 40.3 | 34.3 | 10.0 | 59.9 | 3.8 | -4.9 | -15.2 | 2.2 | 1.1 | 17.9 | 0.2 | 25.6 | 5.0 | 0.4 | 0.1 | 5.7 | 28.6 | 337.5 | 7.0 | 20.3 |
| 211 | 6 | 32.4 | 40.3 | 32.9 | 14.0 | 53.4 | 4.5 | 93.7 | -5.1 | 95.9 | 0.3 | 18.4 | -0.1 | 21.5 | 2.4 | 0.3 | 0.1 | 5.1 | 19.4 | 264.3 | 8.0 | 13.1 |
| 212 | 6 | 32.0 | 38.9 | 34.6 | 13.0 | 55.3 | 4.2 | 67.2 | -24.1 | 121.4 | 2.6 | 14.5 | 0.3 | 14.5 | 3.0 | 0.9 | 0.7 | 7.4 | 34.0 | 318.2 | 8.0 | 18.7 |
| 213 | 6 | 34.0 | 40.4 | 33.9 | 13.0 | 49.8 | 4.3 | 86.3 | -9.4 | 97.4 | 0.6 | 16.1 | 0.4 | 19.9 | 5.4 | 0.6 | 0.1 | 5.2 | 36.8 | 362.3 | 6.0 | 30.5 |
| 214 | 6 | 32.3 | 40.4 | 33.5 | 11.0 | 57.1 | 3.3 | -224.8 | -302.1 | 44.5 | 10.9 | 12.7 | 0.2 | 12.4 | 1.0 | 0.4 | 0.2 | 6.0 | 41.4 | 402.0 | 8.0 | 13.5 |
| 215 | 6 | 33.6 | 39.6 | 34.4 | 14.0 | 42.7 | 4.5 | 191.5 | -3.0 | 201.3 | 0.2 | 15.0 | -0.2 | 30.6 | 4.6 | 0.3 | 0.1 | 5.2 | 20.3 | 323.7 | 6.0 | 17.1 |
| 216 | 6 | 32.9 | 39.7 | 34.5 | 14.0 | 45.7 | 4.7 | 123.2 | -23.6 | 158.5 | 1.8 | 16.3 | 0.7 | 21.2 | 6.2 | 0.7 | 0.2 | 5.2 | 38.4 | 364.1 | 10.0 | 14.1 |

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

## Top outliers (of 312 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 214 | 6 | sea_ice_below_150 | run | - | 74.50 | -..10 | 6.45 |
| 213 | 6 | giant_lake_frames | run | - | 25.50 | -..5 | 4.1 |
| 42 | 6 | sea_ice_below_150 | run | - | 49.00 | -..10 | 3.9 |
| 42 | 6 | giant_lake_frames | run | - | 23.50 | -..5 | 3.7 |
| 107 | 6 | giant_lake_frames | run | - | 21.60 | -..5 | 3.32 |
| 201 | 6 | giant_lake_frames | run | - | 19.60 | -..5 | 2.92 |
| 42 | 6 | lake_max_mkm2 | 364-416 | 11 | 10.10 | -..1.0 | 2.614 |
| 108 | 6 | giant_lake_frames | run | - | 17.60 | -..5 | 2.52 |
| 11 | 6 | sea_ice_below_150 | run | - | 33.30 | -..10 | 2.33 |
| 206 | 6 | giant_lake_frames | run | - | 15.70 | -..5 | 2.14 |
| 206 | 6 | lake_max_mkm2 | 436-456 | 6 | 8.99 | -..1.0 | 1.978 |
| 207 | 6 | sea_ice_below_150 | run | - | 27.50 | -..10 | 1.75 |
| 216 | 6 | giant_lake_frames | run | - | 13.70 | -..5 | 1.74 |
| 105 | 6 | sea_ice_below_150 | run | - | 25.50 | -..10 | 1.55 |
| 102 | 6 | lake_max_mkm2 | 420-424 | 2 | 6.60 | -..1.0 | 1.209 |
| 106 | 6 | sea_ice_below_150 | run | - | 21.60 | -..10 | 1.16 |
| 205 | 6 | lake_max_mkm2 | 420-420 | 1 | 6.29 | -..1.0 | 1.1 |
| 102 | 6 | sea_ice_below_150 | run | - | 19.60 | -..10 | 0.96 |
| 212 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 216 | 6 | lake_max_mkm2 | 500-500 | 1 | 5.17 | -..1.0 | 0.867 |
| 216 | 6 | lake_max_mkm2 | 356-356 | 1 | 5.08 | -..1.0 | 0.848 |
| 216 | 6 | lake_max_mkm2 | 416-428 | 3 | 4.61 | -..1.0 | 0.807 |
| 213 | 6 | lake_max_mkm2 | 332-340 | 3 | 4.58 | -..1.0 | 0.802 |
| 42 | 6 | lake_max_mkm2 | 436-436 | 1 | 4.77 | -..1.0 | 0.784 |
| 2 | 6 | sea_ice_below_150 | run | - | 17.60 | -..10 | 0.76 |
| 108 | 6 | sea_ice_below_150 | run | - | 17.60 | -..10 | 0.76 |
| 213 | 6 | lake_max_mkm2 | 312-320 | 3 | 4.25 | -..1.0 | 0.726 |
| 107 | 6 | lake_max_mkm2 | 444-468 | 6 | 3.83 | -..1.0 | 0.702 |
| 205 | 6 | lake_max_mkm2 | 460-460 | 1 | 4.28 | -..1.0 | 0.683 |
| 107 | 6 | sea_ice_below_150 | run | - | 15.70 | -..10 | 0.57 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run 055c46)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.46 | 31.96 | 32.99 |  |
| cont_pct | 39.03 | 41.33 | 43.04 |  |
| cont_km | 31.77 | 32.91 | 35.19 |  |
| plates | 9.00 | 12.00 | 15.00 |  |
| ocean_age | 37.40 | 60.50 | 71.60 |  |
| speed | 2.14 | 4.19 | 5.13 |  |
| sea_level | -311.00 | -35.50 | 189.50 | 476-500: -311.00 |
| sea_ice_m | -238.70 | -44.90 | -2.30 |  |
| sea_tect_m | -85.70 | 11.90 | 192.20 |  |
| ice_pct | 0.20 | 2.30 | 7.40 |  |
| temp | 8.30 | 14.30 | 20.30 |  |
| co2 | -0.72 | -0.16 | 1.01 |  |
| dry_pct | 14.06 | 19.33 | 23.65 |  |
| inland_pct | 0.85 | 2.61 | 5.06 | 300-500: 0.85 |
| lake_pct | 0.24 | 0.42 | 2.49 |  |
| lake_max_mkm2 | 0.01 | 0.06 | 3.12 | 468-480: 3.12 |
| max_elev_km | 3.71 | 5.19 | 7.73 |  |
| trees_pct | 13.23 | 29.01 | 49.26 |  |
| npp | 148.60 | 329.90 | 478.90 | 356-388: 148.60 |
| landmasses | 4.00 | 8.00 | 13.00 |  |
| largest_pct | 7.10 | 10.20 | 21.10 |  |

### Seed 2, L6 (run 793b2e)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.29 | 33.56 | 35.22 |  |
| cont_pct | 39.33 | 39.99 | 40.72 |  |
| cont_km | 33.47 | 33.87 | 34.21 |  |
| plates | 8.00 | 12.00 | 14.00 |  |
| ocean_age | 41.50 | 57.90 | 79.20 |  |
| speed | 1.93 | 3.65 | 5.85 | 456-460: 1.93 |
| sea_level | -710.80 | 51.10 | 181.10 | 468-500: -710.80 |
| sea_ice_m | -539.80 | -49.20 | -2.70 | 480-500: -539.80 |
| sea_tect_m | -171.40 | 76.90 | 194.90 |  |
| ice_pct | 0.20 | 2.30 | 15.80 | 480-500: 15.80 |
| temp | 7.90 | 15.40 | 23.20 | 492-496: 7.90 |
| co2 | 0.12 | 0.65 | 1.60 |  |
| dry_pct | 15.96 | 23.43 | 28.89 |  |
| inland_pct | 0.33 | 2.63 | 6.10 | 300-500: 0.33 |
| lake_pct | 0.08 | 0.37 | 1.45 | 308-308: 0.20; 332-344: 0.08 |
| lake_max_mkm2 | 0.03 | 0.10 | 1.42 | 500-500: 1.42 |
| max_elev_km | 4.37 | 5.33 | 8.26 |  |
| trees_pct | 31.45 | 37.10 | 43.14 |  |
| npp | 249.30 | 336.80 | 517.40 |  |
| landmasses | 4.00 | 8.00 | 12.00 |  |
| largest_pct | 14.50 | 28.60 | 33.10 |  |

### Seed 11, L6 (run ecbe27)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.48 | 32.97 | 33.60 |  |
| cont_pct | 39.00 | 40.11 | 40.65 |  |
| cont_km | 33.67 | 34.08 | 34.84 |  |
| plates | 9.00 | 12.00 | 14.00 |  |
| ocean_age | 37.20 | 55.30 | 74.30 |  |
| speed | 3.32 | 4.09 | 5.11 |  |
| sea_level | -499.60 | -7.60 | 222.70 | 400-448: -499.60 |
| sea_ice_m | -377.30 | -40.40 | -0.00 | 400-448: -377.30 |
| sea_tect_m | -122.50 | 58.60 | 223.00 |  |
| ice_pct | 0.00 | 2.00 | 10.40 | 432-440: 10.40 |
| temp | 9.60 | 15.20 | 23.20 |  |
| co2 | -1.13 | -0.11 | 0.44 |  |
| dry_pct | 18.83 | 21.91 | 29.42 |  |
| inland_pct | 1.54 | 4.94 | 10.64 | 300-340: 3.25; 352-500: 1.54 |
| lake_pct | 0.25 | 0.74 | 1.65 |  |
| lake_max_mkm2 | 0.04 | 0.30 | 1.40 | 380-388: 1.40 |
| max_elev_km | 3.67 | 4.89 | 8.39 |  |
| trees_pct | 1.72 | 32.69 | 39.32 | 476-500: 1.72 |
| npp | 134.40 | 271.40 | 409.30 | 308-348: 134.40 |
| landmasses | 5.00 | 10.00 | 15.00 |  |
| largest_pct | 8.00 | 14.00 | 18.10 |  |

### Seed 21, L6 (run 146f5f)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.91 | 34.20 | 35.10 |  |
| cont_pct | 39.91 | 41.67 | 42.30 |  |
| cont_km | 32.06 | 32.32 | 34.38 |  |
| plates | 9.00 | 12.00 | 15.00 |  |
| ocean_age | 52.20 | 60.40 | 68.20 |  |
| speed | 3.06 | 4.06 | 5.51 |  |
| sea_level | -78.40 | -4.20 | 82.60 |  |
| sea_ice_m | -43.70 | -29.40 | -0.00 |  |
| sea_tect_m | -38.90 | 14.50 | 82.60 |  |
| ice_pct | 0.00 | 1.20 | 2.00 |  |
| temp | 11.40 | 14.10 | 20.20 |  |
| co2 | -1.36 | -0.51 | 0.12 |  |
| dry_pct | 20.90 | 25.44 | 30.78 |  |
| inland_pct | 0.79 | 2.41 | 5.95 | 300-500: 0.79 |
| lake_pct | 0.11 | 0.27 | 1.28 | 336-340: 0.17; 356-356: 0.17; 376-388: 0.11; 452-452: 0.18; +1 more |
| lake_max_mkm2 | 0.01 | 0.05 | 1.13 | 476-476: 1.13 |
| max_elev_km | 2.98 | 5.62 | 8.65 |  |
| trees_pct | 0.78 | 11.64 | 32.69 | 304-324: 0.78; 388-432: 2.25; 476-496: 3.91 |
| npp | 133.90 | 322.50 | 404.20 | 336-360: 133.90; 380-380: 191.10 |
| landmasses | 6.00 | 9.00 | 13.00 |  |
| largest_pct | 10.80 | 21.80 | 34.50 |  |

### Seed 3199, L6 (run e3ea9f)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.95 | 33.03 | 34.37 |  |
| cont_pct | 39.94 | 41.22 | 42.39 |  |
| cont_km | 31.72 | 32.50 | 33.19 |  |
| plates | 8.00 | 11.00 | 13.00 |  |
| ocean_age | 45.30 | 52.60 | 81.40 |  |
| speed | 1.77 | 4.26 | 5.09 | 492-500: 1.77 |
| sea_level | -133.60 | 123.40 | 172.40 |  |
| sea_ice_m | -64.30 | -4.00 | -0.00 |  |
| sea_tect_m | -69.20 | 127.20 | 172.40 |  |
| ice_pct | 0.00 | 0.30 | 3.60 |  |
| temp | 10.80 | 15.90 | 19.70 |  |
| co2 | -0.29 | 0.52 | 0.81 |  |
| dry_pct | 20.84 | 23.57 | 36.05 |  |
| inland_pct | 1.25 | 3.30 | 8.56 | 304-500: 1.25 |
| lake_pct | 0.12 | 0.29 | 0.73 | 300-300: 0.12; 336-336: 0.20; 360-380: 0.12; 400-416: 0.16; +1 more |
| lake_max_mkm2 | 0.01 | 0.05 | 0.29 |  |
| max_elev_km | 2.46 | 3.64 | 7.44 |  |
| trees_pct | 21.41 | 35.07 | 54.76 | 332-348: 54.76 |
| npp | 292.60 | 373.60 | 411.80 |  |
| landmasses | 5.00 | 9.00 | 13.00 |  |
| largest_pct | 8.30 | 19.90 | 24.70 |  |

### Seed 42, L6 (run a5d12f)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.04 | 32.50 | 33.85 |  |
| cont_pct | 37.42 | 40.59 | 41.28 |  |
| cont_km | 32.80 | 33.59 | 36.33 |  |
| plates | 11.00 | 13.00 | 16.00 |  |
| ocean_age | 46.10 | 49.30 | 57.70 |  |
| speed | 4.11 | 4.48 | 5.25 |  |
| sea_level | -365.00 | -5.20 | 107.40 | 440-500: -365.00 |
| sea_ice_m | -435.50 | -148.00 | -1.00 | 416-500: -435.50 |
| sea_tect_m | 49.20 | 106.60 | 143.70 |  |
| ice_pct | 0.10 | 4.90 | 11.20 | 444-500: 11.20 |
| temp | 7.80 | 13.40 | 21.60 | 452-452: 7.80 |
| co2 | -0.12 | 0.21 | 0.68 |  |
| dry_pct | 15.06 | 20.79 | 52.59 | 300-320: 52.59 |
| inland_pct | 0.32 | 4.17 | 24.11 | 336-360: 3.10; 376-384: 2.76; 408-408: 3.65; 420-500: 0.32 |
| lake_pct | 0.15 | 0.61 | 6.39 | 364-416: 6.39; 436-436: 3.54; 472-472: 0.17; 492-500: 0.15 |
| lake_max_mkm2 | 0.03 | 0.21 | 10.10 | 364-416: 10.10; 436-436: 4.77 |
| max_elev_km | 3.74 | 4.27 | 7.75 |  |
| trees_pct | 20.99 | 34.71 | 43.38 |  |
| npp | 109.40 | 374.10 | 461.90 | 300-344: 109.40 |
| landmasses | 3.00 | 7.00 | 14.00 |  |
| largest_pct | 12.60 | 17.40 | 33.70 |  |

### Seed 77, L6 (run f8ed4c)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.26 | 33.15 | 33.64 |  |
| cont_pct | 38.76 | 39.77 | 40.28 |  |
| cont_km | 33.65 | 34.12 | 34.64 |  |
| plates | 13.00 | 15.00 | 18.00 |  |
| ocean_age | 36.90 | 47.40 | 67.00 |  |
| speed | 3.31 | 4.58 | 5.54 |  |
| sea_level | -63.50 | 144.10 | 221.70 |  |
| sea_ice_m | -37.80 | -11.00 | -0.00 |  |
| sea_tect_m | -27.70 | 157.20 | 224.40 |  |
| ice_pct | 0.00 | 0.70 | 1.40 |  |
| temp | 11.70 | 17.80 | 21.20 |  |
| co2 | -0.19 | 0.49 | 1.26 |  |
| dry_pct | 13.67 | 21.04 | 37.70 |  |
| inland_pct | 2.68 | 5.73 | 11.05 | 308-500: 2.68 |
| lake_pct | 0.26 | 0.49 | 1.38 |  |
| lake_max_mkm2 | 0.04 | 0.12 | 0.66 |  |
| max_elev_km | 2.67 | 4.42 | 7.48 |  |
| trees_pct | 26.02 | 38.33 | 45.98 |  |
| npp | 221.70 | 316.10 | 389.00 |  |
| landmasses | 3.00 | 7.00 | 11.00 |  |
| largest_pct | 12.90 | 18.50 | 33.50 |  |

### Seed 505, L6 (run 05c659)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.64 | 34.01 | 35.01 |  |
| cont_pct | 38.51 | 39.81 | 41.47 |  |
| cont_km | 33.01 | 34.13 | 35.35 |  |
| plates | 8.00 | 11.00 | 15.00 |  |
| ocean_age | 47.40 | 54.30 | 65.80 |  |
| speed | 2.67 | 4.63 | 5.68 |  |
| sea_level | -47.50 | 76.30 | 110.20 |  |
| sea_ice_m | -21.70 | -5.00 | -0.00 |  |
| sea_tect_m | -40.60 | 80.60 | 113.50 |  |
| ice_pct | 0.00 | 0.50 | 1.90 |  |
| temp | 11.80 | 15.70 | 18.80 |  |
| co2 | -0.90 | -0.28 | 0.76 |  |
| dry_pct | 22.64 | 27.21 | 34.38 |  |
| inland_pct | 1.51 | 5.12 | 10.78 | 300-452: 1.51; 476-500: 3.53 |
| lake_pct | 0.16 | 0.32 | 2.16 | 304-304: 0.17; 340-340: 0.17; 368-380: 0.17; 392-408: 0.16 |
| lake_max_mkm2 | 0.03 | 0.07 | 2.99 | 344-344: 2.99 |
| max_elev_km | 3.78 | 6.97 | 8.46 |  |
| trees_pct | 3.53 | 18.50 | 44.05 | 448-476: 3.53 |
| npp | 161.50 | 326.20 | 389.60 | 328-364: 161.50 |
| landmasses | 4.00 | 8.00 | 13.00 |  |
| largest_pct | 12.20 | 22.50 | 34.80 |  |

### Seed 101, L6 (run 6bb00d)

![seed 101 L6](seed101_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.54 | 33.31 | 34.33 |  |
| cont_pct | 37.94 | 39.87 | 41.10 |  |
| cont_km | 33.32 | 34.30 | 35.85 |  |
| plates | 7.00 | 11.00 | 13.00 |  |
| ocean_age | 36.20 | 51.10 | 66.20 |  |
| speed | 3.22 | 4.34 | 5.40 |  |
| sea_level | -74.50 | 98.60 | 230.10 |  |
| sea_ice_m | -49.70 | -1.00 | -0.00 |  |
| sea_tect_m | -70.30 | 112.10 | 230.20 |  |
| ice_pct | 0.00 | 0.10 | 2.60 |  |
| temp | 12.90 | 17.70 | 22.50 |  |
| co2 | -0.96 | -0.24 | 0.39 |  |
| dry_pct | 18.10 | 30.83 | 35.50 |  |
| inland_pct | 0.15 | 4.11 | 10.97 | 300-388: 2.12; 400-500: 0.15 |
| lake_pct | 0.16 | 0.32 | 0.78 | 396-396: 0.17; 416-424: 0.16; 440-440: 0.19 |
| lake_max_mkm2 | 0.03 | 0.06 | 0.76 |  |
| max_elev_km | 4.02 | 5.38 | 8.52 |  |
| trees_pct | 3.10 | 18.70 | 32.81 | 420-456: 3.10; 496-500: 6.35 |
| npp | 175.40 | 286.50 | 377.00 | 352-356: 193.30; 372-372: 196.50; 384-384: 175.40 |
| landmasses | 3.00 | 7.00 | 12.00 |  |
| largest_pct | 22.60 | 26.40 | 32.70 |  |

### Seed 102, L6 (run 54ea2f)

![seed 102 L6](seed102_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.45 | 31.34 | 32.17 |  |
| cont_pct | 38.18 | 40.26 | 41.34 |  |
| cont_km | 33.03 | 33.85 | 35.30 |  |
| plates | 10.00 | 14.00 | 17.00 |  |
| ocean_age | 49.00 | 51.10 | 61.30 |  |
| speed | 3.15 | 4.13 | 4.52 |  |
| sea_level | -126.90 | -10.00 | 144.30 |  |
| sea_ice_m | -166.40 | -132.10 | -22.10 |  |
| sea_tect_m | 25.50 | 117.90 | 166.40 |  |
| ice_pct | 2.00 | 5.10 | 6.20 |  |
| temp | 11.50 | 13.10 | 16.60 |  |
| co2 | -0.57 | -0.05 | 0.41 |  |
| dry_pct | 15.90 | 21.06 | 24.58 |  |
| inland_pct | 1.11 | 3.32 | 13.88 | 300-416: 1.11; 428-444: 6.02; 456-500: 1.29 |
| lake_pct | 0.27 | 0.53 | 4.71 | 420-424: 4.71 |
| lake_max_mkm2 | 0.04 | 0.11 | 6.60 | 420-424: 6.60 |
| max_elev_km | 4.10 | 5.22 | 7.54 |  |
| trees_pct | 21.91 | 30.36 | 54.80 | 360-368: 54.80 |
| npp | 209.20 | 366.35 | 469.00 |  |
| landmasses | 9.00 | 12.00 | 18.00 |  |
| largest_pct | 9.60 | 19.00 | 30.50 |  |

### Seed 103, L6 (run 1b84d1)

![seed 103 L6](seed103_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.43 | 31.94 | 33.33 |  |
| cont_pct | 40.24 | 42.37 | 42.86 |  |
| cont_km | 31.15 | 31.86 | 33.92 |  |
| plates | 10.00 | 13.00 | 15.00 |  |
| ocean_age | 40.90 | 57.60 | 70.20 |  |
| speed | 2.78 | 4.06 | 4.69 |  |
| sea_level | -61.90 | 5.30 | 90.40 |  |
| sea_ice_m | -159.20 | -30.50 | -3.80 |  |
| sea_tect_m | -52.00 | 53.30 | 207.20 |  |
| ice_pct | 0.30 | 1.50 | 5.30 |  |
| temp | 7.60 | 13.60 | 18.70 | 300-304: 7.60 |
| co2 | -1.19 | -0.55 | 0.45 |  |
| dry_pct | 17.83 | 26.59 | 30.70 |  |
| inland_pct | 0.67 | 2.25 | 8.40 | 300-500: 0.67 |
| lake_pct | 0.14 | 0.28 | 1.15 | 392-392: 0.19; 412-428: 0.17; 440-440: 0.14; 464-464: 0.18 |
| lake_max_mkm2 | 0.03 | 0.05 | 1.20 | 368-376: 1.20 |
| max_elev_km | 2.90 | 3.89 | 5.85 |  |
| trees_pct | 1.33 | 18.21 | 51.68 | 328-328: 51.68; 348-356: 6.74; 392-460: 1.33 |
| npp | 124.40 | 275.80 | 415.50 | 344-356: 152.00; 392-400: 124.40 |
| landmasses | 3.00 | 11.00 | 15.00 |  |
| largest_pct | 13.30 | 19.40 | 28.80 |  |

### Seed 104, L6 (run e8c3a5)

![seed 104 L6](seed104_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.28 | 34.72 | 35.16 |  |
| cont_pct | 39.15 | 40.17 | 41.42 |  |
| cont_km | 32.91 | 33.71 | 34.68 |  |
| plates | 7.00 | 10.00 | 13.00 |  |
| ocean_age | 43.90 | 56.80 | 65.30 |  |
| speed | 2.91 | 4.52 | 5.43 |  |
| sea_level | -50.40 | 36.40 | 174.90 |  |
| sea_ice_m | -26.20 | -7.20 | -0.40 |  |
| sea_tect_m | -35.80 | 58.30 | 175.50 |  |
| ice_pct | 0.00 | 0.50 | 1.80 |  |
| temp | 12.90 | 15.90 | 21.50 |  |
| co2 | -0.52 | 0.16 | 1.31 |  |
| dry_pct | 14.97 | 29.21 | 36.89 |  |
| inland_pct | 0.68 | 3.56 | 7.20 | 300-500: 0.68 |
| lake_pct | 0.12 | 0.30 | 1.11 | 300-344: 0.13; 372-376: 0.12; 392-404: 0.13; 424-424: 0.13 |
| lake_max_mkm2 | 0.01 | 0.07 | 0.72 |  |
| max_elev_km | 3.41 | 4.80 | 8.39 |  |
| trees_pct | 11.91 | 29.96 | 45.48 |  |
| npp | 112.70 | 306.95 | 403.40 | 312-332: 112.70; 404-404: 187.70 |
| landmasses | 2.00 | 4.00 | 7.00 | 452-452: 2 |
| largest_pct | 12.50 | 22.80 | 31.40 |  |

### Seed 105, L6 (run 3d42ce)

![seed 105 L6](seed105_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.43 | 32.61 | 33.30 |  |
| cont_pct | 39.51 | 41.04 | 42.68 |  |
| cont_km | 31.67 | 32.89 | 34.05 |  |
| plates | 10.00 | 13.00 | 14.00 |  |
| ocean_age | 49.10 | 59.80 | 81.90 |  |
| speed | 2.89 | 4.02 | 4.64 |  |
| sea_level | -524.90 | 82.70 | 127.40 | 456-500: -524.90 |
| sea_ice_m | -415.80 | -7.20 | -3.20 | 456-500: -415.80 |
| sea_tect_m | -124.70 | 86.90 | 131.30 |  |
| ice_pct | 0.20 | 0.50 | 12.70 | 456-488: 12.70 |
| temp | 8.30 | 15.50 | 18.40 |  |
| co2 | -1.28 | 0.21 | 0.77 |  |
| dry_pct | 12.53 | 17.88 | 31.16 |  |
| inland_pct | 0.58 | 2.43 | 7.09 | 300-500: 0.58 |
| lake_pct | 0.24 | 0.42 | 0.94 |  |
| lake_max_mkm2 | 0.03 | 0.07 | 0.34 |  |
| max_elev_km | 3.59 | 5.04 | 8.09 |  |
| trees_pct | 8.12 | 42.69 | 55.36 | 340-352: 55.36; 452-460: 8.12 |
| npp | 211.20 | 315.25 | 495.50 |  |
| landmasses | 4.00 | 10.00 | 16.00 |  |
| largest_pct | 11.20 | 20.50 | 32.90 |  |

### Seed 106, L6 (run c491e9)

![seed 106 L6](seed106_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.41 | 32.68 | 33.38 |  |
| cont_pct | 38.86 | 40.72 | 42.34 |  |
| cont_km | 32.37 | 33.36 | 34.79 |  |
| plates | 7.00 | 15.00 | 18.00 |  |
| ocean_age | 38.40 | 45.50 | 71.80 |  |
| speed | 1.76 | 4.44 | 5.22 | 468-472: 1.76 |
| sea_level | -416.80 | 158.80 | 220.00 | 484-500: -416.80 |
| sea_ice_m | -376.90 | -22.60 | -1.50 | 472-500: -376.90 |
| sea_tect_m | -39.90 | 173.90 | 233.00 |  |
| ice_pct | 0.10 | 1.80 | 12.30 | 472-500: 12.30 |
| temp | 7.40 | 15.30 | 20.60 | 492-496: 7.40 |
| co2 | -0.84 | 0.14 | 0.74 |  |
| dry_pct | 16.36 | 19.97 | 36.69 |  |
| inland_pct | 0.76 | 3.40 | 15.98 | 300-456: 0.76; 472-500: 1.15 |
| lake_pct | 0.14 | 0.34 | 2.42 | 352-372: 0.14; 384-388: 0.16 |
| lake_max_mkm2 | 0.03 | 0.06 | 2.99 | 448-448: 2.58; 460-468: 2.99 |
| max_elev_km | 3.73 | 5.57 | 8.50 |  |
| trees_pct | 15.41 | 28.33 | 36.55 |  |
| npp | 236.90 | 322.10 | 402.70 |  |
| landmasses | 6.00 | 11.00 | 17.00 |  |
| largest_pct | 8.30 | 13.10 | 32.70 |  |

### Seed 107, L6 (run 41bd87)

![seed 107 L6](seed107_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.84 | 32.59 | 33.31 |  |
| cont_pct | 38.85 | 39.88 | 40.64 |  |
| cont_km | 33.66 | 34.10 | 34.97 |  |
| plates | 7.00 | 12.00 | 15.00 |  |
| ocean_age | 37.80 | 57.00 | 67.00 |  |
| speed | 2.65 | 4.32 | 5.14 |  |
| sea_level | -278.50 | 69.60 | 226.80 | 476-492: -278.50 |
| sea_ice_m | -218.10 | -26.00 | -2.10 |  |
| sea_tect_m | -64.00 | 88.90 | 229.40 |  |
| ice_pct | 0.20 | 1.60 | 7.60 |  |
| temp | 9.70 | 12.30 | 16.60 |  |
| co2 | -0.77 | -0.21 | 0.49 |  |
| dry_pct | 13.76 | 25.83 | 32.27 |  |
| inland_pct | 0.83 | 4.53 | 11.43 | 300-308: 4.66; 328-500: 0.83 |
| lake_pct | 0.28 | 0.77 | 3.77 | 456-468: 3.77 |
| lake_max_mkm2 | 0.04 | 0.32 | 3.83 | 388-388: 1.07; 400-400: 1.26; 416-416: 1.81; 428-432: 3.52; +1 more |
| max_elev_km | 4.75 | 6.89 | 8.32 |  |
| trees_pct | 13.86 | 22.76 | 35.63 |  |
| npp | 189.70 | 280.50 | 452.70 | 300-300: 189.70 |
| landmasses | 4.00 | 7.00 | 13.00 |  |
| largest_pct | 16.40 | 21.20 | 28.50 |  |

### Seed 108, L6 (run 2306db)

![seed 108 L6](seed108_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.52 | 31.60 | 33.85 |  |
| cont_pct | 38.75 | 39.94 | 40.74 |  |
| cont_km | 33.87 | 34.11 | 35.21 |  |
| plates | 15.00 | 17.00 | 19.00 |  |
| ocean_age | 40.00 | 46.40 | 62.50 |  |
| speed | 3.39 | 3.83 | 5.02 |  |
| sea_level | -26.40 | 55.20 | 193.00 |  |
| sea_ice_m | -164.90 | -111.00 | -17.80 |  |
| sea_tect_m | 22.30 | 194.80 | 229.70 |  |
| ice_pct | 1.50 | 5.00 | 7.00 |  |
| temp | 9.40 | 12.20 | 15.50 |  |
| co2 | -1.20 | 0.04 | 0.61 |  |
| dry_pct | 17.49 | 22.16 | 29.11 |  |
| inland_pct | 1.15 | 4.17 | 14.03 | 300-500: 1.15 |
| lake_pct | 0.33 | 0.74 | 2.13 |  |
| lake_max_mkm2 | 0.03 | 0.27 | 1.99 | 344-344: 1.66; 356-356: 1.92; 376-376: 1.32; 388-392: 1.40; +2 more |
| max_elev_km | 4.06 | 5.41 | 8.09 |  |
| trees_pct | 4.76 | 32.54 | 51.86 | 328-352: 51.86; 464-464: 9.10; 476-496: 4.76 |
| npp | 242.40 | 338.25 | 439.60 |  |
| landmasses | 4.00 | 8.00 | 12.00 |  |
| largest_pct | 8.30 | 14.60 | 30.80 |  |

### Seed 201, L6 (run e38080)

![seed 201 L6](seed201_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.03 | 32.09 | 34.19 |  |
| cont_pct | 37.84 | 40.62 | 41.71 |  |
| cont_km | 32.63 | 33.77 | 35.77 |  |
| plates | 8.00 | 12.00 | 16.00 |  |
| ocean_age | 39.30 | 59.20 | 75.50 |  |
| speed | 3.26 | 4.54 | 5.84 |  |
| sea_level | -253.20 | -22.60 | 204.40 | 500-500: -253.20 |
| sea_ice_m | -151.80 | -47.70 | -12.00 |  |
| sea_tect_m | -101.40 | 40.30 | 221.40 |  |
| ice_pct | 1.00 | 2.40 | 6.70 |  |
| temp | 10.70 | 15.60 | 19.20 |  |
| co2 | -1.10 | 0.36 | 1.95 |  |
| dry_pct | 17.10 | 20.22 | 28.96 |  |
| inland_pct | 1.99 | 6.87 | 12.10 | 300-344: 1.99; 356-396: 2.39; 420-460: 3.81; 476-500: 4.63 |
| lake_pct | 0.58 | 1.06 | 3.11 | 440-440: 3.11 |
| lake_max_mkm2 | 0.06 | 0.44 | 2.48 | 384-384: 1.01; 400-416: 1.96; 428-428: 1.27; 440-444: 2.48; +1 more |
| max_elev_km | 4.04 | 5.71 | 7.95 |  |
| trees_pct | 2.53 | 37.16 | 49.75 | 456-472: 2.53 |
| npp | 216.30 | 356.05 | 432.00 |  |
| landmasses | 3.00 | 10.00 | 16.00 |  |
| largest_pct | 8.40 | 17.40 | 33.60 |  |

### Seed 202, L6 (run 5dc5d0)

![seed 202 L6](seed202_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.95 | 33.22 | 34.42 |  |
| cont_pct | 39.74 | 40.20 | 41.66 |  |
| cont_km | 32.45 | 33.34 | 34.25 |  |
| plates | 10.00 | 12.00 | 16.00 |  |
| ocean_age | 46.20 | 50.90 | 74.10 |  |
| speed | 2.40 | 4.38 | 4.90 |  |
| sea_level | -194.80 | 106.10 | 145.90 |  |
| sea_ice_m | -159.90 | -15.70 | -11.40 |  |
| sea_tect_m | -61.10 | 119.50 | 157.70 |  |
| ice_pct | 0.90 | 1.30 | 5.30 |  |
| temp | 11.00 | 15.80 | 19.30 |  |
| co2 | -1.62 | -0.05 | 0.60 |  |
| dry_pct | 16.94 | 21.73 | 26.93 |  |
| inland_pct | 0.41 | 2.42 | 5.43 | 300-500: 0.41 |
| lake_pct | 0.19 | 0.40 | 1.23 | 420-420: 0.19 |
| lake_max_mkm2 | 0.03 | 0.10 | 0.88 |  |
| max_elev_km | 4.17 | 5.13 | 6.85 |  |
| trees_pct | 2.25 | 30.84 | 40.93 | 440-500: 2.25 |
| npp | 203.90 | 289.50 | 392.10 |  |
| landmasses | 5.00 | 8.00 | 16.00 |  |
| largest_pct | 9.10 | 17.80 | 24.20 |  |

### Seed 203, L6 (run 3bca03)

![seed 203 L6](seed203_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.01 | 34.06 | 34.58 |  |
| cont_pct | 38.13 | 39.56 | 40.41 |  |
| cont_km | 33.99 | 34.68 | 35.40 |  |
| plates | 9.00 | 12.00 | 13.00 |  |
| ocean_age | 39.60 | 49.70 | 72.00 |  |
| speed | 3.52 | 4.71 | 6.04 |  |
| sea_level | -114.10 | 102.00 | 193.30 |  |
| sea_ice_m | -30.00 | -14.50 | -1.10 |  |
| sea_tect_m | -88.20 | 111.70 | 207.40 |  |
| ice_pct | 0.10 | 1.20 | 2.00 |  |
| temp | 10.00 | 14.10 | 19.10 |  |
| co2 | -0.90 | -0.30 | 0.47 |  |
| dry_pct | 28.04 | 34.78 | 40.58 |  |
| inland_pct | 1.59 | 6.45 | 27.44 | 324-496: 1.59 |
| lake_pct | 0.18 | 0.33 | 1.76 | 372-372: 0.18; 432-432: 0.19 |
| lake_max_mkm2 | 0.03 | 0.07 | 2.79 | 368-368: 1.81; 436-444: 2.79 |
| max_elev_km | 4.00 | 5.31 | 8.21 |  |
| trees_pct | 4.14 | 12.16 | 35.80 | 368-372: 8.04; 428-456: 4.14 |
| npp | 148.70 | 254.20 | 383.00 | 304-308: 173.20; 352-384: 148.70 |
| landmasses | 2.00 | 4.00 | 8.00 | 328-332: 2; 476-484: 2 |
| largest_pct | 15.90 | 31.20 | 34.50 |  |

### Seed 204, L6 (run 13a3fc)

![seed 204 L6](seed204_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.50 | 32.58 | 34.21 |  |
| cont_pct | 39.31 | 40.67 | 41.15 |  |
| cont_km | 32.39 | 33.03 | 34.83 |  |
| plates | 5.00 | 8.00 | 12.00 |  |
| ocean_age | 48.10 | 59.40 | 73.30 |  |
| speed | 3.15 | 4.25 | 4.71 |  |
| sea_level | -310.70 | -87.30 | 73.50 | 432-444: -310.70 |
| sea_ice_m | -258.50 | -28.60 | -8.30 | 436-436: -258.50 |
| sea_tect_m | -121.90 | -26.80 | 83.60 |  |
| ice_pct | 0.60 | 2.20 | 8.60 |  |
| temp | 9.70 | 15.40 | 20.80 |  |
| co2 | -1.14 | -0.15 | 1.22 |  |
| dry_pct | 10.74 | 27.11 | 38.52 | 412-424: 10.74 |
| inland_pct | 0.80 | 3.12 | 17.18 | 300-328: 2.88; 376-500: 0.80 |
| lake_pct | 0.17 | 0.40 | 1.83 | 352-352: 0.19; 376-380: 0.17 |
| lake_max_mkm2 | 0.03 | 0.07 | 1.43 | 452-452: 1.43 |
| max_elev_km | 5.04 | 5.86 | 8.34 |  |
| trees_pct | 3.27 | 22.86 | 42.78 | 384-392: 4.12; 408-416: 4.28; 452-464: 3.27 |
| npp | 102.60 | 298.30 | 470.40 | 380-396: 102.60 |
| landmasses | 2.00 | 6.00 | 10.00 | 464-464: 2 |
| largest_pct | 12.20 | 15.80 | 31.90 |  |

### Seed 205, L6 (run ce4649)

![seed 205 L6](seed205_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.10 | 33.87 | 35.09 |  |
| cont_pct | 38.67 | 40.44 | 41.59 |  |
| cont_km | 32.88 | 33.77 | 35.23 |  |
| plates | 9.00 | 12.00 | 15.00 |  |
| ocean_age | 39.30 | 52.00 | 62.50 |  |
| speed | 3.32 | 4.57 | 5.52 |  |
| sea_level | -15.60 | 106.70 | 192.00 |  |
| sea_ice_m | -38.40 | -5.90 | -0.00 |  |
| sea_tect_m | 9.90 | 117.50 | 193.10 |  |
| ice_pct | 0.00 | 0.50 | 1.90 |  |
| temp | 10.90 | 17.40 | 21.70 |  |
| co2 | -0.27 | 0.31 | 0.88 |  |
| dry_pct | 17.23 | 22.02 | 33.67 |  |
| inland_pct | 1.22 | 4.02 | 11.39 | 300-500: 1.22 |
| lake_pct | 0.21 | 0.52 | 4.31 | 420-420: 4.31 |
| lake_max_mkm2 | 0.03 | 0.14 | 6.29 | 420-420: 6.29; 436-436: 1.17; 460-460: 4.28 |
| max_elev_km | 3.13 | 4.23 | 7.14 |  |
| trees_pct | 17.43 | 37.07 | 45.09 |  |
| npp | 264.50 | 345.15 | 390.10 |  |
| landmasses | 2.00 | 7.00 | 12.00 | 300-300: 2; 484-500: 2 |
| largest_pct | 10.00 | 20.60 | 31.80 |  |

### Seed 206, L6 (run 6ed4ea)

![seed 206 L6](seed206_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.66 | 33.26 | 34.25 |  |
| cont_pct | 39.05 | 40.64 | 41.36 |  |
| cont_km | 32.97 | 33.57 | 34.90 |  |
| plates | 5.00 | 8.00 | 12.00 |  |
| ocean_age | 46.20 | 53.20 | 79.80 |  |
| speed | 2.66 | 4.41 | 5.26 |  |
| sea_level | -373.50 | 35.50 | 107.40 | 300-324: -373.50 |
| sea_ice_m | -196.40 | -5.80 | -1.50 |  |
| sea_tect_m | -182.60 | 39.60 | 112.20 |  |
| ice_pct | 0.10 | 0.50 | 6.50 |  |
| temp | 11.00 | 17.80 | 22.40 |  |
| co2 | -1.31 | 0.22 | 1.01 |  |
| dry_pct | 14.76 | 22.11 | 25.95 |  |
| inland_pct | 0.84 | 2.99 | 10.82 | 300-432: 1.51; 460-500: 0.84 |
| lake_pct | 0.18 | 0.36 | 5.54 | 436-456: 5.54; 468-468: 0.18 |
| lake_max_mkm2 | 0.03 | 0.07 | 8.99 | 316-316: 2.63; 376-376: 1.37; 436-456: 8.99 |
| max_elev_km | 4.29 | 6.16 | 8.79 |  |
| trees_pct | 1.76 | 36.78 | 50.66 | 324-328: 50.66; 440-500: 1.76 |
| npp | 211.20 | 297.60 | 375.10 |  |
| landmasses | 3.00 | 7.00 | 11.00 |  |
| largest_pct | 15.60 | 25.40 | 33.00 |  |

### Seed 207, L6 (run 264f96)

![seed 207 L6](seed207_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.18 | 33.34 | 33.64 |  |
| cont_pct | 37.35 | 39.56 | 40.62 |  |
| cont_km | 33.76 | 34.44 | 36.44 |  |
| plates | 9.00 | 12.00 | 17.00 |  |
| ocean_age | 44.10 | 59.80 | 80.90 |  |
| speed | 2.97 | 3.96 | 5.21 |  |
| sea_level | -409.90 | 41.60 | 144.50 | 452-500: -409.90 |
| sea_ice_m | -281.50 | -34.70 | -14.20 | 460-500: -281.50 |
| sea_tect_m | -133.80 | 60.90 | 164.20 |  |
| ice_pct | 1.30 | 2.40 | 7.70 |  |
| temp | 10.90 | 16.00 | 18.70 |  |
| co2 | -1.59 | 0.41 | 1.42 |  |
| dry_pct | 14.85 | 20.11 | 34.29 |  |
| inland_pct | 1.11 | 3.26 | 17.54 | 320-320: 7.99; 336-500: 1.11 |
| lake_pct | 0.12 | 0.53 | 1.58 | 392-392: 0.17; 456-456: 0.16; 484-500: 0.12 |
| lake_max_mkm2 | 0.03 | 0.11 | 1.27 | 312-312: 1.06; 324-324: 1.27; 340-340: 1.11 |
| max_elev_km | 4.92 | 5.63 | 7.67 |  |
| trees_pct | 1.66 | 34.59 | 43.17 | 420-452: 1.66 |
| npp | 97.90 | 286.60 | 426.70 | 400-428: 97.90 |
| landmasses | 6.00 | 10.00 | 17.00 |  |
| largest_pct | 14.10 | 19.60 | 33.40 |  |

### Seed 208, L6 (run bd5556)

![seed 208 L6](seed208_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.06 | 32.59 | 33.99 |  |
| cont_pct | 39.16 | 40.71 | 41.87 |  |
| cont_km | 32.68 | 33.21 | 34.41 |  |
| plates | 11.00 | 15.00 | 18.00 |  |
| ocean_age | 42.80 | 47.80 | 64.10 |  |
| speed | 3.07 | 4.15 | 4.74 |  |
| sea_level | 20.50 | 136.50 | 196.20 |  |
| sea_ice_m | -22.30 | -7.50 | -1.80 |  |
| sea_tect_m | 38.30 | 147.40 | 204.00 |  |
| ice_pct | 0.10 | 0.60 | 1.90 |  |
| temp | 16.60 | 20.30 | 23.60 |  |
| co2 | 0.01 | 0.44 | 1.17 |  |
| dry_pct | 12.22 | 18.11 | 31.81 |  |
| inland_pct | 0.46 | 2.36 | 6.36 | 300-500: 0.46 |
| lake_pct | 0.21 | 0.45 | 1.28 |  |
| lake_max_mkm2 | 0.03 | 0.17 | 1.48 | 444-448: 1.48; 492-492: 1.02 |
| max_elev_km | 3.60 | 5.21 | 7.30 |  |
| trees_pct | 28.72 | 35.08 | 48.17 |  |
| npp | 187.40 | 380.55 | 409.20 | 344-344: 187.40 |
| landmasses | 5.00 | 8.00 | 12.00 |  |
| largest_pct | 12.00 | 12.80 | 21.70 |  |

### Seed 209, L6 (run 24926e)

![seed 209 L6](seed209_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.82 | 32.75 | 33.38 |  |
| cont_pct | 39.13 | 40.72 | 41.14 |  |
| cont_km | 33.23 | 33.59 | 34.44 |  |
| plates | 9.00 | 12.00 | 15.00 |  |
| ocean_age | 51.10 | 53.00 | 71.60 |  |
| speed | 3.15 | 4.13 | 5.24 |  |
| sea_level | -93.30 | 72.00 | 129.50 |  |
| sea_ice_m | -56.90 | -10.50 | -3.80 |  |
| sea_tect_m | -45.10 | 86.50 | 133.70 |  |
| ice_pct | 0.30 | 0.80 | 3.50 |  |
| temp | 13.10 | 17.90 | 22.00 |  |
| co2 | -1.13 | -0.27 | 0.54 |  |
| dry_pct | 21.23 | 25.87 | 30.70 |  |
| inland_pct | 1.64 | 4.18 | 9.56 | 300-412: 1.64; 424-500: 2.05 |
| lake_pct | 0.22 | 0.34 | 2.28 |  |
| lake_max_mkm2 | 0.03 | 0.07 | 3.14 | 416-420: 3.14 |
| max_elev_km | 4.31 | 6.26 | 8.79 |  |
| trees_pct | 0.70 | 16.79 | 53.25 | 308-320: 53.25; 432-452: 2.26; 468-484: 0.70; 496-500: 5.25 |
| npp | 155.20 | 241.10 | 364.00 | 340-348: 182.30; 368-392: 155.20 |
| landmasses | 4.00 | 7.00 | 12.00 |  |
| largest_pct | 14.60 | 19.50 | 26.40 |  |

### Seed 210, L6 (run 1a1b8b)

![seed 210 L6](seed210_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.50 | 34.91 | 36.17 |  |
| cont_pct | 39.18 | 40.29 | 41.56 |  |
| cont_km | 33.31 | 34.31 | 34.95 |  |
| plates | 6.00 | 10.00 | 12.00 |  |
| ocean_age | 46.30 | 59.90 | 90.10 |  |
| speed | 2.18 | 3.77 | 5.60 |  |
| sea_level | -248.40 | -4.90 | 85.20 |  |
| sea_ice_m | -56.00 | -15.20 | -6.60 |  |
| sea_tect_m | -225.30 | 2.20 | 100.90 |  |
| ice_pct | 0.50 | 1.10 | 2.80 |  |
| temp | 11.80 | 17.90 | 22.00 |  |
| co2 | -0.55 | 0.25 | 0.83 |  |
| dry_pct | 17.70 | 25.65 | 36.63 |  |
| inland_pct | 1.19 | 4.95 | 13.11 | 300-304: 3.50; 316-372: 4.95; 384-500: 1.19 |
| lake_pct | 0.17 | 0.45 | 2.22 | 312-324: 0.17 |
| lake_max_mkm2 | 0.03 | 0.09 | 3.31 | 352-356: 1.36; 416-420: 3.31 |
| max_elev_km | 4.57 | 5.71 | 7.88 |  |
| trees_pct | 16.59 | 28.62 | 37.12 |  |
| npp | 286.80 | 337.50 | 381.90 |  |
| landmasses | 2.00 | 7.00 | 9.00 | 304-304: 2 |
| largest_pct | 14.50 | 20.30 | 34.40 |  |

### Seed 211, L6 (run 0156d2)

![seed 211 L6](seed211_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.71 | 32.39 | 33.63 |  |
| cont_pct | 39.09 | 40.32 | 41.44 |  |
| cont_km | 32.42 | 32.93 | 33.82 |  |
| plates | 11.00 | 14.00 | 15.00 |  |
| ocean_age | 46.60 | 53.40 | 61.10 |  |
| speed | 2.90 | 4.53 | 5.23 |  |
| sea_level | 5.40 | 93.70 | 146.80 |  |
| sea_ice_m | -20.10 | -5.10 | -0.00 |  |
| sea_tect_m | 23.40 | 95.90 | 147.40 |  |
| ice_pct | 0.00 | 0.30 | 1.50 |  |
| temp | 13.90 | 18.40 | 21.90 |  |
| co2 | -1.43 | -0.14 | 1.00 |  |
| dry_pct | 15.63 | 21.52 | 26.85 |  |
| inland_pct | 0.79 | 2.36 | 6.15 | 300-500: 0.79 |
| lake_pct | 0.08 | 0.31 | 1.87 | 372-372: 0.17; 388-400: 0.12; 412-420: 0.08 |
| lake_max_mkm2 | 0.01 | 0.06 | 2.08 | 376-376: 1.87; 456-460: 2.08 |
| max_elev_km | 3.66 | 5.11 | 8.34 |  |
| trees_pct | 2.17 | 19.38 | 47.57 | 468-500: 2.17 |
| npp | 174.80 | 264.30 | 360.90 | 328-332: 174.80 |
| landmasses | 5.00 | 8.00 | 13.00 |  |
| largest_pct | 7.00 | 13.10 | 23.30 |  |

### Seed 212, L6 (run 477df0)

![seed 212 L6](seed212_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.06 | 32.04 | 33.90 |  |
| cont_pct | 38.42 | 38.89 | 39.37 |  |
| cont_km | 33.85 | 34.61 | 35.23 |  |
| plates | 9.00 | 13.00 | 16.00 |  |
| ocean_age | 42.00 | 55.30 | 69.70 |  |
| speed | 2.63 | 4.17 | 5.25 |  |
| sea_level | -77.90 | 67.20 | 188.80 |  |
| sea_ice_m | -75.70 | -24.10 | -11.20 |  |
| sea_tect_m | -44.30 | 121.40 | 203.20 |  |
| ice_pct | 0.80 | 2.60 | 4.40 |  |
| temp | 11.00 | 14.50 | 20.30 |  |
| co2 | -0.71 | 0.32 | 1.46 |  |
| dry_pct | 7.93 | 14.50 | 29.65 | 448-500: 7.93 |
| inland_pct | 0.44 | 2.95 | 12.08 | 304-312: 6.87; 324-500: 0.44 |
| lake_pct | 0.30 | 0.90 | 1.44 |  |
| lake_max_mkm2 | 0.05 | 0.67 | 1.38 | 392-396: 1.10; 420-428: 1.38 |
| max_elev_km | 4.23 | 7.43 | 8.24 |  |
| trees_pct | 18.50 | 33.99 | 44.37 |  |
| npp | 239.70 | 318.20 | 370.20 |  |
| landmasses | 2.00 | 8.00 | 15.00 | 308-332: 2 |
| largest_pct | 10.40 | 18.70 | 26.60 |  |

### Seed 213, L6 (run b7e213)

![seed 213 L6](seed213_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.77 | 34.01 | 34.84 |  |
| cont_pct | 39.20 | 40.36 | 40.96 |  |
| cont_km | 33.41 | 33.86 | 34.81 |  |
| plates | 10.00 | 13.00 | 17.00 |  |
| ocean_age | 39.80 | 49.80 | 56.60 |  |
| speed | 2.99 | 4.34 | 4.93 |  |
| sea_level | -40.00 | 86.30 | 192.70 |  |
| sea_ice_m | -39.70 | -9.40 | -3.10 |  |
| sea_tect_m | -6.10 | 97.40 | 195.80 |  |
| ice_pct | 0.20 | 0.60 | 1.40 |  |
| temp | 13.00 | 16.10 | 21.40 |  |
| co2 | -0.30 | 0.41 | 0.82 |  |
| dry_pct | 15.86 | 19.89 | 35.59 |  |
| inland_pct | 2.67 | 5.44 | 15.13 | 300-316: 5.15; 344-472: 2.67; 484-500: 3.79 |
| lake_pct | 0.32 | 0.60 | 3.38 | 312-312: 3.04; 332-336: 3.38 |
| lake_max_mkm2 | 0.04 | 0.15 | 4.58 | 312-320: 4.25; 332-340: 4.58; 472-496: 1.29 |
| max_elev_km | 3.81 | 5.20 | 6.85 |  |
| trees_pct | 29.36 | 36.77 | 42.56 |  |
| npp | 288.10 | 362.30 | 406.60 |  |
| landmasses | 3.00 | 6.00 | 12.00 |  |
| largest_pct | 21.40 | 30.50 | 35.00 |  |

### Seed 214, L6 (run 16fdb1)

![seed 214 L6](seed214_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 29.83 | 32.30 | 32.98 |  |
| cont_pct | 39.71 | 40.38 | 40.88 |  |
| cont_km | 33.40 | 33.54 | 34.32 |  |
| plates | 7.00 | 11.00 | 15.00 |  |
| ocean_age | 49.00 | 57.10 | 81.30 |  |
| speed | 2.78 | 3.31 | 5.08 |  |
| sea_level | -461.90 | -224.80 | 80.30 | 416-500: -461.90 |
| sea_ice_m | -362.30 | -302.10 | -19.20 | 352-492: -362.30 |
| sea_tect_m | -169.20 | 44.50 | 136.70 |  |
| ice_pct | 2.20 | 10.90 | 13.40 | 352-492: 13.40 |
| temp | 8.60 | 12.70 | 17.10 |  |
| co2 | -0.74 | 0.25 | 1.38 |  |
| dry_pct | 8.93 | 12.42 | 21.73 | 404-500: 8.93 |
| inland_pct | 0.11 | 0.99 | 3.42 | 300-500: 0.11 |
| lake_pct | 0.14 | 0.43 | 1.18 | 384-384: 0.14; 404-404: 0.19 |
| lake_max_mkm2 | 0.03 | 0.16 | 1.08 | 496-496: 1.08 |
| max_elev_km | 4.64 | 6.01 | 7.37 |  |
| trees_pct | 20.43 | 41.40 | 48.68 |  |
| npp | 295.00 | 402.00 | 590.20 |  |
| landmasses | 4.00 | 8.00 | 12.00 |  |
| largest_pct | 9.00 | 13.50 | 18.50 |  |

### Seed 215, L6 (run bc0075)

![seed 215 L6](seed215_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.12 | 33.65 | 34.06 |  |
| cont_pct | 38.64 | 39.62 | 40.49 |  |
| cont_km | 33.74 | 34.40 | 35.32 |  |
| plates | 13.00 | 14.00 | 17.00 |  |
| ocean_age | 35.20 | 42.70 | 51.10 |  |
| speed | 3.32 | 4.52 | 5.15 |  |
| sea_level | 91.80 | 191.50 | 244.10 |  |
| sea_ice_m | -39.20 | -3.00 | -0.00 |  |
| sea_tect_m | 113.10 | 201.30 | 247.90 |  |
| ice_pct | 0.00 | 0.20 | 2.60 |  |
| temp | 8.50 | 15.00 | 18.90 |  |
| co2 | -0.68 | -0.24 | 0.74 |  |
| dry_pct | 17.28 | 30.59 | 41.09 |  |
| inland_pct | 1.12 | 4.60 | 13.38 | 300-320: 3.78; 332-340: 6.73; 356-500: 1.12 |
| lake_pct | 0.12 | 0.25 | 0.82 | 300-300: 0.17; 312-324: 0.12; 336-340: 0.17; 388-396: 0.18; +2 more |
| lake_max_mkm2 | 0.03 | 0.05 | 0.45 |  |
| max_elev_km | 3.78 | 5.18 | 8.15 |  |
| trees_pct | 10.52 | 20.26 | 33.10 |  |
| npp | 131.70 | 323.70 | 410.40 | 332-392: 131.70 |
| landmasses | 3.00 | 6.00 | 12.00 |  |
| largest_pct | 12.60 | 17.10 | 30.10 |  |

### Seed 216, L6 (run 4840ac)

![seed 216 L6](seed216_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.70 | 32.88 | 34.62 |  |
| cont_pct | 38.68 | 39.72 | 40.42 |  |
| cont_km | 33.81 | 34.49 | 35.58 |  |
| plates | 10.00 | 14.00 | 18.00 |  |
| ocean_age | 36.60 | 45.70 | 63.30 |  |
| speed | 3.11 | 4.68 | 5.39 |  |
| sea_level | -80.10 | 123.20 | 224.80 |  |
| sea_ice_m | -103.30 | -23.60 | -11.60 |  |
| sea_tect_m | 1.40 | 158.50 | 237.00 |  |
| ice_pct | 0.80 | 1.80 | 4.90 |  |
| temp | 12.30 | 16.30 | 19.30 |  |
| co2 | 0.00 | 0.72 | 1.27 |  |
| dry_pct | 18.19 | 21.23 | 36.85 |  |
| inland_pct | 2.12 | 6.19 | 17.87 | 312-316: 6.19; 332-348: 2.95; 360-452: 2.12; 464-500: 3.21 |
| lake_pct | 0.27 | 0.68 | 4.12 | 356-356: 3.50; 416-416: 3.17; 428-428: 3.36; 448-448: 3.08; +1 more |
| lake_max_mkm2 | 0.03 | 0.19 | 5.17 | 308-308: 2.19; 356-356: 5.08; 416-428: 4.61; 448-448: 3.74; +1 more |
| max_elev_km | 4.29 | 5.22 | 6.80 |  |
| trees_pct | 30.48 | 38.41 | 53.58 | 340-372: 53.58 |
| npp | 311.80 | 364.10 | 404.30 |  |
| landmasses | 6.00 | 10.00 | 15.00 |  |
| largest_pct | 9.00 | 14.10 | 28.30 |  |

## Determinism

(not run)
