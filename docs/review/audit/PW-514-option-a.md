# PW-514 option A: coast_loss with the cost cut, alone (2026-10-21, agent pw514a)

Branch `worktree-agent-a9ef586c8f7c30585`, from main e599d1e. Scratch: session scratchpad `pw514a/`
(`phase1.sh` runs, `phase2.sh` time zooms, `phase3.sh` + `bench_states.py` + `variants.py` cost and
fixed-point checks, `sl_table.py` + `tect_split.py` sea level, `pan_repro.py` + `pan_diag.py` PW-515;
fresh runs in `store_main`, `store_br`). Nothing was written to the real store.

**Outcome: meets every merge criterion.** Cold eras 8/10 (main 8/10), Earth time zoom bit-identical,
drift check 5/10 (main 4/10), the climate update is cheaper than main's, `uv run pytest -q` passes
(golden `sim_L4` regenerated for the PW-515 fix). Ready to merge.

## What was taken
- From c720d92 (PW-465 side lane), the code only: `icemass.coast_loss`, the shared marine constants and
  `shelf_viable`, `earth.coast_cost` / `marine_view`, the trim of a sheet in deficit in `ablation_zone`,
  `ICE_CALVE` removed, and the callers in `tests/test_invariants.py`, `tests/test_timezoom_consistency.py`,
  `tools/ice_probe.py`. Its tracker changes and drafts were left out (already intaken: PW-513/514/515).
- From b74f2c0, the cost-cut hunks only: `coast_cost` and the bare-ground start balance (`earth._start`)
  once per fixed point, on the bed the old ice pressed down, and `PASS_TOL` (a fixed point settles when the
  iced cells repeat but for 0.2% of them, at least 2 cells). `_ice_pass` and `ablation_zone` take `cost` /
  `start` (computed if not given, so `test_invariants` still calls `_ice_pass` alone). Not taken: PW-464's
  `cycle_ice` / `glacial_states` / `balance(warm=)` / `ice_mean`, PW-460/459's margin ramp and
  seasonal `orbit_k`, the `tools/sealevel.py` `ice_mean` field.
- **PW-515 fixed at its cause** (`kernels.carve`). The test's failing frame (L4 seed 1 @ 220 Myr, cell 2461,
  415.7 m, a remembered valley 9.4 m deep, beside a 410.9 m salt pan) reproduced. `carve` stops a valley
  floor at the next cell downstream, `floor = out[d]`. Here that cut 2461 to exactly 410.918 m, the pan's
  height. With no lower neighbour, the lakes' bed had a flat, and `lake_order` gave 2461 no receiver, so it
  was a pit of its own in the pan's basin. It became a sink, but with too little catchment to be a pan, so
  its river ended 5 m above the pan beside it. The floor now stays `eps` = 0.01 m above the next cell, as
  `priority_flood` and `fill_shallow` already do. After that, 2461 drains into the pan. The test is
  unchanged. This changes the rivers and terrain of every run a little: `tests/golden/sim_L4_s1_60myr.json`
  was regenerated on purpose (its ice is unchanged; rivers, flow, elevation and what follows changed).

## Measures (same seeds and harness as docs/review/audit/PW-465-side-lane.md)

Main is today's main (e599d1e). Its run physics are unchanged since the side lane's 2a6f559 reference:
main's seeds 7 and 1 re-run here are identical to the reference tracks, and the 4 main runs give the same
drift numbers as the side lane's main column. So the main columns are the reference's.

### 1. 10-seed L6 1 Gyr cold-era check (`tools/sealevel.py`; worst >= -450 m and <= 2% of time below -430 m)

