# Audit fixes: tectonics (PW-285, 287, 288, 284, 286; PW-172)

Branch `worktree-agent-a58543b41e5117cc6`. Baselines: `docs/review/baseline-2026-10-15/` (main 58a12c0).
After: `docs/review/health-tectonics/` (health --quick, 8 L6 seeds x 500 Myr) and the scorecard row for 258e77a.

## What changed
- **PW-285** (`isostasy._k`, `iso_rate`): sediment on hotspot rock floats at K_SEA; `iso_rate` takes the thickness and gives ISO_SEA past VOLCANO_PILE_KM (matches `elevation`'s slope; test).
- **PW-172** (`crust.stretch`): the 10.6 km one-frame L7 peaks were not hotspots. They were 80 km collision-belt cells next to an opening edge. These were stretched and dated as rifting every step while stacking rebuilt them, so their strain reached beta 6-9 and the McKenzie hot uplift lifted whole belt stretches ~2 km (to 9-10 km). Crust being stacked this step is no longer stretched. Replays: a1d3b9 900-950 Myr max 10.0 -> 8.6 km; 550a5a 100-156 Myr max 8.5 km.
- **PW-287** (`crust.flanks`): the rift pool's decay goes back into the plate's recently rifted continent (booked "rift flanks"), not deleted.
- **PW-288** (`earth.global_temperature`, `motion.forces`): basin term against the fixed starting floor, factor (rho_m - rho_w)/rho_m = 0.69. Process cause of the young ocean: production was ~2x Earth's (6.6 km2/yr at L5, Earth ~3.3), mostly from spreading speed. Slab pull had no velocity-dependent resistance. New `slab_drag` = 0.1 per cm/yr is Stokes resistance to the sinking slab: an 80 Myr slab alone sinks at a terminal 10 cm/yr (Earth's fastest slab-attached plates are 8-10 cm/yr). Mantle traction was checked and moves mostly continents: turning it off left ocean age unchanged.
- **PW-286** (`crust.rifted_margin`): margin thickness depends on the pool only (12-18 km), not on `shrink`.
- **PW-284: not landed.** Full two-sided flexure (share 1, volume kept) lifts grid-scale 80 km crust spikes almost by their whole root: L7 replays reached 14 km (FLEX_KM 150 or 75) and 10.4 km (50). L6 seed 1 reached a mean max elevation of 40 km. See `issue-tracking/inbox/draft-tect-flexure-needs-smooth-crust.md`.

## Before / after
health --quick, all keyframes after 50 Myr pooled (median, p5-p95):

| metric | before (58a12c0) | after (258e77a) |
|---|---|---|
| land % | 31.6 (29.7-37.3) | 32.8 (30.6-37.1) |
| continental crust % | 38.7 (36.7-42.3) | 39.2 (37.2-43.1) |
| continental thickness km | 35.2 (33.9-37.5) | 35.3 (33.8-37.7) |
| crust volume end/start (per seed) | 0.873-0.907 | 0.879-0.926 |
| plates | 12 (8-16) | 13 (8-17) |
| ocean age Myr | 38.2 (23.8-57.3) | 50.3 (35.7-69.1) |
| plate speed cm/yr | 6.2 (4.2-10.2) | 4.5 (3.2-7.2) |
| sea level m | +34 (-228..+189) | +141 (-75..+221) |
| inland drainage % | 10.6 (4.2-25.4) | 9.2 (3.3-22.1) |
| highest peak km (max) | 9.3 | 8.4 |
| arid % of land | 35.5 | 37.5 |

Scorecard (L6, 1 Gyr), seed 1 / seed 2: land 32.6/32.1 -> 31.0/31.9%; crust 43.3/43.1 -> 42.7/40.6%; volume x0.936/0.955 -> x0.911/0.927; ocean age 73.6/41.5 -> 66.9/75.4 Myr; dry 32.0/37.2 -> 27.3/35.9%. Earth climate unchanged (71.8%).

## Notes
- The sea now sits ~+140 m on average. The model's steady ocean (~50 Myr) is younger than the starting reference (60 Myr), and the +-250 m tanh limiter shapes it softly. Inbox draft `draft-tect-sea-ref-older-than-steady-state.md`.
- The land share did not drop: slower plates also changed the crust and relief, and the thermostats hold area and volume.
- No other knob was retuned. `slab_drag` is a new process term; its value comes from a terminal slab speed, not from an ocean-age fit, but the 0.07-0.15 sweep (L5) shows ocean age is sensitive to it (48-68 Myr).
- PW-051: ocean age now 36-69 Myr (p5-p95), never near the old-ocean clip. It's closable from the old-ocean side.
