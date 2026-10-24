# Health sweep 2026-10-23 19:02

Commit None. 32 runs (default params, `--every 4`) at 6 workers x 3 numba threads; simulations 37.5 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | ice bar new (ice-v2-criteria.md) | icehouse % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 500 | cac49b | 378 | 104 / 316 | 12.1 | 0 | 2.0 | 0.978 | 3.9 | 0.0 | ok | ok | 21.6 |
| 2 | 6 | 500 | 036ccb | 322 | 116 / 268 | 15.4 | 0 | 11.8 | 0.976 | 9.8 | 0.0 | ok | ok | 21.6 |
| 11 | 6 | 500 | 24eaaa | 325 | 116 / 272 | 6.4 | 0 | 2.0 | 0.963 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 21 | 6 | 500 | ba9bb5 | 325 | 116 / 336 | 9.0 | 0 | 2.0 | 0.965 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 3199 | 6 | 500 | dd25e6 | 372 | 112 / 344 | 7.1 | 0 | 17.6 | 0.975 | 0.0 | 0.0 | ok | ok | 60.8 |
| 42 | 6 | 500 | b28daa | 343 | 116 / 288 | 12.2 | 0 | 2.0 | 0.969 | 0.0 | 0.0 | ok | ok | 27.5 |
| 77 | 6 | 500 | 54eb69 | 365 | 112 / 272 | 8.6 | 0 | 11.8 | 0.973 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 505 | 6 | 500 | 8705fe | 346 | 108 / 328 | 5.7 | 0 | 11.8 | 0.979 | 0.0 | 0.0 | ok | ok | 23.5 |
| 101 | 6 | 500 | 34f6ae | 379 | 116 / 352 | 7.0 | 0 | 3.9 | 0.971 | 0.0 | 0.0 | ok | ok | 7.8 |
| 102 | 6 | 500 | fe597e | 332 | 116 / 344 | 7.1 | 0 | 0.0 | 0.962 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 103 | 6 | 500 | 8af0fe | 354 | 116 / 336 | 8.6 | 0 | 19.6 | 0.953 | 0.0 | 0.0 | ok | ok | 15.7 |
| 104 | 6 | 500 | 87d9a0 | 316 | 116 / 312 | 7.2 | 0 | 3.9 | 0.979 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 105 | 6 | 500 | 0baa8b | 445 | 108 / 312 | 8.8 | 0 | 5.9 | 0.988 | 0.0 | 0.0 | ok | ok | 23.5 |
| 106 | 6 | 500 | b6cebb | 442 | 116 / 312 | 6.6 | 0 | 3.9 | 0.994 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 107 | 6 | 500 | 5cb408 | 424 | 100 / 300 | 6.9 | 0 | 0.0 | 0.959 | 23.5 | 0.0 | ok | ok | 54.9 |
| 108 | 6 | 500 | ba8f7a | 496 | 104 / 320 | 9.4 | 0 | 5.9 | 0.979 | 0.0 | 0.0 | ok | F: icehouse 94% of the time, outside 5-70% | 94.1 |
| 201 | 6 | 500 | 6431ba | 483 | 120 / 344 | 6.9 | 0 | 21.6 | 0.984 | 0.0 | 0.0 | ok | ok | 45.1 |
| 202 | 6 | 500 | d0dc04 | 496 | 116 / 328 | 7.1 | 0 | 0.0 | 0.965 | 0.0 | 0.0 | ok | ok | 39.2 |
| 203 | 6 | 500 | 04e901 | 403 | 112 / 260 | 8.2 | 0 | 25.5 | 0.956 | 0.0 | 0.0 | F | F: icehouse 0% of the time, outside 5-70% | 0.0 |
| 204 | 6 | 500 | d289b7 | 444 | 116 / 348 | 11.9 | 0 | 0.0 | 0.978 | 0.0 | 0.0 | ok | ok | 47.1 |
| 205 | 6 | 500 | 570258 | 429 | 104 / 312 | 10.7 | 0 | 3.9 | 0.977 | 0.0 | 0.0 | ok | ok | 13.7 |
| 206 | 6 | 500 | 3e4d1e | 448 | 116 / 332 | 7.1 | 0 | 0.0 | 0.961 | 0.0 | 0.0 | ok | ok | 7.8 |
| 207 | 6 | 500 | b93d32 | 537 | 116 / 360 | 9.4 | 0 | 0.0 | 0.981 | 21.6 | 0.0 | ok | F: icehouse 100% of the time, outside 5-70% | 100.0 |
| 208 | 6 | 500 | 74921e | 390 | 116 / 344 | 13.5 | 0 | 9.8 | 0.966 | 0.0 | 0.0 | ok | ok | 19.6 |
| 209 | 6 | 500 | 1307ca | 422 | 116 / 324 | 11.1 | 0 | 3.9 | 0.978 | 0.0 | 0.0 | ok | ok | 9.8 |
| 210 | 6 | 500 | 73f64d | 400 | 116 / 356 | 10.9 | 0 | 3.9 | 0.996 | 5.9 | 0.0 | ok | ok | 51.0 |
| 211 | 6 | 500 | 2568a9 | 424 | 96 / 328 | 8.7 | 0 | 0.0 | 0.975 | 0.0 | 0.0 | ok | ok | 17.6 |
| 212 | 6 | 500 | 1875a8 | 372 | 112 / 340 | 7.1 | 0 | 2.0 | 0.968 | 0.0 | 0.0 | ok | ok | 17.6 |
| 213 | 6 | 500 | 43dda4 | 357 | 112 / 360 | 8.1 | 0 | 0.0 | 0.982 | 0.0 | 0.0 | ok | ok | 45.1 |
| 214 | 6 | 500 | b05e14 | 313 | 108 / 244 | 8.2 | 0 | 0.0 | 0.95 | 0.0 | 0.0 | ok | ok | 11.8 |
| 215 | 6 | 500 | c47f22 | 311 | 96 / 332 | 10.8 | 0 | 7.8 | 0.962 | 17.6 | 0.0 | ok | ok | 49.0 |
| 216 | 6 | 500 | f0ffe0 | 299 | 104 / 336 | 5.6 | 0 | 5.9 | 0.969 | 0.0 | 0.0 | ok | F: icehouse 0% of the time, outside 5-70% | 0.0 |