| seed | main worst / <-430 / <-150 | branch | (side lane c720d92) |
|---|---|---|---|
| 3199 | -386 / 0.0% / 31% ok | -228 / 0.0% / 8% ok | -210 ok |
| 11 | -569 / 5.2% / 37% F | -417 / 0.0% / 10% ok | -473 F |
| 2 | -404 / 0.0% / 22% ok | **-560 / 3.6% / 27% F** | -334 ok |
| 21 | -393 / 0.0% / 11% ok | -254 / 0.0% / 9% ok | -220 ok |
| 1 | -260 / 0.0% / 13% ok | -397 / 0.0% / 22% ok | -352 ok |
| 5 | -215 / 0.0% / 16% ok | -285 / 0.0% / 24% ok | -166 ok |
| 7 | -362 / 0.0% / 14% ok | -282 / 0.0% / 22% ok | -745 F |
| 13 | -372 / 0.0% / 44% ok | -380 / 0.0% / 23% ok | -479 F |
| 42 | -364 / 0.0% / 27% ok | **-510 / 6.8% / 14% F** | -304 ok |
| 99 | -450 / 3.2% / 60% F | -349 / 0.0% / 58% ok | -404 ok |
| pass | **8/10** | **8/10** | 7/10 |

Seed 7's -745 m on the side lane is gone (-282). The seeds that fail move around (2 and 42 now), as
expected from a changed trajectory. Time below -150 m falls on 6 seeds and rises on 4.

### 2. PW-471 run-moment drift at I = 0 (index off, mean orbit, no swing, 50 kyr; 4 fresh L6 800 Myr runs, seeds 5/3/2/11)

| moment | main ice % land | main @50 kyr | branch ice % land | branch @50 kyr |
|---|---|---|---|---|
| s5 @ 260 | 10.4 | -52.1 F | 15.6 | +27.0 F |
| s5 @ 440 | 28.3 | +26.7 F | 10.6 | +17.9 |
| s5 @ 520 | 18.0 | +94.1 F | 6.3 | +18.4 |
| s3 @ 200 | 17.1 | +84.0 F | 1.8 | -10.0 |
| s3 @ 500 | 10.0 | +22.1 | 25.4 | **-91.1 F** |
| s3 @ 620 | 13.4 | +49.1 F | 25.9 | +44.6 F |
| s2 @ 500 | 39.2 | +101.8 F | 60.7 | +41.3 F |
| s2 @ 700 | 13.1 | +17.4 | 3.2 | -3.1 |
| s11 @ 200 | 36.4 | +16.0 | 42.2 | **+89.5 F** |
| s11 @ 420 | 13.5 | +17.0 | 2.1 | -2.9 |
| within 25 m | **4/10** | | | **5/10** |

