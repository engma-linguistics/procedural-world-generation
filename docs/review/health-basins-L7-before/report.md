# Health sweep 2026-10-16 04:09

Commit None. 1 runs (default params, `--every 4`) at 1 workers x 4 numba threads; simulations 11.6 min wall. Made by `tools/health.py` (PW-246).

## Runs

| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3199 | 7 | 500 | e4e270 | 693 | 132 / 376 | 9.4 | 0 | 1.8 | 0.898 | 0.0 | 0.0 |

## Medians by seed (after 50 Myr; tree cover after forests, NPP after flowering trees appear)

| seed | L | land_pct | cont_pct | cont_km | plates | ocean_age | speed | sea_level | sea_ice_m | ice_pct | temp | co2 | dry_pct | inland_pct | lake_pct | lake_max_mkm2 | max_elev_km | trees_pct | npp | landmasses | largest_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3199 | 7 | 34.7 | 38.0 | 37.1 | 14.0 | 44.5 | 5.0 | 115.2 | -1.6 | 0.3 | 15.3 | -0.2 | 33.6 | 8.3 | 1.0 | 0.2 | 6.8 | 26.0 | 315.5 | 12.0 | 22.9 |

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
| land ice, % of surface (`ice_pct`) | - | 10 | 3.10 | Earth 3.1% now (earth.EARTH_ICE), ~7-8% at the LGM |
| global mean temperature, C (`temp`) | 8 | 30 | 14.50 | Earth 14.5 C; LGM ~8 C (Tierney et al. 2020); Phanerozoic hothouses to ~30 C (Scotese et al. 2021) |
| CO2 index (ln source/sink) (`co2`) | -1.5 | 1.5 | 0.00 | the forcing's clip in earth.py (+-1.5); Earth 0 |
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

## Top outliers (of 20 spells; severity = excess / band width x (0.2 + share of the run))

| seed | L | metric | Myr | frames | worst | envelope | severity |
|---|---|---|---|---|---|---|---|
| 3199 | 7 | lake_max_mkm2 | 220-220 | 1 | 2.39 | -..1.0 | 0.289 |
| 3199 | 7 | lake_max_mkm2 | 104-104 | 1 | 2.25 | -..1.0 | 0.261 |
| 3199 | 7 | dry_pct | 52-140 | 23 | 57.52 | 12..45 | 0.145 |
| 3199 | 7 | inland_pct | 324-412 | 21 | 2.62 | 8..30 | 0.09 |
| 3199 | 7 | inland_pct | 144-168 | 5 | 3.25 | 8..30 | 0.052 |
| 3199 | 7 | inland_pct | 92-132 | 9 | 3.94 | 8..30 | 0.05 |
| 3199 | 7 | inland_pct | 424-452 | 6 | 4.45 | 8..30 | 0.04 |
| 3199 | 7 | inland_pct | 468-476 | 3 | 4.30 | 8..30 | 0.038 |
| 3199 | 7 | inland_pct | 228-252 | 5 | 4.94 | 8..30 | 0.033 |
| 3199 | 7 | lake_pct | 220-220 | 1 | 3.41 | 0.2..3.0 | 0.031 |
| 3199 | 7 | inland_pct | 264-264 | 1 | 5.62 | 8..30 | 0.022 |
| 3199 | 7 | inland_pct | 276-288 | 3 | 6.03 | 8..30 | 0.02 |
| 3199 | 7 | inland_pct | 308-312 | 2 | 6.66 | 8..30 | 0.013 |
| 3199 | 7 | largest_pct | 160-160 | 1 | 36.10 | 5..35 | 0.008 |
| 3199 | 7 | largest_pct | 172-208 | 9 | 35.80 | 5..35 | 0.007 |
| 3199 | 7 | inland_pct | 500-500 | 1 | 7.56 | 8..30 | 0.004 |
| 3199 | 7 | inland_pct | 212-212 | 1 | 30.30 | 8..30 | 0.003 |
| 3199 | 7 | landmasses | 64-64 | 1 | 2 | 3..80 | 0.003 |
| 3199 | 7 | lake_pct | 144-144 | 1 | 0.17 | 0.2..3.0 | 0.002 |
| 3199 | 7 | volume_ratio | run | - | 0.90 | 0.9..1.1 | 0.002 |

## Per seed: min / median / max after the 50 Myr spin-up, and spells outside the envelopes

### Seed 3199, L7 (run e4e270)

![seed 3199 L7](seed3199_L7.png)

*At 48, 200, 348, 500 Myr: sea by depth, land green by tree cover / tan where arid, shaded by height, ice white, lakes blue.*

| metric | min | median | max | outside (Myr: worst) |
|---|---|---|---|---|
| land_pct | 31.90 | 34.67 | 38.75 |  |
| cont_pct | 35.85 | 38.02 | 41.80 |  |
| cont_km | 35.53 | 37.07 | 37.79 |  |
| plates | 9.00 | 14.00 | 18.00 |  |
| ocean_age | 34.40 | 44.50 | 63.10 |  |
| speed | 2.81 | 4.95 | 7.10 |  |
| sea_level | -91.10 | 115.20 | 210.70 |  |
| sea_ice_m | -11.00 | -1.60 | -0.00 |  |
| ice_pct | 0.00 | 0.30 | 2.30 |  |
| temp | 11.40 | 15.30 | 20.80 |  |
| co2 | -0.48 | -0.17 | 0.35 |  |
| dry_pct | 18.55 | 33.65 | 57.52 | 52-140: 57.52 |
| inland_pct | 2.62 | 8.30 | 31.90 | 92-132: 3.94; 144-168: 3.25; 212-212: 30.30; 228-252: 4.94; +7 more |
| lake_pct | 0.17 | 1.03 | 3.41 | 144-144: 0.17; 220-220: 3.41 |
| lake_max_mkm2 | 0.03 | 0.24 | 2.39 | 104-104: 2.25; 220-220: 2.39 |
| max_elev_km | 2.42 | 6.81 | 8.64 |  |
| trees_pct | 11.78 | 26.04 | 39.33 |  |
| npp | 265.30 | 315.50 | 357.10 |  |
| landmasses | 2.00 | 12.00 | 20.00 | 64-64: 2 |
| largest_pct | 11.10 | 22.90 | 36.10 | 160-160: 36.10; 172-208: 35.80 |

## Determinism

(not run)
