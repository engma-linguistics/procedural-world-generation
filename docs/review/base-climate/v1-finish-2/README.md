# v1-finish-2: the physics lane's last v1 steps (2026-10-24)

Branch `worktree-agent-a88a4faf3662fcb21`, from main 2fef240 (main merged again at 2ac35b4 before the showcase; no
run-physics change came in). Scripts here; tables in `step1/`, `step2/`; raw ice_diag runs in the session
scratchpad `v1f2/` (`main`: 16 seeds, `rr_p`: the same 16 at climate_offset +0.001, `preset_*`: the recipes).
CPU: at most ~22 cores (diag runs 8 at 2 numba threads, pytest `-n 4`, showcase 4 makes at 5 threads).

## Step 1: PW-708, why late history runs icier (decision: B, accept)

**Measurement** (`relief.py` = thermostat-1024's `srcsplit.py` plus the land's bed height, runoff, erosion on bare
land and mantle heat, read only; `trend.py` window means 600-1000 minus 300-500 Myr; `bins.py` per 100 Myr medians
over seeds). At steady state 0.4 ln X = ln(src/ref) - ln(sink/ref), and the sink is supply x temperature factor
x plant factor, so the CO2 change splits into forcings (source, supply, plants) and the thermostat's answer (the
temperature factor). Medians over the 10 thermostat seeds, then 16 seeds on two draws (`step2/trend_*.txt`):

| late - early | dT | drift | CO2 term | ice albedo | 0.4 dln X | ln source | ln supply | ln plants | ln temp |
|---|---|---|---|---|---|---|---|---|---|
| v1-finish's 10 (bal_tree) | -1.53 | +1.77 | -2.14 | -0.42 | -0.20 | -0.04 | **+0.17** | **+0.04** | -0.05 |
| 16 seeds, draw 1 (main) | -0.91 | +1.77 | -2.94 | -0.22 | -0.28 | -0.01 | **+0.18** | **+0.03** | -0.01 |
| 16 seeds, draw 2 (+0.001) | +0.02 | +1.17 | -0.92 | -0.28 | -0.09 | +0.11 | **+0.11** | **+0.05** | +0.00 |

(The `main` / `rr_p` runs used `relief.py` before its import order was fixed: numpy came before `planet`, so
OpenBLAS ran multi-threaded, which changes the bits (docs/coordination.md, PW-260). They are draws of main's
physics, not bit-copies of plain `ice_diag` runs: seed 1 parts from the plain run at one ULP by 12 Myr. Fixed
since; a plain and a `relief.py` run now agree bit for bit.)

What it is:
- **Not the source.** The mantle heat is constant in default runs (`heat_start` = 1.0, so `heat_halflife` does
  nothing): the "fading heat" candidate is ruled out by construction. The ridge part does fall late (ln newc -0.23
  to -0.28: the stress rifts die out, spreading slows), but arcs are ~95% of the source and rise a little, so the
  source is flat (ln ~8.0 in every 100 Myr bin, `step2/bins_main.txt`).
- **It's weatherability, mostly relief.** The fresh rock eroded on bare land (the weathering supply) is ~20%
  higher late than at 300-500 Myr (ln +0.11 to +0.18), and the plant factor rises by ~4% on every seed. Per seed,
  ln supply follows the erosion rate on bare land (corr 0.98), which follows the land's relief: the bed's 90th
  percentile rises by a median 400 m, its mean by ~120 m (corr with supply 0.61); runoff only +4%. Bare land share
  is flat, so it isn't sea-level exposure. The late relief is Earth-like (land bed mean ~800-850 m, p90 ~1.6-1.9
  km; Earth's land mean ~840 m), while 300-500 Myr is a low-relief interval for many seeds (200-300 Myr had high
  relief again: an orogeny cycle, not a monotonic drift).
- **The thermostat answers as it should**: the temperature factor falls slightly (warming back), the sink's own
  fb stays in the ~0.5 range of v1-finish (`step2/summary_*.txt`).
- **The drift isn't it either**: it is warmer late than early on these seeds (same RNG draw per seed, so the same
  +1.2 to +1.8 C in both draws), i.e. it masks part of the cooling.