## Medians by seed (after 300 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | sea_tect_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 32.7 | 39.2 | 34.6 | 13.0 | 47.9 | 5.0 | 144.4 | -7.8 | 154.9 | 0.5 | 18.7 | 0.5 | 28.8 | 6.0 | 0.4 | 0.1 | 4.8 | 34.2 | 350.4 | 7.0 | 22.9 |
| 2 | 6 | 33.1 | 38.8 | 34.8 | 11.0 | 54.3 | 4.2 | 86.7 | -11.7 | 93.6 | 1.0 | 15.9 | 0.3 | 26.1 | 6.3 | 0.5 | 0.2 | 5.6 | 35.4 | 349.2 | 8.0 | 24.7 |
| 11 | 6 | 33.3 | 41.2 | 33.1 | 12.0 | 54.9 | 4.1 | 73.6 | -3.2 | 79.3 | 0.3 | 18.3 | -0.0 | 28.6 | 4.0 | 0.3 | 0.1 | 4.9 | 37.5 | 360.3 | 4.0 | 28.9 |
| 21 | 6 | 32.6 | 41.0 | 33.4 | 13.0 | 45.3 | 3.8 | 149.1 | -1.7 | 149.3 | 0.1 | 18.5 | 0.1 | 29.7 | 4.6 | 0.3 | 0.1 | 5.7 | 29.9 | 369.6 | 13.0 | 14.3 |
| 3199 | 6 | 32.9 | 39.5 | 34.5 | 13.0 | 50.6 | 4.6 | 144.5 | -29.0 | 161.8 | 1.7 | 14.9 | 0.1 | 23.1 | 5.1 | 0.6 | 0.1 | 6.2 | 35.5 | 366.9 | 7.0 | 18.2 |
| 42 | 6 | 33.1 | 40.4 | 33.5 | 13.0 | 46.9 | 4.1 | 168.2 | -14.3 | 168.3 | 0.8 | 17.3 | 0.5 | 24.6 | 4.6 | 0.4 | 0.1 | 4.3 | 41.4 | 366.4 | 10.0 | 18.3 |
| 77 | 6 | 34.6 | 39.7 | 34.5 | 10.0 | 58.5 | 5.0 | 30.6 | -2.1 | 30.6 | 0.2 | 18.6 | 0.1 | 35.1 | 5.7 | 0.4 | 0.1 | 4.7 | 31.6 | 312.2 | 8.0 | 20.7 |
| 505 | 6 | 34.1 | 39.0 | 34.8 | 9.0 | 63.6 | 5.0 | -33.9 | -11.2 | -33.6 | 1.0 | 16.4 | -0.2 | 32.3 | 5.1 | 0.4 | 0.1 | 7.5 | 29.0 | 334.2 | 6.0 | 26.5 |
| 101 | 6 | 33.8 | 41.0 | 33.1 | 11.0 | 63.8 | 4.2 | -4.7 | -3.0 | -1.1 | 0.2 | 17.6 | -0.8 | 20.1 | 3.2 | 0.4 | 0.1 | 5.1 | 17.8 | 284.9 | 6.0 | 14.0 |
| 102 | 6 | 33.6 | 41.1 | 33.3 | 11.0 | 54.4 | 3.8 | 70.7 | -2.2 | 72.6 | 0.2 | 17.4 | -0.0 | 33.5 | 7.5 | 0.3 | 0.1 | 4.8 | 31.5 | 346.9 | 10.0 | 24.7 |
| 103 | 6 | 33.6 | 40.0 | 33.7 | 14.0 | 55.8 | 4.4 | 52.8 | -6.0 | 66.0 | 0.4 | 15.9 | -0.5 | 24.1 | 2.9 | 0.4 | 0.1 | 4.2 | 16.2 | 330.4 | 6.0 | 16.2 |
| 104 | 6 | 34.3 | 40.0 | 33.7 | 13.0 | 48.3 | 4.4 | 135.6 | -3.3 | 137.3 | 0.2 | 17.2 | 0.1 | 29.3 | 3.9 | 0.3 | 0.1 | 3.9 | 33.0 | 329.1 | 5.0 | 19.7 |
| 105 | 6 | 33.5 | 41.1 | 33.7 | 11.0 | 50.0 | 4.1 | 123.9 | -6.1 | 128.4 | 0.5 | 16.8 | 0.1 | 24.8 | 3.3 | 0.3 | 0.1 | 4.1 | 35.3 | 357.2 | 7.0 | 20.6 |
| 106 | 6 | 34.1 | 40.6 | 33.6 | 14.0 | 50.9 | 4.5 | 139.5 | -8.2 | 145.4 | 0.8 | 18.8 | 0.4 | 20.6 | 3.7 | 0.4 | 0.1 | 5.6 | 41.8 | 372.7 | 8.0 | 22.2 |
| 107 | 6 | 33.2 | 41.4 | 32.8 | 12.0 | 53.8 | 3.6 | 37.4 | -39.7 | 60.8 | 1.7 | 12.4 | -0.6 | 21.6 | 1.9 | 0.3 | 0.1 | 4.6 | 21.5 | 377.6 | 9.0 | 24.1 |
| 108 | 6 | 32.1 | 41.6 | 32.8 | 12.0 | 53.8 | 4.0 | 30.7 | -53.0 | 83.0 | 2.8 | 13.9 | -0.3 | 17.8 | 2.9 | 0.5 | 0.1 | 5.3 | 39.0 | 376.0 | 9.0 | 19.8 |
| 201 | 6 | 34.2 | 40.4 | 34.1 | 11.0 | 54.6 | 4.3 | 39.7 | -18.6 | 63.1 | 1.2 | 16.3 | 0.2 | 23.1 | 4.4 | 0.6 | 0.2 | 4.3 | 36.0 | 347.4 | 10.0 | 14.4 |
| 202 | 6 | 33.1 | 40.6 | 33.3 | 15.0 | 47.6 | 4.5 | 157.4 | -17.7 | 180.1 | 1.4 | 16.2 | -0.5 | 22.0 | 3.5 | 0.3 | 0.1 | 4.8 | 17.6 | 335.1 | 14.0 | 18.7 |
| 203 | 6 | 34.1 | 40.8 | 33.0 | 9.0 | 69.4 | 4.5 | 21.8 | -0.1 | 21.9 | 0.0 | 19.5 | 0.4 | 30.6 | 6.0 | 0.3 | 0.1 | 5.6 | 34.7 | 346.4 | 7.0 | 25.4 |
| 204 | 6 | 32.9 | 39.9 | 34.0 | 14.0 | 51.3 | 4.1 | 154.0 | -17.5 | 171.5 | 1.3 | 18.2 | 0.3 | 21.0 | 3.3 | 0.3 | 0.1 | 5.4 | 39.6 | 348.7 | 9.0 | 14.2 |
| 205 | 6 | 32.5 | 39.7 | 34.1 | 14.0 | 47.7 | 4.7 | 167.0 | -2.2 | 172.2 | 0.1 | 18.1 | 0.4 | 23.0 | 2.7 | 0.3 | 0.1 | 4.2 | 30.8 | 379.4 | 10.0 | 16.5 |
| 206 | 6 | 32.7 | 40.5 | 33.6 | 11.0 | 52.5 | 4.3 | 96.8 | -16.5 | 116.6 | 1.4 | 20.1 | 0.5 | 18.9 | 2.5 | 0.3 | 0.1 | 5.9 | 40.5 | 370.2 | 9.0 | 12.4 |
| 207 | 6 | 33.8 | 39.9 | 34.4 | 10.0 | 67.4 | 3.7 | -35.1 | -36.3 | 5.6 | 3.0 | 15.9 | -0.1 | 15.5 | 2.6 | 0.5 | 0.1 | 5.5 | 35.9 | 274.4 | 11.0 | 14.9 |
| 208 | 6 | 33.8 | 40.4 | 33.7 | 10.0 | 57.0 | 4.8 | 35.2 | -3.3 | 47.4 | 0.3 | 20.5 | -0.1 | 25.4 | 4.6 | 0.6 | 0.2 | 4.7 | 26.8 | 351.6 | 8.0 | 17.6 |
| 209 | 6 | 33.9 | 40.8 | 33.8 | 11.0 | 68.1 | 4.0 | -8.4 | -4.3 | -6.6 | 0.4 | 18.9 | -0.4 | 30.9 | 4.5 | 0.3 | 0.0 | 6.7 | 21.5 | 285.8 | 6.0 | 25.5 |
| 210 | 6 | 33.2 | 39.9 | 34.5 | 13.0 | 48.6 | 4.1 | 128.1 | -23.1 | 147.2 | 1.2 | 17.5 | 0.0 | 18.7 | 3.4 | 0.5 | 0.1 | 5.3 | 36.1 | 350.7 | 8.0 | 14.4 |
| 211 | 6 | 33.0 | 40.4 | 33.5 | 11.0 | 54.8 | 4.4 | 68.1 | -16.7 | 89.5 | 1.2 | 20.0 | 0.2 | 25.8 | 3.7 | 0.4 | 0.1 | 4.8 | 31.7 | 313.8 | 8.0 | 18.5 |
| 212 | 6 | 32.4 | 40.0 | 33.7 | 14.0 | 54.5 | 4.3 | 89.2 | -12.1 | 115.1 | 1.0 | 15.4 | -0.1 | 22.9 | 2.4 | 0.4 | 0.1 | 5.0 | 35.8 | 348.1 | 9.0 | 13.1 |
| 213 | 6 | 33.6 | 40.0 | 34.1 | 15.0 | 46.7 | 4.4 | 137.8 | -19.5 | 162.9 | 1.6 | 17.6 | 0.4 | 16.9 | 3.0 | 0.3 | 0.1 | 4.9 | 41.2 | 360.2 | 6.0 | 20.5 |
| 214 | 6 | 32.7 | 40.3 | 33.3 | 11.0 | 56.2 | 4.4 | 42.9 | -4.2 | 61.2 | 0.3 | 16.8 | 0.4 | 24.2 | 3.0 | 0.4 | 0.1 | 5.2 | 34.1 | 355.6 | 6.0 | 17.3 |
| 215 | 6 | 33.7 | 40.5 | 33.7 | 9.0 | 64.6 | 4.0 | -57.4 | -18.9 | -24.1 | 1.4 | 13.9 | -0.4 | 24.0 | 3.4 | 0.4 | 0.1 | 5.4 | 34.5 | 308.4 | 8.0 | 22.1 |
| 216 | 6 | 34.2 | 40.9 | 33.2 | 11.0 | 53.8 | 4.3 | 124.6 | -0.7 | 124.6 | 0.0 | 18.7 | 0.7 | 22.3 | 3.3 | 0.3 | 0.1 | 4.1 | 42.8 | 378.1 | 8.0 | 24.1 |

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

