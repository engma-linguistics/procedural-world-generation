# PW-471 handoff: v1 ice ages by a glacial index (2026-10-20, agent pw471)

**Outcome: the glacial index is built and is the time zoom's only mode. Earth passes every criterion.
Run moments fail the 7/10 bar (0/10), because their ice at I = 0 isn't the zoom's balance (PW-436). The
stop rule was reached after two attempts, so there's a needs-decision draft
(`issue-tracking/inbox/draft-glacial-index-run-moment-drift.md`).** On those moments the index still
drifts less than main's PW-440 cycle on 9 of 10.

## What it does (`planet/timezoom/cycle.py`, `forcing.py`, `sim.setup_index`)
- I(t), from 0 (interglacial: the run's climate) to 1 (glacial maximum), is computed up front from the
  planet's orbit. It is a three-state conceptual model (Paillard 1998 states, Huybers 2011 falling bar):
  - **between:** I = 0 for at least `ig_kyr` 10 kyr;
  - **building:** starts when the summer sun at the cycling latitude falls below the 40th percentile of
    its own 800-kyr series; I approaches 1 with an e-folding time of `build_kyr` 36 kyr, at x(1 +/- 0.5)
    with the sun (`build_orb`);
  - **ending:** starts when I >= 0.85 and the sun beats a bar falling from the 95th to the 60th
    percentile over 100 kyr; I falls to 0 in `end_kyr` 8 kyr;
  - backstop at 200 kyr (counted; it has never fired).
- Cycling latitude: the mean latitude of the snowline land in the hemisphere with more of it. Snowline
  land is ice-free land whose annual mean, brought to sea level, is below 0 C (Earth: 65.2 N).
- dTg = -I x cooling + the plants' term, polar-amplified by the existing paths (`amp` in the step,
  climate.compute for the full climates). Cooling = `glacial_cool` x (snowline-land share / `glacial_f`),
  capped at 1.6x; `glacial_dt` sets it by hand.
  - `glacial_cool` is 6.5 C at Earth's share, 0.035 (measured at L6: 0.0349).
  - 6.5 C is above the LGM's 4.5-6 C. At 6 C Earth's maxima were -75..-92 m, below the -80 m bar; the
    model's sheets answer a cooling weakly (PW-435). A calibration call: flagged, not hidden.
- The CO2 and ice-albedo feedbacks are removed, with the PW-440 boosts (melt_f, calving x, release),
  `start`/`average_room` and the sea-level-driven Cycle. `co2_share` (0.5) only sets the plants' CO2.
  `kernels.climate_melt` was folded back into `climate_step`; it's bit-identical for icemass and the run.
- Diagnostics in meta `ice_age_cycle` and `run.txt`: endings, `cycle_kyr`, `cooling_c`, `target_m` (the
  sea-level target: 2 km of ice over the snowline land, Earth 87 m) and `snowline_land_share`. Each
  frame's stats have `glacial_index`.
- Speed: the new front's balance reuses the step's `orbit_k` (one `smooth_big` per step instead of two).
  Earth 300 kyr L6, 8 threads: main 36.1-37.0 s, branch 36.8 s (38.2-38.6 before that reuse). It is no
  slower, with 2.5x the ice.

## Earth (L6, 600 kyr, default; showcase `6d0ed0` in the real store)
| criterion | target | result |
|---|---|---|
| cycle length | 80-120 kyr | 98.5, 107.5, 108.5, 99.5, 107 |
| fast endings | ~10 kyr | I falls in 8 kyr; sea level rises 57-76 m in the 15 kyr after each ending starts |
| glacial maxima | -80..-130 m | -86, -87, -94, -97, -99, -104 |
| Laurentide south of 50 N at maximum | yes | yes: to 42.5 N, 0.7 Mkm2 south of 50 N (9.2 Mkm2 in North America) |
| interglacial ice | 9-12% of land | 9.1, 9.4, 9.7, 10.8, 12.2 (sea level -12..+6 m) |

## Run moments (L6, 400 kyr; 4 fresh L6 runs of 800 Myr in the scratch store, seeds 5/3/2/11)
Moments (ice % of land): seed 5 @ 260 (10), 440 (28), 520 (18); seed 3 @ 200 (17), 500 (10), 620 (13);
seed 2 @ 500 (39), 700 (13); seed 11 @ 200 (36), 420 (13). A moment passes if it cycles, each glacial
maximum is at most 1.5x its target below the start, and no interglacial stands more than 1.5x the
target above it.