**Verdict:** a real mechanism behaving as the physics says: when mountains rise and plants spread, the planet
weathers more readily, CO2 falls and it cools until weathering balances the outgassing again (the
uplift-weathering hypothesis, Raymo & Ruddiman 1992, behind the late Cenozoic cooling; the plants' weathering
since the Devonian, Berner). The reference frozen at 300 Myr (PW-558/559 B) is what lets a lasting change in
weatherability count, which is the point of freezing it. The plant part is the run's flora arriving through its
history (`flora_end` = the run's length), by design. Not an artefact or a bug, so no fix; and the balance itself
isn't wrong (C not taken: it would only chase the metric, and 700 ppm made most quick windows ice-free).

The size of the late cooling is mostly the draw: the re-rolled draw (+0.001 C offset) of the same 16 seeds has
almost none (dT +0.02, CO2 term -0.92 C) where the first had -0.91 / -2.94.

**Pass rate on the owner's bar over 1 Gyr** (`passrate.py`, judged on 300-1000 Myr; `step2/passrate.txt`): icehouse
(ice >= 20 m of sea level) at most ~40% of the time, no always-icebox (>= 90%, or ice below -150 m on >= 30% of
updates), no hellhole (median dT > 10.5 or any > 15.5).

| sweep | seeds | owner's bar | icehouse median (300-500 / 600-1000) | always-icebox | hellhole | N1-N4 |
|---|---|---|---|---|---|---|
| draw 1 (main) | 16 | 11 (69%) | 37% (6 / 48) | 1 (seed 2, 85%) | 0 | 11 |
| draw 2 (+0.001) | 16 | 13 (81%) | 28% (7 / 28) | 0 | 0 | 13 |
| **pooled** | 32 | **24 (75%)** | 33% | 1 | 0 | 24 |

At the owner's ~70% bar. Fails: seed 2 (draw 1: 85%, then 27% on draw 2), 99 (73% / 8%), 103 (73% / 49%), 13 (57% /
38%), 105 (44% / 35%), 1 (37% / 46%), 42 (26% / 42%). Only 103 fails on both draws. Hottest keyframe dT +11.8
(26 C). So the 1 Gyr bar holds, the late history is icier on some draws (the median late share 28-48%), and
the outliers are outlier draws, not seeds. Decision: **B, accept** (the coordinator delegated it; the evidence is
clear).

## Step 2: PW-709, N3's floor only on >= 1 Gyr runs (5e552b9)

`tools/ice_criteria.py`: the 5% floor of the icehouse share is judged only when the run reaches `FLOOR_RUN`
(1000 Myr; its last climate update may fall a step short); the 70% cap, the 300 Myr longest-icehouse limit and
N1, N2, N4 are judged on every window. No threshold moved. `res["icehouse"]["floor_judged"]` says which.
`test_ice_diag` checks both sides. `docs/review/ice-v2-criteria.md`'s N3 row says so. On the 32 seed-draws
above, N1-N4 pass 24 of 32 (the floor fails left are draws that never glaciated in 700 Myr: seed 11 on both draws, 21,
5 and 7 on one each; a variety miss over a long window, which is what the floor is for, not a window artefact).

## Step 3: PW-700, the present in an icehouse era is a warm moment of it (5e552b9)

`highlights.representative_time`: when the picked frame (the geographically most typical once the full flora has
appeared) is in an icehouse era (sea_ice_m <= -20 m; spells within 8 Myr joined, the same rules as ice_criteria),
the pick moves to a warm moment of the same era: among the era's least-ice quarter, the geographically most
typical. Picked from the run's own record, no fixed date. Runs without sea_ice_m are unchanged. `planet make`'s
time zoom starts there and finishes at its latest interglacial (`finish.now_kyr`, unchanged), so the default
present is an interglacial within the present icehouse era. On the old showcase runs: 3a0480 964 (-114 m) -> 960
(-106), 0d1889 944 (-84) -> 912 (-32), 172922 996 (-87) -> 968 (-34); a6643c, 89bea8, 0ceebf unchanged (already in
their era's warm quarter, or not in an icehouse). Test `test_representative_time_interglacial_in_icehouse`. Full
pytest 623 passed, 1 skipped (`step1/full.txt`). Docs: coordination.md's recipes, overview's `slice --at auto`.

## Step 4: PW-202, the showcase

**Recipes' climate_offset re-checked** (L6, 1 Gyr, `preset_*`; `passrate.py`): kept as they are.
- Cold world (`tilt=15 climate_offset=-6`), seeds 15 and 1: an icehouse 100% of the time, deep (< -150 m) 55% /
  83%, worst -356 / -377 m, dT -6.6..+4.7 / -10.8..+0.8: a permanently cold world with LGM-to-3x-LGM ice, never a
  snowball, which is the recipe's point (a world-builder choice). The warmer balance made it milder, not colder.
- Hothouse (`tilt=45 climate_offset=5`), seeds 16 and 1: never an icehouse, global mean 21.5 / 23.3 C median,
  26.9 C at most (dT max +14.2): a Cretaceous-like hothouse under the hellhole bar (25 C median, 30 C max).
- Earth-like (0): the sweeps above.

**Earth world:** `tools/earth_world.py` (L6) -> **506694** ("Earth (today, ETOPO1) — model vs observed"). The
worktree needed `data/earth/` copied from the main checkout (the Koppen server resets connections).

(The four L7 planets: filled in below once made.)
