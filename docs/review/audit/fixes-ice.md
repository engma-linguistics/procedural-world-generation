# Audit fixes: ice and the glacial time zoom (PW-274..277)

Branch `worktree-agent-a7ab2c7787d86d6e5`. One commit per ticket. Before = main at the audit (the baselines in
`docs/review/baseline-2026-10-15/`, or the same probe on main's code); after = this branch.

## What changed
- **PW-274** `finish.orbit_dt`: land = bed + ice > 0 (the time zoom's mask). Test: orbit_dt equals the time zoom's
  anomaly on that mask.
- **PW-276** `earth.sheet_surface`: a sheet's surface is the least, over its margin cells, of their bed plus the
  Nye rise at the hop distance from them (Bellman-Ford through the sheet); ice = surface - bed, at least a
  margin's. The nearest-margin version from the audit was tried first: it still gave 9.4-10 km surfaces where a
  margin sits on a 7 km ridge above a basin (L5 seed 2), so the ice drains to the margin that keeps it lowest.
  Test: raising the bed inside a sheet by 3 km thins the ice there. `test_values_sane` back to -95 C.
- **PW-275** (lean B): the time zoom damps the summer only on ice (`ice_g > 1`); bare ground's lying snow gets
  none, as the run's new-cap test and the zoom's glaciers already did. LOCAL is a floor on ice only.
- **PW-277**: `climate.ice_surface` is now icemass's own year (`icemass.surface`, mean orbit; annual mean keeps
  the ground's offset), used by climate.compute, the run's keyframes, `ice_sheets`' softness and the zoom's
  glaciers. `zoom.ice_ground` inverts it (`icemass.ground_from_surface`, bisection: the surface's coldest month
  depends only on the ground's coldest, its warmest monotonically on both). No new constants. Small edits in
  other areas: `climate.compute` (the cover it passes), `zoom.py` (ice_ground, pixel glaciers), `update_climate`.

## Before / after

Run ice, per climate update (probe: every `update_climate`), L5, 1000 Myr:

| | seed 2 before | seed 2 after | seed 11 before | seed 11 after |
|---|---|---|---|---|
| sea level from ice, mean / min (m) | -66 / -371 | -43 / -169 | -32 / -340 | -41 / -393 |
| updates below -150 m | 18% | 5% | 9% | 11% |
| highest iced surface (km) | 9.7 | 9.2 (an 8.8 km peak + margin ice) | 9.9 | 8.4 |
| max ice thickness on > 5 km bed | ~2.2 km | margin (~350 m) | | |
| coldest month min (C) / cells < -90 C | -107.5 / 25 | -93.5 / 1 | -123.4 / 27 | -97.4 / 8 |

L4 seed 1 (the test run) -52 -> -71 C at worst over the run, -47 -> -55 C at its end; L4 seed 4 -116 -> -98 C.

`tools/health.py --quick` (8 L6 seeds, 500 Myr; `docs/review/health-ice/`), sea level from ice:

| seed | 1 | 2 | 11 | 21 | 3199 | 42 | 77 | 505 |
|---|---|---|---|---|---|---|---|---|
| min, before (m) | -112 | -174 | -360 | -72 | -129 | -304 | -99 | -128 |
| min, after (m) | -58 | -115 | -247 | -32 | -84 | -124 | -127 | -52 |
| frames < -150 m, before / after | 0 / 0 | 5.6 / 0 | 13.5 / 8.7 | 0 / 0 | 0 / 0 | 11.9 / 0 | 0 / 0 | 0 / 0 |

Earth L6 with its real ice, model vs NCEP (`climate.compute`; tools/earth_check could not run here: the Kottek
file is not cached and its server refused the download):

| | coldest month bias before | after | warmest month bias before | after |
|---|---|---|---|---|
| Antarctica (1095 cells) | -10.1 C (rmse 12.4) | -1.7 C (7.4) | +4.8 C (5.8) | +6.3 C (7.7) |
| Greenland (133) | -20.9 (21.3) | -14.1 (14.5) | -5.2 (5.6) | -4.0 (4.7) |
| ice-free land | unchanged | | | |

`tools/earth_check.py` against the coordinator's baseline (only these lines changed; Köppen unchanged, both
sheets EF): Antarctica annual / coldest / warmest -32.8 / -56.3 / -9.5 -> -26.7 / -47.9 / -8.1 C (obs -35.6 /
-47.6 / -14.9): the coldest month now right, but the annual mean +8.9 C too warm (was +2.8). Greenland -32.2 /
-54.4 / -10.1 -> -27.5 / -48.0 / -9.2 (obs -21.4 / -33.0 / -5.0). Vostok annual -41.5 -> -35.5 (obs -50.6),
Summit -37.7 -> -32.6 (obs -26.8). Global mean T 14.5 -> 14.7 C. The 10 C was compensating a too-warm polar
base (PW-112, PW-039: East Antarctica ~10 C too warm); without it that bias shows on Antarctica's annual mean.

Antarctic summers get warmer by ~1.5 C (the 10 C cut no longer hides PW-112's warm polar base); winters much
closer to observed.

Time zoom drift (150 kyr from 5 keyframes each of L5 seeds 2 and 11): median -94 m -> -53 m, worst -195 -> -312
m (draft `timezoom-drift-tail`). PW-275 alone, on the same moments: 0 to +6 m (small). Earth's 150 kyr time zoom:
-100 m -> -38 m (PW-275: Earth glaciates less, as the ticket expected; PW-033).

`tools/scorecard.py` (seeds 1, 2 at 1000 Myr; end states are chaotic, so only a sanity check): seed 1 ice 0.0 ->
1.1%, dry 32.0 -> 20.0%; seed 2 ice 3.6 -> 4.3%, dry 37.2 -> 30.4%; Earth Köppen group agreement 72% -> 71.8%.
(Not appended to docs/scorecard.jsonl, to keep the branches mergeable.)

No retunes.
