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