## Top outliers (of 257 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 203 | 6 | giant_lake_frames | run | - | 25.50 | -..5 | 4.1 |
| 201 | 6 | giant_lake_frames | run | - | 21.60 | -..5 | 3.32 |
| 103 | 6 | giant_lake_frames | run | - | 19.60 | -..5 | 2.92 |
| 3199 | 6 | giant_lake_frames | run | - | 17.60 | -..5 | 2.52 |
| 106 | 6 | lake_max_mkm2 | 412-412 | 1 | 9.58 | -..1.0 | 1.783 |
| 203 | 6 | lake_max_mkm2 | 304-324 | 6 | 7.52 | -..1.0 | 1.615 |
| 201 | 6 | lake_max_mkm2 | 328-364 | 8 | 6.61 | -..1.0 | 1.479 |
| 2 | 6 | giant_lake_frames | run | - | 11.80 | -..5 | 1.36 |
| 77 | 6 | giant_lake_frames | run | - | 11.80 | -..5 | 1.36 |
| 505 | 6 | giant_lake_frames | run | - | 11.80 | -..5 | 1.36 |
| 107 | 6 | sea_ice_below_150 | run | - | 23.50 | -..10 | 1.35 |
| 207 | 6 | sea_ice_below_150 | run | - | 21.60 | -..10 | 1.16 |
| 208 | 6 | giant_lake_frames | run | - | 9.80 | -..5 | 0.96 |
| 77 | 6 | lake_max_mkm2 | 436-452 | 5 | 4.96 | -..1.0 | 0.948 |
| 1 | 6 | lake_max_mkm2 | 392-392 | 1 | 5.16 | -..1.0 | 0.864 |
| 215 | 6 | sea_ice_below_150 | run | - | 17.60 | -..10 | 0.76 |
| 209 | 6 | lake_max_mkm2 | 364-364 | 1 | 4.20 | -..1.0 | 0.665 |
| 2 | 6 | lake_max_mkm2 | 380-400 | 4 | 3.66 | -..1.0 | 0.617 |
| 108 | 6 | lake_max_mkm2 | 332-332 | 1 | 3.74 | -..1.0 | 0.569 |
| 215 | 6 | giant_lake_frames | run | - | 7.80 | -..5 | 0.56 |
| 103 | 6 | lake_max_mkm2 | 444-448 | 2 | 3.54 | -..1.0 | 0.547 |
| 203 | 6 | lake_max_mkm2 | 448-448 | 1 | 3.62 | -..1.0 | 0.546 |
| 3199 | 6 | lake_max_mkm2 | 476-500 | 7 | 2.96 | -..1.0 | 0.502 |
| 201 | 6 | lake_max_mkm2 | 472-472 | 1 | 3.30 | -..1.0 | 0.478 |
| 205 | 6 | lake_max_mkm2 | 316-320 | 2 | 3.11 | -..1.0 | 0.456 |
| 11 | 6 | lake_max_mkm2 | 304-304 | 1 | 3.09 | -..1.0 | 0.434 |
| 216 | 6 | lake_max_mkm2 | 340-340 | 1 | 2.89 | -..1.0 | 0.393 |
| 105 | 6 | lake_max_mkm2 | 324-332 | 3 | 2.60 | -..1.0 | 0.359 |
| 210 | 6 | lake_max_mkm2 | 448-448 | 1 | 2.65 | -..1.0 | 0.344 |
| 103 | 6 | lake_max_mkm2 | 472-496 | 7 | 2.32 | -..1.0 | 0.336 |

## Per seed: min / median / max after the 300 Myr spin-up, and spells outside the envelopes

### Seed 1, L6 (run cac49b)

