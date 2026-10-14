# Overnight runs (2026-10-14)

All runs use main after the mantle merge (a2eb9fa): breakup fix, B′ mantle, lighter sediment, ocean overturning, lakes, store format.

## Resolution check: seed 1, level 6 (98adcb) vs level 7 (1beb32), 1500 Myr
- **Run time:** L6 553 s; L7 2621 s (~29 min/Gyr while sharing the machine with 3–4 other jobs).
- **Overall:** behaviour is broadly resolution-independent.

| | L6 | L7 |
|---|---|---|
| Land after 300 Myr, median | 34.7% | 36.8% |
| Frames with one landmass > 25% of the surface | 8% | 10% |
| Landmasses > 0.5%, median | 5 | 5 |
| Plates, median | 7 | 5 |

- **Same rhythm:** an early reassembly around 200 Myr and another around 500–600 Myr in both.
- **Per-frame (every 100 Myr):** land 26–40% in both. Big swings (e.g. 27% at 700 in L6) are sea-level/assembly events, not drift.
- **Concern (both levels):** plate counts drop to 2–3 around 500–700 Myr, while Earth has ~7 major plus ~8 minor plates. Showcases also end with 4 plates (2b59b1, 9219ac). Logged in Known issues.
- **Ocean age not compared:** my quick metric (crust age of all cells deeper than −1000 m) also counted submerged continental crust, so it isn't comparable. The scorecard's ocean age (oceanic crust only) was 72–81 Myr at L6 in the mantle agent's runs.

## Level-7 sudden land losses
Level-7 runs show sudden land losses of 7–19 points in ~8 Myr, which level 6 doesn't:

| Run | Land |
|---|---|
| eef4a2 (seed 13 water world) | 33% → 14% over 1488–1500 Myr |
| 1beb32 (seed 1) | 37→26% at ~900, 40→28% at ~1266, 41→22% at ~1400 |
| f3f4ac (seed 16) | 33→23% at ~930, recovered by 952 |
| 0e4c66 (seed 11) | 36→29% at 784 |

The amount of continental crust doesn't change; the continents sink (median continental elevation +95 → −243 m in eef4a2). The `l7jumps` agent is investigating. The L8 run may show the same thing. eef4a2's 1496 Myr world (06bc3f) is caught mid-drop; the 1400 Myr world is the better look.

**Cause (the `l7jumps` agent, merged at 05:20).** A modelling artifact. Every fast sea-level rise, at L6 too, followed an "old ocean floor breaks off its continental margin" event. That event broke off the plate's **whole** ocean as one new plate. This left hundreds of island "holes" ringed by trenches, and the plate raced at the 18 cm/yr cap. Half of every coastline opened as a ridge, so the ocean floor renewed itself in about 10 Myr and sea level rose about 400 m. L7 suffers more because it has about 3× as many small continental specks (holes) and continents about 300 m lower.

**Fix:** break off one basin, along 6000 km of the oldest passive margin. Largest land drop per 8 Myr, before → after:

| Window | Before | After |
|---|---|---|
| eef4a2 | 15.4 points | 4.3 points |
| 1beb32 | 11.5 points | 0.7 points |
| f3f4ac | 9–17 points | 3.9 points |

On L6 the largest 8-Myr sea rise goes from 176 m to 111 m. Plots: `docs/review/before_after_L7.png` and `docs/review/map_1496.png`.

**Verification runs** on the final code, L7, 1500 Myr: seed 1 (compare 1beb32) and seed 13 (compare eef4a2).

## Level 8: 15b1b0 (seed 1, 1200 Myr, made before the plate and land-drop fixes)
- **Cost:** 14,876 s (4.1 h, sharing the machine with 2–3 other jobs), 3.9 GB on disk with `--every 10` and checkpoints every 300 Myr.
- **Highlights:** about 8.5 min for the world plus 5 zooms. World **aa1864** at 800 Myr.

Against L7 (1beb32, same seed and code), after 300 Myr:

| | L7 | L8 |
|---|---|---|
| Land median | 36.8% | 36.9% |
| Landmasses > 0.5%, median | 5 | 6 |
| Plates, median | 5 | 8 |
| Frames with one landmass > 25% | 10% | 3% |

The sudden land drops occur at L8 too (e.g. 43→33% at 890, 38→24% at 940), as expected before the fix.

## Final code (after mantle c8a06d2 and l7jumps)
- **L6 showcases re-made:**

  | Run | Showcase | Plates at end | Land |
  |---|---|---|---|
  | 01b0f7 | Earth-like A | 7 | 37.8% |
  | 796a25 | Earth-like B | 6 | 36.9% |
  | f0a1b0 | Water world | 7 | 32.5% |
  | 07fb28 | Land-heavy | 7 | 53.6% |
  | 9abc92 | Cold | 4 | 38.1% |
  | 19385e | Hothouse | 8 | 33.9% |

  Plate counts are mostly back up from 2–4.
- **Fast land changes are rarer but not gone.**
  - L7 seed 1 (fe7144) still drops 40→30% at ~1140 and recovers 26→34% by 1172.
  - L6 seed 12 (796a25) drops 37→30% at 1320 and recovers to 34% by 1364.
  - L6 seed 14 drops 55→49% at 716.
  - Before the fix there were 3–4 such events per L7 run; now there are 1–2, and some are recoveries (fast sea-level falls).
- **Logged in Known issues:** the cause is probably the same ridge-age to sea-level link (any big reorganisation renews ocean floor quickly), together with the low L7 continents.