| moment | cooling C | target m | cycles kyr | maxima m | interglacials m | mean m (main) |
|---|---|---|---|---|---|---|
| s5 @ 260 | 5.95 | 86 | 109, 98, 108 | -220..-231 | -73..-171 | -147 (-74) |
| s5 @ 440 | 0.53 | 7.5 | 94, 91, 91 | 0..+27 | +34..+61 | +34 (+45) |
| s5 @ 520 | 0.62 | 8.8 | 118, 93 | +120, +161 | +166..+198 | +154 (+186) |
| s3 @ 200 | 0.49 | 7.2 | 114, 111 | +98, +101 | +145..+159 | +122 (+172) |
| s3 @ 500 | 1.65 | 24 | 115, 94, 94 | +17..+24 | +51..+56 | +34 (+55) |
| s3 @ 620 | 3.59 | 53 | 116, 91 | -58, -82, -63 | +32..+60 | +4 (+102) |
| s2 @ 500 | 0.40 | 5.9 | 116, 92, 93 | +93..+100 | +129..+176 | +123 (+145) |
| s2 @ 700 | 0.18 | 2.6 | 92, 92, 114 | +112..+115 | +130..+132 | +112 (+124) |
| s11 @ 200 | 0.90 | 13 | 92, 91, 91 | 0..+88 | +57..+147 | +70 (+103) |
| s11 @ 420 | 3.64 | 52 | 91, 93, 114 | -71..-85 | -4..+37 | -20 (+82) |

**0/10 pass** (s3 @ 620 and s11 @ 420 come closest). Every moment cycles, at ~100 kyr, with no runaway
of the index itself. What fails is the reference. With `index=off` and the mean orbit (I = 0
throughout), 5 of 10 drift by more than 25 m in 50 kyr, by +16..+101 m, and are still drifting. Calving
and shelf melt beat the surface balance, and even -4 C of extra cooling doesn't hold the ice (PW-436,
PW-461 B(2): the run's rule has no calving). Earth's real ice is near balance at I = 0 (-10..+5 m).

## Attempts
1. The index as specified: Earth good after tuning (see below), runs 0/10 (table).
2. The index plus a 40 kyr spin-up at I = 0 and the mean orbit, so the zoom starts in its own interglacial
   (PW-462 item 3). Runs 3/10 (at 6 C). The spin-up moves the sea level -51..+98 m and hasn't converged
   on several moments, and it costs +7%. Reverted; the patch is `docs/review/audit/PW-471-spinup.patch`.

Earth tuning, in order:
- linear I over 90 kyr: cycles 72-92 kyr, too short;
- saturating build (e-folding 40 kyr): 90-116 kyr, but interglacials only ~0 kyr long, because the next
  build started at once, so they stayed -14..-22 m with 12.5-13.6% of land iced;
- `ig_kyr` 10 kyr minimum interglacial with an 8 kyr ending: interglacials -6..+6 m;
- cooling 5 -> 6 -> 6.5 C.

## Tests
- `tests/test_timezoom_cycle.py` (rewritten):
  - the index's sawtooth on Earth's and 4 seeded orbits: cycles of ~100 kyr (80-120 on Earth's), builds
    over 60 kyr, endings of end_kyr;
  - endings at sunshine peaks;
  - no swing or index=off means no ice age;
  - the cooling's planet-relative scaling;
  - on sim4 (L4): dT_global = -I x cooling, and an ending gives back most of the glacial's ice within
    15 kyr.
- `tests/test_timezoom_consistency.py`: the 25 m start-drift test is now "the zoom's ice at I = 0 is the
  run's": with no orbital swing the index never builds, and sea level stays within 25 m in 20 kyr.
- `tests/test_timezoom.py`: test_feedback_room is replaced by test_glacial_index_cooling.
- Full `uv run pytest -q`: 415 passed. No golden changes were needed (the run is untouched; `test_kernel_threads` now tests `climate_step`, the folded kernel).

## For PW-418 / pw037-carving
On Earth the ice is now bounded, and SIA speeds at the first glacial maximum (82 kyr, -86 m) are a
median of 18 m/yr (northern sheets 23), p99 1.8 km/yr. PW-418's blocker was a ~1 km/yr median on
drifting moments. So carving looks unblocked for Earth zooms, but not for drifting run moments: see
draft `draft-carving-after-glacial-index.md`. Not merged.

## Scripts (session scratchpad `pw471/`)
- `tz_eval.py`, `sweep.sh`: in-memory zooms and their summary;
- `shift.sh`: global dT offsets;
- `idx.py`: the index alone on synthetic orbits;
- `main_batch.sh` / `main_eval.py`: main's code on the same moments;
- `timing.py`;
- `speeds.py`: SIA speeds;
- `showcase.py`.
The scratch store with the 4 runs is `pw471/data` (ids 3133f2 seed 5, 575ac0 seed 3, 8386d5 seed 2,
ea0254 seed 11).