![seed 1 L6](seed1_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.89 | 32.69 | 33.52 |  |
| cont_pct | 37.05 | 39.21 | 40.78 |  |
| cont_km | 33.81 | 34.65 | 36.55 |  |
| plates | 10.00 | 13.00 | 17.00 |  |
| ocean_age | 39.80 | 47.90 | 59.50 |  |
| speed | 3.26 | 5.03 | 5.53 |  |
| sea_level | -143.80 | 144.40 | 218.10 |  |
| sea_ice_m | -179.80 | -7.80 | -0.00 |  |
| sea_tect_m | 36.00 | 154.90 | 218.10 |  |
| ice_pct | 0.00 | 0.50 | 7.30 |  |
| temp | 12.90 | 18.70 | 25.00 |  |
| co2 | -0.21 | 0.53 | 1.08 |  |
| dry_pct | 23.66 | 28.83 | 36.78 |  |
| inland_pct | 2.31 | 5.97 | 11.54 | 300-500: 2.31 |
| lake_pct | 0.12 | 0.40 | 3.37 | 368-368: 0.12; 392-392: 3.37; 420-420: 0.12 |
| lake_max_mkm2 | 0.01 | 0.07 | 5.16 | 392-392: 5.16 |
| max_elev_km | 4.01 | 4.82 | 8.39 |  |
| trees_pct | 23.36 | 34.19 | 47.08 |  |
| npp | 215.10 | 350.40 | 426.40 |  |
| landmasses | 4.00 | 7.00 | 12.00 |  |
| largest_pct | 11.40 | 22.90 | 33.00 |  |

### Seed 2, L6 (run 036ccb)

![seed 2 L6](seed2_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.50 | 33.07 | 33.58 |  |
| cont_pct | 37.77 | 38.75 | 39.61 |  |
| cont_km | 34.10 | 34.78 | 35.54 |  |
| plates | 9.00 | 11.00 | 13.00 |  |
| ocean_age | 44.00 | 54.30 | 64.60 |  |
| speed | 2.90 | 4.20 | 5.14 |  |
| sea_level | -253.80 | 86.70 | 166.70 | 500-500: -253.80 |
| sea_ice_m | -250.80 | -11.70 | -1.00 | 500-500: -250.80 |
| sea_tect_m | -3.00 | 93.60 | 178.50 |  |
| ice_pct | 0.10 | 1.00 | 7.90 |  |
| temp | 7.70 | 15.90 | 23.10 | 496-500: 7.70 |
| co2 | -0.45 | 0.27 | 1.02 |  |
| dry_pct | 19.21 | 26.05 | 40.95 |  |
| inland_pct | 2.08 | 6.27 | 14.18 | 304-384: 3.97; 396-456: 2.08; 468-476: 5.45; 488-500: 2.62 |
| lake_pct | 0.16 | 0.49 | 2.43 | 324-328: 0.16; 340-340: 0.16; 368-368: 0.19 |
| lake_max_mkm2 | 0.03 | 0.16 | 3.66 | 308-312: 1.85; 380-400: 3.66 |
| max_elev_km | 4.21 | 5.62 | 7.53 |  |
| trees_pct | 24.83 | 35.35 | 42.86 |  |
| npp | 234.10 | 349.20 | 483.60 |  |
| landmasses | 4.00 | 8.00 | 13.00 |  |
| largest_pct | 16.30 | 24.70 | 28.90 |  |

### Seed 11, L6 (run 24eaaa)

![seed 11 L6](seed11_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.65 | 33.26 | 33.79 |  |
| cont_pct | 40.03 | 41.17 | 41.58 |  |
| cont_km | 32.65 | 33.12 | 34.15 |  |
| plates | 9.00 | 12.00 | 16.00 |  |
| ocean_age | 39.20 | 54.90 | 57.80 |  |
| speed | 2.82 | 4.06 | 5.33 |  |
| sea_level | 48.20 | 73.60 | 224.70 |  |
| sea_ice_m | -13.30 | -3.20 | -0.00 |  |
| sea_tect_m | 61.30 | 79.30 | 227.90 |  |
| ice_pct | 0.00 | 0.30 | 1.00 |  |
| temp | 15.30 | 18.30 | 21.70 |  |
| co2 | -0.69 | -0.02 | 0.65 |  |
| dry_pct | 19.99 | 28.55 | 40.71 |  |
| inland_pct | 1.18 | 3.99 | 16.85 | 300-500: 1.18 |
| lake_pct | 0.07 | 0.33 | 4.17 | 304-304: 4.17; 428-452: 0.07; 472-500: 0.09 |
| lake_max_mkm2 | 0.01 | 0.05 | 3.09 | 304-304: 3.09 |
| max_elev_km | 3.26 | 4.90 | 8.16 |  |
| trees_pct | 13.01 | 37.47 | 50.38 | 344-344: 50.38 |
| npp | 145.30 | 360.30 | 407.00 | 300-316: 145.30 |
| landmasses | 1.00 | 4.00 | 12.00 | 388-404: 1; 444-444: 2 |
| largest_pct | 16.10 | 28.90 | 33.70 |  |

### Seed 21, L6 (run ba9bb5)

![seed 21 L6](seed21_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.86 | 32.61 | 33.04 |  |
| cont_pct | 39.26 | 40.97 | 41.43 |  |
| cont_km | 32.79 | 33.35 | 34.97 |  |
| plates | 11.00 | 13.00 | 15.00 |  |
| ocean_age | 42.10 | 45.30 | 64.20 |  |
| speed | 2.34 | 3.79 | 4.74 |  |
| sea_level | -1.80 | 149.10 | 205.10 |  |
| sea_ice_m | -7.40 | -1.70 | -0.00 |  |
| sea_tect_m | 3.70 | 149.30 | 205.60 |  |
| ice_pct | 0.00 | 0.10 | 0.50 |  |
| temp | 15.20 | 18.50 | 24.20 |  |
| co2 | -0.66 | 0.13 | 0.41 |  |
| dry_pct | 18.44 | 29.73 | 47.45 | 348-372: 47.45 |
| inland_pct | 0.96 | 4.63 | 11.77 | 304-312: 5.36; 324-500: 0.96 |
| lake_pct | 0.10 | 0.26 | 1.26 | 308-308: 0.18; 332-340: 0.10; 352-360: 0.14; 372-372: 0.19; +3 more |
| lake_max_mkm2 | 0.01 | 0.05 | 1.43 | 316-316: 1.43 |
| max_elev_km | 4.70 | 5.65 | 8.28 |  |
| trees_pct | 11.62 | 29.93 | 40.61 |  |
| npp | 204.00 | 369.55 | 416.40 |  |
| landmasses | 5.00 | 13.00 | 17.00 |  |
| largest_pct | 8.80 | 14.30 | 25.80 |  |

### Seed 3199, L6 (run dd25e6)

![seed 3199 L6](seed3199_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.02 | 32.88 | 33.89 |  |
| cont_pct | 36.80 | 39.46 | 40.28 |  |
| cont_km | 33.69 | 34.49 | 36.73 |  |
| plates | 9.00 | 13.00 | 15.00 |  |
| ocean_age | 39.20 | 50.60 | 76.20 |  |
| speed | 2.86 | 4.61 | 5.18 |  |
| sea_level | -162.90 | 144.50 | 205.70 |  |
| sea_ice_m | -68.50 | -29.00 | -13.00 |  |
| sea_tect_m | -94.30 | 161.80 | 220.70 |  |
| ice_pct | 1.00 | 1.70 | 3.30 |  |
| temp | 12.40 | 14.90 | 19.50 |  |
| co2 | -0.52 | 0.07 | 0.48 |  |
| dry_pct | 18.81 | 23.12 | 31.60 |  |
| inland_pct | 1.61 | 5.06 | 13.31 | 300-472: 1.61; 500-500: 7.81 |
| lake_pct | 0.23 | 0.59 | 3.35 | 492-492: 3.35 |
| lake_max_mkm2 | 0.04 | 0.14 | 2.96 | 432-440: 1.11; 476-500: 2.96 |
| max_elev_km | 3.95 | 6.16 | 8.06 |  |
| trees_pct | 29.12 | 35.47 | 53.12 | 336-344: 53.12 |
| npp | 310.90 | 366.90 | 410.50 |  |
| landmasses | 3.00 | 7.00 | 13.00 |  |
| largest_pct | 11.10 | 18.20 | 20.10 |  |

### Seed 42, L6 (run b28daa)

![seed 42 L6](seed42_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.33 | 33.06 | 34.00 |  |
| cont_pct | 39.30 | 40.41 | 41.14 |  |
| cont_km | 33.08 | 33.50 | 34.55 |  |
| plates | 11.00 | 13.00 | 17.00 |  |
| ocean_age | 38.90 | 46.90 | 61.20 |  |
| speed | 2.90 | 4.08 | 5.22 |  |
| sea_level | 6.60 | 168.20 | 209.90 |  |
| sea_ice_m | -52.70 | -14.30 | -0.00 |  |
| sea_tect_m | 23.00 | 168.30 | 215.80 |  |
| ice_pct | 0.00 | 0.80 | 3.30 |  |
| temp | 12.90 | 17.30 | 25.10 |  |
| co2 | 0.01 | 0.48 | 0.82 |  |
| dry_pct | 17.57 | 24.55 | 40.59 |  |
| inland_pct | 1.70 | 4.63 | 11.98 | 300-500: 1.70 |
| lake_pct | 0.13 | 0.41 | 1.30 | 300-300: 0.13; 320-328: 0.15 |
| lake_max_mkm2 | 0.03 | 0.07 | 1.31 | 500-500: 1.31 |
| max_elev_km | 3.66 | 4.33 | 7.84 |  |
| trees_pct | 32.40 | 41.38 | 46.73 |  |
| npp | 204.60 | 366.40 | 428.70 |  |
| landmasses | 6.00 | 10.00 | 14.00 |  |
| largest_pct | 9.30 | 18.30 | 30.70 |  |

### Seed 77, L6 (run 54eb69)

![seed 77 L6](seed77_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 34.14 | 34.64 | 35.47 |  |
| cont_pct | 38.01 | 39.66 | 41.38 |  |
| cont_km | 33.24 | 34.52 | 35.36 |  |
| plates | 7.00 | 10.00 | 12.00 |  |
| ocean_age | 46.40 | 58.50 | 95.50 |  |
| speed | 2.81 | 4.97 | 6.13 |  |
| sea_level | -190.90 | 30.60 | 150.20 |  |
| sea_ice_m | -15.00 | -2.10 | -0.00 |  |
| sea_tect_m | -186.50 | 30.60 | 151.80 |  |
| ice_pct | 0.00 | 0.20 | 1.30 |  |
| temp | 12.20 | 18.60 | 20.80 |  |
| co2 | -0.27 | 0.14 | 0.60 |  |
| dry_pct | 14.87 | 35.09 | 40.85 |  |
| inland_pct | 2.04 | 5.65 | 15.41 | 300-500: 2.04 |
| lake_pct | 0.18 | 0.41 | 4.45 | 300-304: 0.18; 332-332: 0.18; 360-360: 0.19; 436-436: 3.79; +1 more |
| lake_max_mkm2 | 0.03 | 0.15 | 4.96 | 436-452: 4.96; 484-484: 1.54 |
| max_elev_km | 3.12 | 4.68 | 8.45 |  |
| trees_pct | 25.48 | 31.65 | 40.76 |  |
| npp | 230.70 | 312.20 | 371.30 |  |
| landmasses | 4.00 | 8.00 | 12.00 |  |
| largest_pct | 12.10 | 20.70 | 34.40 |  |

### Seed 505, L6 (run 8705fe)

![seed 505 L6](seed505_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.39 | 34.08 | 34.73 |  |
| cont_pct | 37.49 | 38.96 | 39.88 |  |
| cont_km | 34.12 | 34.81 | 35.98 |  |
| plates | 6.00 | 9.00 | 11.00 |  |
| ocean_age | 49.10 | 63.60 | 81.10 |  |
| speed | 3.46 | 5.05 | 6.74 |  |
| sea_level | -210.70 | -33.90 | 116.40 |  |
| sea_ice_m | -75.90 | -11.20 | -0.00 |  |
| sea_tect_m | -160.30 | -33.60 | 118.70 |  |
| ice_pct | 0.00 | 1.00 | 4.90 |  |
| temp | 14.00 | 16.40 | 19.70 |  |
| co2 | -1.14 | -0.23 | 0.46 |  |
| dry_pct | 13.74 | 32.27 | 37.04 |  |
| inland_pct | 2.72 | 5.09 | 10.07 | 300-500: 2.72 |
| lake_pct | 0.18 | 0.41 | 1.57 | 348-364: 0.18 |
| lake_max_mkm2 | 0.03 | 0.09 | 2.06 | 376-376: 2.06; 416-432: 1.83 |
| max_elev_km | 4.01 | 7.47 | 8.61 |  |
| trees_pct | 10.41 | 29.00 | 38.15 |  |
| npp | 205.70 | 334.20 | 410.20 |  |
| landmasses | 2.00 | 6.00 | 9.00 | 332-344: 2 |
| largest_pct | 20.30 | 26.50 | 34.30 |  |

### Seed 101, L6 (run 34f6ae)

![seed 101 L6](seed101_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.58 | 33.82 | 34.23 |  |
| cont_pct | 39.45 | 40.96 | 41.44 |  |
| cont_km | 32.81 | 33.15 | 34.78 |  |
| plates | 7.00 | 11.00 | 13.00 |  |
| ocean_age | 55.60 | 63.80 | 79.50 |  |
| speed | 3.07 | 4.15 | 5.44 |  |
| sea_level | -164.80 | -4.70 | 83.90 |  |
| sea_ice_m | -25.00 | -3.00 | -0.00 |  |
| sea_tect_m | -144.80 | -1.10 | 86.00 |  |
| ice_pct | 0.00 | 0.20 | 1.70 |  |
| temp | 13.30 | 17.60 | 20.30 |  |
| co2 | -1.36 | -0.77 | -0.34 |  |
| dry_pct | 13.61 | 20.15 | 30.27 |  |
| inland_pct | 0.28 | 3.21 | 9.02 | 304-500: 0.28 |
| lake_pct | 0.23 | 0.41 | 1.11 |  |
| lake_max_mkm2 | 0.03 | 0.14 | 1.28 | 440-448: 1.28 |
| max_elev_km | 4.38 | 5.10 | 7.90 |  |
| trees_pct | 4.81 | 17.77 | 29.48 | 432-460: 4.81 |
| npp | 138.70 | 284.95 | 363.70 | 352-360: 138.70; 372-372: 183.70 |
| landmasses | 3.00 | 6.00 | 13.00 |  |
| largest_pct | 9.80 | 14.00 | 31.80 |  |

### Seed 102, L6 (run fe597e)

![seed 102 L6](seed102_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.62 | 33.62 | 34.18 |  |
| cont_pct | 39.01 | 41.11 | 42.73 |  |
| cont_km | 31.51 | 33.31 | 34.77 |  |
| plates | 9.00 | 11.00 | 13.00 |  |
| ocean_age | 44.60 | 54.40 | 62.70 |  |
| speed | 2.89 | 3.79 | 4.90 |  |
| sea_level | 7.70 | 70.70 | 140.10 |  |
| sea_ice_m | -6.80 | -2.20 | -0.70 |  |
| sea_tect_m | 9.60 | 72.60 | 142.50 |  |
| ice_pct | 0.10 | 0.20 | 0.50 |  |
| temp | 13.40 | 17.40 | 20.50 |  |
| co2 | -0.80 | -0.01 | 0.76 |  |
| dry_pct | 26.88 | 33.53 | 38.46 |  |
| inland_pct | 2.37 | 7.48 | 12.34 | 300-396: 2.97; 408-408: 5.87; 420-440: 5.56; 456-456: 7.48; +2 more |
| lake_pct | 0.15 | 0.35 | 0.80 | 308-308: 0.16; 344-348: 0.18; 436-436: 0.19; 496-500: 0.15 |
| lake_max_mkm2 | 0.03 | 0.07 | 0.70 |  |
| max_elev_km | 3.14 | 4.83 | 8.44 |  |
| trees_pct | 16.49 | 31.46 | 41.04 |  |
| npp | 156.30 | 346.90 | 386.40 | 348-348: 156.30 |
| landmasses | 6.00 | 10.00 | 14.00 |  |
| largest_pct | 16.70 | 24.70 | 34.00 |  |

### Seed 103, L6 (run 8af0fe)

![seed 103 L6](seed103_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.88 | 33.57 | 34.60 |  |
| cont_pct | 39.30 | 39.95 | 40.75 |  |
| cont_km | 32.75 | 33.73 | 34.45 |  |
| plates | 11.00 | 14.00 | 16.00 |  |
| ocean_age | 48.60 | 55.80 | 69.00 |  |
| speed | 3.05 | 4.43 | 5.20 |  |
| sea_level | -95.60 | 52.80 | 135.60 |  |
| sea_ice_m | -61.80 | -6.00 | -0.80 |  |
| sea_tect_m | -91.80 | 66.00 | 138.50 |  |
| ice_pct | 0.10 | 0.40 | 3.00 |  |
| temp | 11.20 | 15.90 | 19.80 |  |
| co2 | -1.68 | -0.48 | 0.79 |  |
| dry_pct | 18.39 | 24.13 | 28.80 |  |
| inland_pct | 0.59 | 2.92 | 7.35 | 300-500: 0.59 |
| lake_pct | 0.12 | 0.36 | 2.27 | 336-348: 0.12; 372-372: 0.19; 460-464: 0.20 |
| lake_max_mkm2 | 0.03 | 0.09 | 3.54 | 432-432: 2.39; 444-448: 3.54; 472-496: 2.32 |
| max_elev_km | 3.05 | 4.20 | 6.59 |  |
| trees_pct | 0.57 | 16.21 | 51.27 | 332-336: 51.27; 400-468: 0.57 |
| npp | 164.60 | 330.35 | 429.30 | 400-400: 164.60 |
| landmasses | 3.00 | 6.00 | 11.00 |  |
| largest_pct | 13.30 | 16.20 | 31.40 |  |

### Seed 104, L6 (run 87d9a0)

![seed 104 L6](seed104_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.93 | 34.34 | 35.41 |  |
| cont_pct | 38.65 | 40.01 | 41.46 |  |
| cont_km | 33.05 | 33.67 | 35.23 |  |
| plates | 11.00 | 13.00 | 15.00 |  |
| ocean_age | 42.20 | 48.30 | 56.40 |  |
| speed | 3.82 | 4.36 | 5.00 |  |
| sea_level | 70.20 | 135.60 | 180.80 |  |
| sea_ice_m | -13.80 | -3.30 | -0.00 |  |
| sea_tect_m | 71.70 | 137.30 | 184.80 |  |
| ice_pct | 0.00 | 0.20 | 0.80 |  |
| temp | 15.00 | 17.20 | 22.20 |  |
| co2 | -0.48 | 0.09 | 0.56 |  |
| dry_pct | 21.18 | 29.34 | 34.05 |  |
| inland_pct | 1.16 | 3.94 | 8.28 | 300-500: 1.16 |
| lake_pct | 0.11 | 0.26 | 0.99 | 372-384: 0.11; 396-412: 0.16; 440-444: 0.11; 456-476: 0.16 |
| lake_max_mkm2 | 0.03 | 0.06 | 1.43 | 388-388: 1.43; 424-424: 1.01 |
| max_elev_km | 2.81 | 3.92 | 8.20 |  |
| trees_pct | 16.24 | 32.95 | 41.33 |  |
| npp | 190.90 | 329.05 | 440.80 | 312-312: 190.90; 324-324: 197.00 |
| landmasses | 3.00 | 5.00 | 7.00 |  |
| largest_pct | 11.80 | 19.70 | 24.60 |  |

### Seed 105, L6 (run 0baa8b)

![seed 105 L6](seed105_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.54 | 33.54 | 34.19 |  |
| cont_pct | 38.72 | 41.07 | 42.07 |  |
| cont_km | 32.85 | 33.66 | 35.25 |  |
| plates | 10.00 | 11.00 | 14.00 |  |
| ocean_age | 43.40 | 50.00 | 64.10 |  |
| speed | 3.27 | 4.08 | 5.20 |  |
| sea_level | -108.10 | 123.90 | 190.20 |  |
| sea_ice_m | -100.60 | -6.10 | -0.40 |  |
| sea_tect_m | -9.50 | 128.40 | 193.80 |  |
| ice_pct | 0.00 | 0.50 | 3.60 |  |
| temp | 11.70 | 16.80 | 20.50 |  |
| co2 | -0.90 | 0.13 | 0.56 |  |
| dry_pct | 19.95 | 24.77 | 42.79 |  |
| inland_pct | 1.51 | 3.26 | 14.94 | 312-312: 7.67; 324-500: 1.51 |
| lake_pct | 0.14 | 0.27 | 1.79 | 352-352: 0.18; 384-420: 0.14; 484-488: 0.16; 500-500: 0.16 |
| lake_max_mkm2 | 0.01 | 0.05 | 2.60 | 324-332: 2.60 |
| max_elev_km | 3.09 | 4.06 | 5.94 |  |
| trees_pct | 15.59 | 35.32 | 46.00 |  |
| npp | 220.50 | 357.20 | 474.30 |  |
| landmasses | 3.00 | 7.00 | 11.00 |  |
| largest_pct | 14.60 | 20.60 | 33.80 |  |

### Seed 106, L6 (run b6cebb)

![seed 106 L6](seed106_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.07 | 34.06 | 34.58 |  |
| cont_pct | 38.93 | 40.58 | 40.98 |  |
| cont_km | 33.25 | 33.64 | 34.80 |  |
| plates | 11.00 | 14.00 | 17.00 |  |
| ocean_age | 44.30 | 50.90 | 55.50 |  |
| speed | 3.78 | 4.50 | 5.12 |  |
| sea_level | 62.10 | 139.50 | 177.00 |  |
| sea_ice_m | -16.80 | -8.20 | -1.10 |  |
| sea_tect_m | 72.60 | 145.40 | 178.30 |  |
| ice_pct | 0.10 | 0.80 | 1.80 |  |
| temp | 14.70 | 18.80 | 21.30 |  |
| co2 | -0.09 | 0.45 | 1.08 |  |
| dry_pct | 13.68 | 20.65 | 35.61 |  |
| inland_pct | 1.16 | 3.68 | 11.63 | 300-308: 4.41; 320-320: 5.81; 332-500: 1.16 |
| lake_pct | 0.07 | 0.38 | 5.88 | 340-380: 0.07; 392-412: 5.88; 424-424: 0.16 |
| lake_max_mkm2 | 0.03 | 0.07 | 9.58 | 312-312: 1.85; 412-412: 9.58 |
| max_elev_km | 3.56 | 5.62 | 8.29 |  |
| trees_pct | 32.73 | 41.82 | 50.38 | 444-444: 50.38 |
| npp | 287.60 | 372.70 | 435.00 |  |
| landmasses | 2.00 | 8.00 | 12.00 | 488-488: 2 |
| largest_pct | 12.00 | 22.20 | 31.00 |  |

### Seed 107, L6 (run 5cb408)

![seed 107 L6](seed107_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.21 | 33.21 | 34.68 |  |
| cont_pct | 40.54 | 41.35 | 41.60 |  |
| cont_km | 32.29 | 32.79 | 33.87 |  |
| plates | 9.00 | 12.00 | 14.00 |  |
| ocean_age | 47.40 | 53.80 | 63.70 |  |
| speed | 3.09 | 3.60 | 4.89 |  |
| sea_level | -192.80 | 37.40 | 119.30 |  |
| sea_ice_m | -196.70 | -39.70 | -0.10 |  |
| sea_tect_m | 0.40 | 60.80 | 121.40 |  |
| ice_pct | 0.00 | 1.70 | 6.30 |  |
| temp | 10.30 | 12.40 | 17.20 |  |
| co2 | -1.21 | -0.60 | 0.15 |  |
| dry_pct | 17.54 | 21.56 | 34.92 |  |
| inland_pct | 0.61 | 1.93 | 6.16 | 300-500: 0.61 |
| lake_pct | 0.11 | 0.27 | 0.79 | 300-304: 0.15; 316-320: 0.11; 380-380: 0.17; 400-400: 0.16; +4 more |
| lake_max_mkm2 | 0.03 | 0.06 | 0.46 |  |
| max_elev_km | 3.62 | 4.57 | 6.69 |  |
| trees_pct | 5.59 | 21.54 | 43.30 | 332-352: 5.59 |
| npp | 142.90 | 377.60 | 484.30 | 300-312: 142.90; 332-348: 159.90 |
| landmasses | 6.00 | 9.00 | 13.00 |  |
| largest_pct | 11.90 | 24.10 | 30.10 |  |

### Seed 108, L6 (run ba8f7a)

![seed 108 L6](seed108_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.18 | 32.08 | 33.19 |  |
| cont_pct | 39.65 | 41.62 | 42.09 |  |
| cont_km | 32.50 | 32.82 | 34.49 |  |
| plates | 9.00 | 12.00 | 14.00 |  |
| ocean_age | 45.30 | 53.80 | 59.80 |  |
| speed | 3.31 | 3.95 | 4.74 |  |
| sea_level | -96.00 | 30.70 | 139.30 |  |
| sea_ice_m | -131.30 | -53.00 | -17.10 |  |
| sea_tect_m | 18.30 | 83.00 | 192.50 |  |
| ice_pct | 1.20 | 2.80 | 5.40 |  |
| temp | 9.30 | 13.90 | 18.70 |  |
| co2 | -1.46 | -0.25 | 0.92 |  |
| dry_pct | 13.08 | 17.84 | 27.32 |  |
| inland_pct | 1.03 | 2.88 | 14.41 | 300-348: 2.69; 360-500: 1.03 |
| lake_pct | 0.28 | 0.48 | 3.19 | 332-332: 3.19 |
| lake_max_mkm2 | 0.03 | 0.10 | 3.74 | 332-332: 3.74; 352-352: 1.28; 472-472: 1.44 |
| max_elev_km | 3.61 | 5.33 | 7.38 |  |
| trees_pct | 4.48 | 39.04 | 51.18 | 316-328: 51.18; 384-392: 4.48 |
| npp | 272.90 | 376.00 | 451.80 |  |
| landmasses | 4.00 | 9.00 | 12.00 |  |
| largest_pct | 7.40 | 19.80 | 28.60 |  |

### Seed 201, L6 (run 6431ba)

![seed 201 L6](seed201_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.41 | 34.16 | 34.73 |  |
| cont_pct | 38.58 | 40.40 | 40.86 |  |
| cont_km | 33.92 | 34.15 | 35.61 |  |
| plates | 9.00 | 11.00 | 14.00 |  |
| ocean_age | 51.20 | 54.60 | 69.80 |  |
| speed | 2.65 | 4.30 | 4.96 |  |
| sea_level | -75.80 | 39.70 | 68.70 |  |
| sea_ice_m | -33.70 | -18.60 | -2.50 |  |
| sea_tect_m | -58.20 | 63.10 | 87.40 |  |
| ice_pct | 0.20 | 1.20 | 2.20 |  |
| temp | 12.30 | 16.30 | 19.20 |  |
| co2 | -1.24 | 0.15 | 0.99 |  |
| dry_pct | 19.76 | 23.06 | 35.84 |  |
| inland_pct | 1.44 | 4.44 | 10.58 | 300-336: 3.05; 348-416: 1.44; 428-500: 1.71 |
| lake_pct | 0.30 | 0.63 | 4.30 | 336-364: 4.30 |
| lake_max_mkm2 | 0.04 | 0.20 | 6.61 | 304-312: 1.54; 328-364: 6.61; 472-472: 3.30 |
| max_elev_km | 3.35 | 4.32 | 8.59 |  |
| trees_pct | 4.73 | 36.01 | 44.14 | 468-484: 4.73 |
| npp | 264.00 | 347.40 | 404.80 |  |
| landmasses | 6.00 | 10.00 | 13.00 |  |
| largest_pct | 11.30 | 14.40 | 20.70 |  |

### Seed 202, L6 (run d0dc04)

![seed 202 L6](seed202_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.58 | 33.08 | 33.55 |  |
| cont_pct | 39.77 | 40.59 | 41.89 |  |
| cont_km | 32.53 | 33.34 | 34.15 |  |
| plates | 7.00 | 15.00 | 17.00 |  |
| ocean_age | 40.10 | 47.60 | 80.20 |  |
| speed | 1.70 | 4.47 | 4.85 | 496-500: 1.70 |
| sea_level | -110.80 | 157.40 | 213.90 |  |
| sea_ice_m | -24.30 | -17.70 | -1.60 |  |
| sea_tect_m | -97.40 | 180.10 | 220.80 |  |
| ice_pct | 0.10 | 1.40 | 1.80 |  |
| temp | 14.20 | 16.20 | 21.30 |  |
| co2 | -1.78 | -0.47 | 0.74 |  |
| dry_pct | 18.71 | 22.03 | 33.00 |  |
| inland_pct | 0.82 | 3.47 | 6.49 | 300-500: 0.82 |
| lake_pct | 0.14 | 0.30 | 1.07 | 304-312: 0.18; 324-324: 0.14; 340-360: 0.15; 376-396: 0.16 |
| lake_max_mkm2 | 0.03 | 0.06 | 0.31 |  |
| max_elev_km | 3.77 | 4.85 | 6.88 |  |
| trees_pct | 1.77 | 17.59 | 46.32 | 488-500: 1.77 |
| npp | 239.90 | 335.05 | 448.80 |  |
| landmasses | 7.00 | 14.00 | 19.00 |  |
| largest_pct | 10.40 | 18.70 | 29.80 |  |

### Seed 203, L6 (run 04e901)

![seed 203 L6](seed203_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.39 | 34.06 | 34.67 |  |
| cont_pct | 38.94 | 40.78 | 41.45 |  |
| cont_km | 32.45 | 33.01 | 34.38 |  |
| plates | 6.00 | 9.00 | 13.00 |  |
| ocean_age | 56.80 | 69.40 | 115.40 |  |
| speed | 3.16 | 4.47 | 5.57 |  |
| sea_level | -330.30 | 21.80 | 63.40 | 300-328: -330.30 |
| sea_ice_m | -3.90 | -0.10 | -0.00 |  |
| sea_tect_m | -330.10 | 21.90 | 63.50 | 300-328: -330.10 |
| ice_pct | 0.00 | 0.00 | 0.30 |  |
| temp | 15.90 | 19.50 | 24.10 |  |
| co2 | -0.36 | 0.44 | 1.50 |  |
| dry_pct | 19.98 | 30.55 | 40.84 |  |
| inland_pct | 0.91 | 5.97 | 17.70 | 328-360: 4.22; 380-456: 0.91; 472-476: 7.16; 500-500: 4.13 |
| lake_pct | 0.14 | 0.34 | 4.46 | 316-324: 4.46; 384-404: 0.14; 420-420: 0.18; 456-456: 0.18; +1 more |
| lake_max_mkm2 | 0.01 | 0.09 | 7.52 | 304-324: 7.52; 372-372: 1.12; 432-436: 2.53; 448-448: 3.62; +2 more |
| max_elev_km | 4.02 | 5.57 | 8.38 |  |
| trees_pct | 24.13 | 34.67 | 48.86 |  |
| npp | 190.40 | 346.40 | 436.60 | 304-304: 190.40 |
| landmasses | 2.00 | 7.00 | 11.00 | 480-480: 2; 496-500: 2 |
| largest_pct | 13.50 | 25.40 | 34.40 |  |

### Seed 204, L6 (run d289b7)

![seed 204 L6](seed204_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.06 | 32.92 | 34.61 |  |
| cont_pct | 38.13 | 39.92 | 41.48 |  |
| cont_km | 33.05 | 33.99 | 35.49 |  |
| plates | 10.00 | 14.00 | 17.00 |  |
| ocean_age | 35.60 | 51.30 | 72.30 |  |
| speed | 3.24 | 4.07 | 4.86 |  |
| sea_level | -196.00 | 154.00 | 232.40 |  |
| sea_ice_m | -113.40 | -17.50 | -6.90 |  |
| sea_tect_m | -82.50 | 171.50 | 241.50 |  |
| ice_pct | 0.40 | 1.30 | 4.60 |  |
| temp | 12.50 | 18.20 | 24.40 |  |
| co2 | -1.02 | 0.26 | 1.01 |  |
| dry_pct | 14.83 | 20.97 | 28.12 |  |
| inland_pct | 1.59 | 3.28 | 7.54 | 300-500: 1.59 |
| lake_pct | 0.19 | 0.35 | 1.07 | 324-324: 0.20; 348-348: 0.19; 480-480: 0.19 |
| lake_max_mkm2 | 0.03 | 0.09 | 0.57 |  |
| max_elev_km | 4.47 | 5.38 | 7.26 |  |
| trees_pct | 11.30 | 39.63 | 51.06 | 356-360: 51.06 |
| npp | 249.90 | 348.70 | 410.30 |  |
| landmasses | 3.00 | 9.00 | 17.00 |  |
| largest_pct | 11.80 | 14.20 | 32.70 |  |

### Seed 205, L6 (run 570258)

![seed 205 L6](seed205_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.51 | 32.55 | 33.84 |  |
| cont_pct | 38.25 | 39.72 | 40.95 |  |
| cont_km | 33.28 | 34.08 | 35.12 |  |
| plates | 12.00 | 14.00 | 16.00 |  |
| ocean_age | 44.20 | 47.70 | 57.30 |  |
| speed | 4.13 | 4.69 | 5.59 |  |
| sea_level | 10.50 | 167.00 | 190.00 |  |
| sea_ice_m | -42.20 | -2.20 | -0.00 |  |
| sea_tect_m | 28.20 | 172.20 | 192.60 |  |
| ice_pct | 0.00 | 0.10 | 3.30 |  |
| temp | 13.40 | 18.10 | 24.10 |  |
| co2 | -0.32 | 0.35 | 1.23 |  |
| dry_pct | 19.09 | 23.03 | 34.58 |  |
| inland_pct | 1.15 | 2.72 | 7.62 | 300-500: 1.15 |
| lake_pct | 0.16 | 0.33 | 2.43 | 364-364: 0.20; 492-500: 0.16 |
| lake_max_mkm2 | 0.03 | 0.06 | 3.11 | 316-320: 3.11 |
| max_elev_km | 3.40 | 4.17 | 5.33 |  |
| trees_pct | 20.19 | 30.83 | 46.96 |  |
| npp | 316.20 | 379.40 | 441.40 |  |
| landmasses | 4.00 | 10.00 | 16.00 |  |
| largest_pct | 11.10 | 16.50 | 32.80 |  |

### Seed 206, L6 (run 3e4d1e)

![seed 206 L6](seed206_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.09 | 32.74 | 33.23 |  |
| cont_pct | 38.98 | 40.55 | 41.40 |  |
| cont_km | 33.11 | 33.59 | 34.71 |  |
| plates | 8.00 | 11.00 | 13.00 |  |
| ocean_age | 42.70 | 52.50 | 62.90 |  |
| speed | 3.31 | 4.29 | 5.08 |  |
| sea_level | 23.20 | 96.80 | 152.30 |  |
| sea_ice_m | -22.40 | -16.50 | -12.50 |  |
| sea_tect_m | 36.30 | 116.60 | 166.60 |  |
| ice_pct | 1.10 | 1.40 | 2.10 |  |
| temp | 16.80 | 20.10 | 23.90 |  |
| co2 | -1.12 | 0.50 | 1.15 |  |
| dry_pct | 15.28 | 18.95 | 23.69 |  |
| inland_pct | 0.71 | 2.51 | 5.63 | 300-500: 0.71 |
| lake_pct | 0.10 | 0.34 | 1.23 | 344-380: 0.10 |
| lake_max_mkm2 | 0.03 | 0.07 | 0.92 |  |
| max_elev_km | 5.01 | 5.87 | 8.29 |  |
| trees_pct | 12.02 | 40.52 | 58.33 | 316-364: 58.33 |
| npp | 257.90 | 370.20 | 413.40 |  |
| landmasses | 5.00 | 9.00 | 14.00 |  |
| largest_pct | 7.40 | 12.40 | 28.80 |  |

### Seed 207, L6 (run b93d32)

![seed 207 L6](seed207_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.86 | 33.76 | 35.49 |  |
| cont_pct | 38.41 | 39.85 | 42.02 |  |
| cont_km | 32.75 | 34.37 | 35.23 |  |
| plates | 6.00 | 10.00 | 16.00 |  |
| ocean_age | 42.00 | 67.40 | 95.90 |  |
| speed | 2.92 | 3.71 | 4.90 |  |
| sea_level | -599.80 | -35.10 | 127.00 | 452-500: -599.80 |
| sea_ice_m | -349.70 | -36.30 | -27.20 | 460-496: -349.70 |
| sea_tect_m | -259.10 | 5.60 | 161.20 | 468-488: -259.10 |
| ice_pct | 1.80 | 3.00 | 11.60 | 464-480: 11.60 |
| temp | 9.70 | 15.90 | 19.10 |  |
| co2 | -1.46 | -0.10 | 0.66 |  |
| dry_pct | 13.40 | 15.54 | 24.37 |  |
| inland_pct | 0.46 | 2.65 | 6.87 | 300-500: 0.46 |
| lake_pct | 0.20 | 0.52 | 1.09 | 484-484: 0.20 |
| lake_max_mkm2 | 0.04 | 0.07 | 0.90 |  |
| max_elev_km | 4.25 | 5.45 | 8.66 |  |
| trees_pct | 4.62 | 35.86 | 46.48 | 432-456: 4.62 |
| npp | 174.90 | 274.45 | 411.20 | 408-412: 174.90; 428-428: 186.30 |
| landmasses | 7.00 | 11.00 | 16.00 |  |
| largest_pct | 9.80 | 14.90 | 25.50 |  |

### Seed 208, L6 (run 74921e)

![seed 208 L6](seed208_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.68 | 33.78 | 34.44 |  |
| cont_pct | 38.67 | 40.43 | 41.84 |  |
| cont_km | 32.51 | 33.71 | 35.01 |  |
| plates | 6.00 | 10.00 | 14.00 |  |
| ocean_age | 41.50 | 57.00 | 75.00 |  |
| speed | 2.69 | 4.80 | 5.45 |  |
| sea_level | -159.20 | 35.20 | 184.00 |  |
| sea_ice_m | -70.40 | -3.30 | -0.00 |  |
| sea_tect_m | -95.20 | 47.40 | 186.40 |  |
| ice_pct | 0.00 | 0.30 | 3.60 |  |
| temp | 11.60 | 20.50 | 25.10 |  |
| co2 | -1.20 | -0.07 | 0.66 |  |
| dry_pct | 21.16 | 25.35 | 35.57 |  |
| inland_pct | 0.94 | 4.56 | 8.17 | 300-500: 0.94 |
| lake_pct | 0.16 | 0.57 | 1.52 | 332-340: 0.16; 356-360: 0.17; 372-372: 0.16 |
| lake_max_mkm2 | 0.03 | 0.22 | 1.43 | 328-328: 1.01; 400-400: 1.26; 420-420: 1.25; 432-432: 1.43; +1 more |
| max_elev_km | 3.76 | 4.65 | 8.31 |  |
| trees_pct | 9.37 | 26.79 | 41.87 | 496-500: 9.37 |
| npp | 224.70 | 351.65 | 406.90 |  |
| landmasses | 5.00 | 8.00 | 13.00 |  |
| largest_pct | 10.30 | 17.60 | 34.00 |  |

### Seed 209, L6 (run 1307ca)

![seed 209 L6](seed209_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 30.41 | 33.94 | 34.40 |  |
| cont_pct | 38.65 | 40.78 | 41.71 |  |
| cont_km | 32.83 | 33.80 | 35.29 |  |
| plates | 8.00 | 11.00 | 13.00 |  |
| ocean_age | 46.10 | 68.10 | 82.10 |  |
| speed | 3.17 | 4.00 | 5.76 |  |
| sea_level | -197.20 | -8.40 | 112.60 |  |
| sea_ice_m | -29.90 | -4.30 | -0.70 |  |
| sea_tect_m | -168.00 | -6.60 | 124.00 |  |
| ice_pct | 0.10 | 0.40 | 2.20 |  |
| temp | 14.00 | 18.90 | 25.10 |  |
| co2 | -1.14 | -0.38 | 0.54 |  |
| dry_pct | 19.22 | 30.86 | 39.41 |  |
| inland_pct | 0.82 | 4.52 | 13.64 | 304-312: 4.13; 324-500: 0.82 |
| lake_pct | 0.09 | 0.28 | 3.03 | 340-340: 0.16; 364-364: 3.03; 412-464: 0.09 |
| lake_max_mkm2 | 0.01 | 0.04 | 4.20 | 364-364: 4.20; 392-392: 1.08 |
| max_elev_km | 4.37 | 6.65 | 8.79 |  |
| trees_pct | 4.36 | 21.48 | 39.48 | 400-400: 9.90; 424-444: 4.36 |
| npp | 153.30 | 285.80 | 429.50 | 348-352: 184.50; 364-380: 153.30; 392-400: 162.70 |
| landmasses | 3.00 | 6.00 | 20.00 |  |
| largest_pct | 17.20 | 25.50 | 34.50 |  |

### Seed 210, L6 (run 73f64d)

![seed 210 L6](seed210_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.74 | 33.24 | 34.15 |  |
| cont_pct | 37.98 | 39.92 | 42.23 |  |
| cont_km | 33.00 | 34.45 | 35.99 |  |
| plates | 10.00 | 13.00 | 16.00 |  |
| ocean_age | 38.30 | 48.60 | 68.70 |  |
| speed | 2.47 | 4.11 | 4.64 |  |
| sea_level | -146.60 | 128.10 | 209.30 |  |
| sea_ice_m | -159.60 | -23.10 | -7.60 |  |
| sea_tect_m | -68.80 | 147.20 | 219.90 |  |
| ice_pct | 0.80 | 1.20 | 5.30 |  |
| temp | 11.50 | 17.50 | 22.40 |  |
| co2 | -1.12 | 0.05 | 0.54 |  |
| dry_pct | 14.60 | 18.67 | 35.05 |  |
| inland_pct | 0.65 | 3.40 | 12.35 | 312-500: 0.65 |
| lake_pct | 0.25 | 0.54 | 2.15 |  |
| lake_max_mkm2 | 0.04 | 0.11 | 2.65 | 308-308: 1.08; 448-448: 2.65 |
| max_elev_km | 4.26 | 5.29 | 6.57 |  |
| trees_pct | 15.23 | 36.11 | 45.61 |  |
| npp | 270.50 | 350.70 | 431.10 |  |
| landmasses | 3.00 | 8.00 | 12.00 |  |
| largest_pct | 12.90 | 14.40 | 21.70 |  |

### Seed 211, L6 (run 2568a9)

![seed 211 L6](seed211_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.44 | 32.98 | 33.73 |  |
| cont_pct | 38.40 | 40.36 | 41.51 |  |
| cont_km | 32.89 | 33.51 | 35.28 |  |
| plates | 9.00 | 11.00 | 13.00 |  |
| ocean_age | 50.90 | 54.80 | 63.90 |  |
| speed | 3.01 | 4.38 | 5.09 |  |
| sea_level | -7.70 | 68.10 | 123.20 |  |
| sea_ice_m | -24.40 | -16.70 | -1.20 |  |
| sea_tect_m | 6.90 | 89.50 | 126.30 |  |
| ice_pct | 0.10 | 1.20 | 1.70 |  |
| temp | 16.50 | 20.00 | 25.20 |  |
| co2 | -1.25 | 0.20 | 0.91 |  |
| dry_pct | 20.49 | 25.83 | 34.37 |  |
| inland_pct | 1.53 | 3.66 | 8.59 | 300-500: 1.53 |
| lake_pct | 0.19 | 0.37 | 1.22 | 488-488: 0.19 |
| lake_max_mkm2 | 0.03 | 0.07 | 0.86 |  |
| max_elev_km | 3.75 | 4.79 | 8.36 |  |
| trees_pct | 6.30 | 31.74 | 53.35 | 344-356: 53.35; 492-500: 6.30 |
| npp | 211.10 | 313.80 | 421.60 |  |
| landmasses | 5.00 | 8.00 | 15.00 |  |
| largest_pct | 13.80 | 18.50 | 29.30 |  |

### Seed 212, L6 (run 1875a8)

![seed 212 L6](seed212_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.29 | 32.35 | 32.81 |  |
| cont_pct | 39.43 | 40.05 | 40.99 |  |
| cont_km | 33.39 | 33.74 | 34.49 |  |
| plates | 11.00 | 14.00 | 18.00 |  |
| ocean_age | 38.30 | 54.50 | 58.90 |  |
| speed | 3.73 | 4.35 | 4.91 |  |
| sea_level | 2.90 | 89.20 | 198.20 |  |
| sea_ice_m | -29.70 | -12.10 | -5.80 |  |
| sea_tect_m | 17.60 | 115.10 | 215.40 |  |
| ice_pct | 0.50 | 1.00 | 1.70 |  |
| temp | 12.40 | 15.40 | 19.50 |  |
| co2 | -1.13 | -0.08 | 0.72 |  |
| dry_pct | 10.79 | 22.85 | 25.03 | 312-328: 10.79 |
| inland_pct | 0.73 | 2.36 | 7.11 | 300-500: 0.73 |
| lake_pct | 0.21 | 0.37 | 1.56 |  |
| lake_max_mkm2 | 0.03 | 0.09 | 1.48 | 420-420: 1.48 |
| max_elev_km | 4.25 | 4.97 | 8.27 |  |
| trees_pct | 11.31 | 35.77 | 55.36 | 324-344: 55.36 |
| npp | 289.30 | 348.10 | 414.00 |  |
| landmasses | 6.00 | 9.00 | 12.00 |  |
| largest_pct | 10.90 | 13.10 | 24.40 |  |

### Seed 213, L6 (run 43dda4)

![seed 213 L6](seed213_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 32.78 | 33.61 | 33.84 |  |
| cont_pct | 38.58 | 39.98 | 40.46 |  |
| cont_km | 33.87 | 34.06 | 35.14 |  |
| plates | 12.00 | 15.00 | 19.00 |  |
| ocean_age | 41.50 | 46.70 | 53.90 |  |
| speed | 3.15 | 4.44 | 5.26 |  |
| sea_level | 86.70 | 137.80 | 175.70 |  |
| sea_ice_m | -42.10 | -19.50 | -7.20 |  |
| sea_tect_m | 95.60 | 162.90 | 196.30 |  |
| ice_pct | 0.60 | 1.60 | 2.70 |  |
| temp | 13.70 | 17.60 | 21.80 |  |
| co2 | -0.30 | 0.37 | 1.17 |  |
| dry_pct | 14.11 | 16.93 | 35.57 |  |
| inland_pct | 0.75 | 2.96 | 6.96 | 300-500: 0.75 |
| lake_pct | 0.16 | 0.34 | 0.93 | 320-320: 0.16 |
| lake_max_mkm2 | 0.03 | 0.05 | 0.82 |  |
| max_elev_km | 3.80 | 4.94 | 6.76 |  |
| trees_pct | 32.29 | 41.24 | 51.97 | 348-356: 51.97 |
| npp | 324.90 | 360.25 | 401.50 |  |
| landmasses | 3.00 | 6.00 | 11.00 |  |
| largest_pct | 11.80 | 20.50 | 30.70 |  |

### Seed 214, L6 (run b05e14)

![seed 214 L6](seed214_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.29 | 32.66 | 34.33 |  |
| cont_pct | 38.70 | 40.28 | 41.71 |  |
| cont_km | 32.48 | 33.30 | 34.35 |  |
| plates | 9.00 | 11.00 | 14.00 |  |
| ocean_age | 42.30 | 56.20 | 64.60 |  |
| speed | 3.48 | 4.44 | 5.11 |  |
| sea_level | -111.60 | 42.90 | 178.30 |  |
| sea_ice_m | -42.80 | -4.20 | -0.00 |  |
| sea_tect_m | -102.80 | 61.20 | 179.90 |  |
| ice_pct | 0.00 | 0.30 | 2.10 |  |
| temp | 13.00 | 16.80 | 21.20 |  |
| co2 | -1.27 | 0.38 | 2.23 |  |
| dry_pct | 20.55 | 24.22 | 37.76 |  |
| inland_pct | 0.88 | 2.99 | 8.67 | 304-500: 0.88 |
| lake_pct | 0.22 | 0.35 | 0.72 |  |
| lake_max_mkm2 | 0.03 | 0.07 | 0.34 |  |
| max_elev_km | 3.74 | 5.21 | 8.39 |  |
| trees_pct | 5.71 | 34.09 | 40.55 | 464-500: 5.71 |
| npp | 267.20 | 355.60 | 397.90 |  |
| landmasses | 4.00 | 6.00 | 12.00 |  |
| largest_pct | 14.60 | 17.30 | 30.40 |  |

### Seed 215, L6 (run c47f22)

![seed 215 L6](seed215_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.50 | 33.70 | 34.28 |  |
| cont_pct | 40.17 | 40.53 | 40.96 |  |
| cont_km | 33.22 | 33.68 | 34.28 |  |
| plates | 6.00 | 9.00 | 15.00 |  |
| ocean_age | 45.60 | 64.60 | 79.00 |  |
| speed | 2.85 | 4.04 | 4.68 |  |
| sea_level | -286.20 | -57.40 | 106.30 | 416-444: -286.20 |
| sea_ice_m | -190.00 | -18.90 | -6.90 |  |
| sea_tect_m | -171.90 | -24.10 | 113.60 |  |
| ice_pct | 0.60 | 1.40 | 5.70 |  |
| temp | 8.50 | 13.90 | 19.30 |  |
| co2 | -1.15 | -0.39 | 0.49 |  |
| dry_pct | 20.03 | 23.97 | 30.26 |  |
| inland_pct | 0.52 | 3.44 | 12.57 | 300-300: 7.95; 312-496: 0.52 |
| lake_pct | 0.21 | 0.39 | 1.45 |  |
| lake_max_mkm2 | 0.04 | 0.09 | 1.94 | 316-316: 1.20; 416-432: 1.94 |
| max_elev_km | 4.23 | 5.41 | 8.28 |  |
| trees_pct | 16.87 | 34.53 | 49.71 |  |
| npp | 168.70 | 308.40 | 473.40 | 404-404: 168.70 |
| landmasses | 5.00 | 8.00 | 12.00 |  |
| largest_pct | 9.50 | 22.10 | 27.00 |  |

### Seed 216, L6 (run f0ffe0)

![seed 216 L6](seed216_L6.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 33.83 | 34.24 | 34.72 |  |
| cont_pct | 39.95 | 40.92 | 41.70 |  |
| cont_km | 32.55 | 33.23 | 34.23 |  |
| plates | 10.00 | 11.00 | 14.00 |  |
| ocean_age | 42.60 | 53.80 | 70.80 |  |
| speed | 3.65 | 4.32 | 4.58 |  |
| sea_level | -46.20 | 124.60 | 206.50 |  |
| sea_ice_m | -4.30 | -0.70 | -0.00 |  |
| sea_tect_m | -42.60 | 124.60 | 206.50 |  |
| ice_pct | 0.00 | 0.00 | 0.30 |  |
| temp | 15.90 | 18.70 | 21.50 |  |
| co2 | 0.06 | 0.72 | 0.95 |  |
| dry_pct | 14.10 | 22.28 | 35.63 |  |
| inland_pct | 1.24 | 3.34 | 12.29 | 300-500: 1.24 |
| lake_pct | 0.13 | 0.32 | 1.96 | 376-376: 0.18; 392-400: 0.13; 412-420: 0.16; 436-440: 0.15; +1 more |
| lake_max_mkm2 | 0.03 | 0.06 | 2.89 | 340-340: 2.89; 444-448: 1.58 |
| max_elev_km | 3.06 | 4.07 | 8.29 |  |
| trees_pct | 37.72 | 42.75 | 51.61 | 484-500: 51.61 |
| npp | 234.80 | 378.10 | 409.10 |  |
| landmasses | 1.00 | 8.00 | 12.00 | 300-304: 1 |
| largest_pct | 17.10 | 24.10 | 34.30 |  |

## Determinism

(not run)