That's not worse than main (median |drift| 38 m on main, 23 m here), but it is far from the side lane's 9/10.
The cost cut is not the reason. On 24 fixed states (seeds 11/2/7 @ 200/300/400/520 Myr, from both
codes' runs), the climate update's ice with the cut, with exact repeats, and with cost and start recomputed
every pass (the side lane's rule) agrees within 2.5 m of sea level everywhere (`variants.py`; e.g. seed
11 @ 400: -22.7 / -20.8 / -23.3 m). So the rule is the side lane's. The difference is in the moments: the
same times fall on different ice on this trajectory (the carve fix and the cut each perturb it). The misses
are the heavily iced moments (25-61% of land): the zoom loses 41-90 m of the run's ice on s11 @ 200 and
s2 @ 500, and gains 91 m on s3 @ 500. The side lane had s2 @ 500 at 58% within 1 m, so heavy ice alone
doesn't explain it either. With 10 moments the check is noisy at about ±2-4 moments.
Draft: draft-coast-loss-iced-moment-drift.md.

### 3. Earth time zoom (L6, 600 kyr, default)
Bit-identical to main (`out_tz/earth_main.npz` and `earth_br.npz` compare equal): cycles 108.5, 98.5, 107.5,
99.5, 107 kyr; maxima -84..-104 m; interglacial ice 9.1-11.9% of land (and 20.7% at the window's end);
Laurentide to 42.5 N, 0.47 Mkm2 south of 50 N. (These differ a little from the side lane's numbers
because PW-213 merged on main since. Both codes here include it.)

### 4. Cost
- Whole run, seed 11 L6 400 Myr side by side (4 threads): main 303 s wall / 781 s CPU, branch **190 s /
  401 s (-37%)**. That isn't like for like: main's trajectory has a -569 m cold era there, and the branch's
  is milder.
- So, fixed states: the same 12 states timed on each code (`bench_states.py`, best of 3 per climate
  update, 4 threads). On main's states: main 63.4 s, branch **19.3 s**. On the branch's states: main
  33.3 s, branch **25.0 s**. On both sets the branch is cheaper. Most of main's extra time is fixed points
  that never settle: a margin cell or two flicker, and main runs the full 201 passes (5 of the 24
  updates). PASS_TOL ends those at 2-11 passes. On states where neither flickers, the two codes cost
  about the same (1.1-2.0 s per update).
- Bar (<= ~+5% wall): met, by a wide margin.

### 5. PW-549: total sea level (ice + ocean-basin term), the same 10 seeds

| seed | main end (ice + basin) | main min | branch end (ice + basin) | branch min |
|---|---|---|---|---|
| 3199 | -294 (-2 + -292) | -746 @ 632 | +5 (-15 + +20) | -466 @ 356 |
| 11 | -394 (-142 + -252) | -591 @ 192 | -13 (-26 + +13) | -413 @ 212 |
| 2 | -472 (-302 + -170) | -653 @ 964 | -135 (-12 + -123) | -612 @ 652 |
| 21 | -378 (-108 + -270) | -577 @ 876 | -92 (-8 + -83) | -454 @ 912 |
| 1 | -360 (-11 + -349) | -526 @ 792 | -47 (-17 + -30) | -448 @ 484 |
| 5 | -296 (-19 + -277) | -486 @ 552 | -575 (-278 + -297) | -575 @ 1000 |
| 7 | -242 (-37 + -204) | -605 @ 224 | -432 (-160 + -272) | -510 @ 868 |
| 13 | -242 (-188 + -54) | -503 @ 876 | -263 (-36 + -227) | -602 @ 864 |
| 42 | -236 (-92 + -144) | -500 @ 480 | -88 (-29 + -59) | -729 @ 492 |
| 99 | -491 (-203 + -288) | -750 @ 532 | -550 (-212 + -338) | -576 @ 972 |
| median | end -328, 4/10 below -370; min -584 | | end -113, 3/10 below -370; min -543 | |

On 4-Myr samples, the share outside -250..+300 m is 10-61% on main and 9-50% on the branch.

What this says about PW-549:
- **The deep ends are mostly the ocean-basin term, not the ice.** At 1 Gyr the basin term is -144..-349 m
  on 9 of 10 main seeds, while the ice part is under -150 m on only 3. The basin term follows the ocean
  floor's mean age almost exactly: the correlation is -0.87..-0.97 on every seed of both codes. The floor
  starts at ~50 Myr (the 48 Myr reference that sets sea level 0) and ages to **61-130 Myr by 1 Gyr** on main.
  Old floor is deep, so the basins hold more water. (`hot_sea` adds nothing at the default
  `heat_start` 1.) Where the floor stays young (branch seeds 3199, 11, 1: 55-63 Myr at the end, 10-14
  plates) the basin term ends near 0. Where it ages (branch 5, 99: 97-114 Myr; seed 5 down to 4 plates) it
  ends at -300..-340 m.
- The ice and basin terms are correlated (median +0.4..+0.5): eras of old, slow-spreading ocean are also the
  cold eras. That fits the CO2 loop (less ridge outgassing, colder), so one cause, slowing plates and ageing
  floor, deepens both terms at once.
- **coast_loss touches only the ice part, and that part comes out milder:** median end ice -27 m against
  -100, and the time below -150 m and the cold-era failures are about the same or better. The branch's
  younger end oceans (median end plates 12 against 8.5) are a different trajectory, not something
  coast_loss does: the code changes nothing in tectonics. So coast_loss **helps the ice part a little and
  doesn't touch the main driver**, the ocean floor ageing to 60-130 Myr over a Gyr, so that the fixed 48 Myr
  reference reads as -150..-350 m.
- Not tried (PW-549's own work): whether a 1 Gyr planet's floor should age that much (plate count falling,
  slower spreading late), or whether the reference should be the planet's own long-run mean.

## Tests
`uv run pytest -q` (-n 6): 559 passed, 1 skipped. Golden `sim_L4_s1_60myr.json` regenerated for the carve
fix (intended; the ice in it didn't change).
