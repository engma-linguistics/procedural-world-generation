# PW-293 (sea level re-centred) and PW-309 (stats land = frame land)

Branch `worktree-agent-a637524a2470475ad`, on main 10ac1a4 (PW-308's glaciation fix included). Owner decision 2026-10-15: A+B.

## What changed
- **(B) The start is the model's own steady ocean** (`tectonics/setup.py`, `OCEAN_MAX_AGE`). Setup still lays a steady-state age distribution (floor made at a steady rate, subducted at any age up to a maximum: p(a) ~ 1 - a/max, mean max/3), but with max 144 Myr (mean 48) instead of 180 (mean 60). Sea level 0 is the starting floor's mean depth (`earth.global_temperature`), so it is now the model's own mean depth, and excursions are breakups and assemblies.
- **Ranked over the ocean's cells only.** The ages were ranked over all cells and the continent then took a patchy share, so the starting ocean's mean age ran 55-65 Myr by seed (8 L6 seeds). That shifted each run's whole sea-level record by up to ~±70 m. Every seed now starts at the same mean depth (48.0 Myr at setup, 50.0-50.8 in the first keyframe after one step).
- **(A) `SEA_TECT_MAX` 250 -> 400 m.** A +250 m Cretaceous-like basin term now passes at +222 m (was +190). The limiter only stops runaways.
- **PW-309** (`Simulation.bed()`): the frame's trench term on oceanic crust is now inside `bed()`, which only `land()` and the frame outputs read. So `sim.land()`, `stats()["land_pct"]`, the frame's Köppen, vegetation and rivers, and the frame's elevation all agree. The long-term processes use `w_elev` and are unchanged.
- `tools/sealevel.py` reads the limit from `earth.SEA_TECT_MAX`.

## How the start age is set (measured, not derived)
I looked first for a derivation from the model's spreading. A steady triangular ocean has mean age 2A/(3P), with A the ocean area and P its production; Earth's numbers give 63 Myr. But setup can't give P. Its plate speeds are random draws (2-6 cm/yr) that the force balance replaces within ~15 Myr. Its boundaries are a random partition, not a ridge system. The model's steady speed (4.5 cm/yr) and ridge length emerge from slab pull, slab drag and the plate count. So the constant comes from measurement: health --quick on the branch point (8 L6 seeds x 500 Myr, frames after 50 Myr).
- The model's mean ocean depth is -4802 m (median -4767). Its mean age is 52.0 Myr (median 49.1); per-seed means run 45-62.
- A triangular start with mean age 48 Myr has mean depth -4805 m; one with 50 Myr has -4848 m. The model's ocean is a little older for the same depth because its ages spread wider (depth ~ sqrt(age) is concave).
- The match is on depth, the quantity sea level reads. After the change the model's ocean is still at -4806 m mean (age 51.4 mean): the start didn't move its steady state.
- Residual: the reference is read after the first 2 Myr step (age 50, depth ~-4870 m), so the expected mean basin term is ~+40 m before the tanh and ice. The seed-to-seed spread (±130 m of floor depth, ±90 m of sea) is larger than that.

## Before / after
`tools/health.py --quick --no-determinism --workers 8 --threads 1`: before `docs/review/health-pw293-before/` (10ac1a4), after `docs/review/health-pw293-after/`. All keyframes after 50 Myr pooled, median (p5..p95):

| metric | before | after |
|---|---|---|
| sea level m | +148 (-137..+226) | **+15 (-155..+191)** |
| sea level m, max / min of any frame | +235 / -182 | +216 / -370 |
| per-seed medians of sea level | 0..+208 (7 of 8 above +100) | -53..+124 (1 of 8 above +50) |
| sea level m, 50-100 Myr (first breakup) | +135 (-13..+216) | +54 (-68..+184) |
| sea from ice m | -1.5 (-19.5..0) | -3.9 (-22.3..0) |
| land % | 33.4 (30.9..37.0) | 33.5 (31.3..37.4) |
| land % at start / 0-100 Myr | 39.6 / 38.4 | 39.6 / 38.7 |
| continental crust % | 39.0 (37.0..42.9) | 39.3 (37.3..42.7) |
| continental thickness km | 35.6 (34.1..38.4) | 35.2 (34.0..37.5) |
| ocean age Myr | 49.2 (35.8..79.5) | 51.6 (35.1..65.8) |
| ocean age at start (first frame) | 56.8 (53.0..63.0) | 48.0 (48.0..48.0) (setup; 50.0-50.8 after one step) |
| plate speed cm/yr | 4.5 (2.9..7.3) | 4.5 (3.2..7.1) |
| plates | 13 (7..17) | 12 (7..17) |
| ice % of surface | 0.3 (0..2.3) | 0.7 (0..3.0) |
| global T C | 15.2 (9.7..20.0) | 14.9 (9.2..20.1) |
| arid % of land | 28.5 (16.0..47.2) | 28.5 (18.5..46.2) |
| inland drainage % | 5.5 (1.6..17.1) | 5.2 (1.6..14.8) |
| highest peak km | 6.2 (2.2..7.3) | 5.8 (2.1..7.8) |
| icehouse spells (ice SL < -50 m, gaps <= 5 frames) | 1 (seed 2) | 3 (seeds 1, 2, 11) |
| deepest ice sea level per seed m | -94 (s2); others -5..-33 | -264 (s11), -57 (s1), -53 (s2); others -12..-41 |
| giant-lake frames, mean per run | 5.2% | **9.6%** |
| outlier spells | 148 | 173 |

The outlier spells by metric, before -> after: lake_max 34 -> 40, giant_lake_frames 2 -> 6 runs, inland 40 -> 44, trees 1 -> 5, volume_ratio 3 -> 5 runs (0.887-0.927 both times), sea_level 0 -> 2 and sea_ice_m 0 -> 1 (both seed 11's icehouse), lake_pct 38 -> 37, the rest the same.

Scorecard (`tools/scorecard.py --jobs 3 --threads 2`, L6 seeds 1 / 2, 1 Gyr). The branch point was run from an exported copy (10ac1a4, no row on main). Its Earth climate was skipped (no `data/` in the worktree; the climate is untouched):

| | 10ac1a4 | 15a8cac |
|---|---|---|
| land at 1 Gyr % | 31.2 / 31.6 | 34.2 / 33.6 |
| land, median of the 100 Myr track % | 31.6 / 31.4 | 32.3 / 33.0 |
| land range % | 30.2-35.8 / 29.2-35.0 | 29.9-35.0 / 31.2-35.5 |
| crust % | 40.7 / 43.0 | 42.4 / 41.7 |
| volume end/start | 0.89 / 0.918 | 0.936 / 0.917 |
| ocean age Myr | 62.2 / 66.4 | 74.2 / 65.6 |
| dry % (final) | 27.3 / 16.4 | 17.6 / 16.1 |
| ice % (final) | 0.7 / 1.6 | 0.8 / 2.2 |
| tree cover % | 24.1 / 28.5 | 37.5 / 35.0 |

## Reading it
- **The sea is centred.** The median went from +148 to +15 m, and 7 of 8 seeds now have medians within ±55 m (seed 2: +124). Excursions remain: the first breakup's young ocean gives a +100..+200 m highstand at ~50-100 Myr (before: +135 m median there, partly the offset). Assemblies with old oceans give lows of -100..-150 m. The p95 fell only from +226 to +191 because the wider limiter lets the high end through.
- **Land hardly moved** (+0.1 point at 500 Myr, +0.6 / +1.5 on the 1 Gyr scorecard track) although the sea is ~130 m lower. Weathering and erosion work toward the sea (a 200 m base level) and the crust thermostats hold area and volume, so the land relevels to the sea within ~100 Myr. Peaks are a little lower (median 6.2 -> 5.8 km).
- **Glaciation is not broken.** It has more spells in 500 Myr (3 vs 1); PW-308's 5 of 8 seeds was over 1 Gyr. Seed 11's 180-232 Myr cold era (global 3.5 C) is the one PW-308 measured at -322 m. With the +140 m offset gone, the total sea there reaches -370 m (ice -264, basins ~-105), below the health envelope's -250 m (inbox draft).
- **What got worse:** giant lakes. The share of frames whose biggest lake is over 1 Mkm2 rose from 5.2 to 9.6% per run, while the lake share of land stayed at 0.5%. Likely mechanism: low interiors that a +150 m sea flooded are now dry closed basins. That is evidence for PW-300, which owns them (inbox draft).
- **The start doesn't depend on 60 Myr elsewhere.** Land share at the start is the same (39.6%). Isostasy at the start only changes the ocean floor (shallower by ~190 m mean). Continental rock ages are untouched. Passive margins older than 120 Myr (`margin_age`, subduction start) are rarer at the start (2.8% of floor vs 11%; not checked event by event), yet plate counts and speeds over the first 100 Myr are the same. Plate speed over 0-100 Myr is unchanged (5.7 cm/yr). The PW-053 history (a start far from steady renews itself and moves the sea) still holds: the start is a steady state, just the model's.
- **PW-309:** on main, the L4 300 Myr test sim had no such cells. The test now builds the case on a copy (an oceanic cell at +10 m bed with a 300 m trench is sea in both).

## Tests and goldens
- `tests/test_sea_level.py`: the starting ocean's mean age is OCEAN_MAX_AGE / 3 on 3 seeds. The basin term starts at 0 and averages within ±50 m over 300 Myr on L4 seeds 1-3, each within ±120 m (the old start: +74..+102 per seed).
- `tests/test_health.py`: the run's land equals the frame's land, including the PW-309 trench case.
- Golden `tests/golden/sim_L4_s1_60myr.json` regenerated (the start ages change every run).
- `tests/test_parallel.py::test_jobs_in_worker_processes_match_sequential` failed once in the full suite and passed alone (known flaky, PW-303).

## Inbox drafts
- `draft-giant-lakes-lower-sea.md`: the giant-lake rise above, for PW-300.
- `draft-icehouse-sea-below-envelope.md`: seed 11's -370 m icehouse total.
- `draft-scattered-start-ocean-ages.md`: with `start=scattered` the ocean barely renews in the first 100 Myr (L5: 48 -> 58-93 Myr, basin sea -54..-182 m on average). The behaviour predates this change (old start 60 -> 77-108).
