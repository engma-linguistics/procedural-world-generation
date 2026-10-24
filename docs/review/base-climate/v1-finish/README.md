# v1-finish: the serial run-physics lane's last v1 gates (2026-10-24)

Branch `worktree-agent-a6d02ad362f9b6ab0`, from main 91d0887. Each step is its own commit. Scripts here; raw outputs in
the step folders. CPU: at most ~24 cores (health `--workers 6 --threads 3`, pytest `-n 4` with `PW_SEED_WORKERS=3`).

## Step 1: PW-693 + PW-446, one canonical mantle basis

`mantle._build_basis` took an SVD's columns per degree. Within a degree those are arbitrary (sign, and any rotation
where singular values are close), and LAPACK could return another set by thread count or load. The random mantle
eddies sit on these columns, so the basis a process got picked the world. Three different caches existed on this
machine.

**The change (`planet/tectonics/mantle.py`):** the basis is now the real spherical harmonics by definition:
degree d, then order m = 0 and the cos/sin pairs of m = 1..d, each `N_dm P_d^m(z) Re/Im((x + iy)^m)` (no
Condon-Shortley sign). They come from the Legendre recurrence in z and from products of x and y only, so there's no
trig and no SVD. Then a sequential compiled modified Gram-Schmidt, in that order and after the cells' mean, makes
them exactly orthonormal on the cells. It runs twice for round-off. It uses only `+ - * / sqrt` in a fixed order,
so the bits depend only on the grid's cells. The cache's key also hashes the orthonormaliser's source. The cache
was already written atomically (temp file + `os.replace`, PW-258), and that's kept.

- **Bit-identical builds:** at L4-L7 the digests are the same at 1 and 24 threads, and the same for six concurrent
  builds at 1-6 threads (L6 `395cef5ca38f`, L7 `02ec82c9a042`; `step1/` notes). Orthonormal to 5e-14 at L7, and
  0.7 s to build at L7 (the SVD took ~2.2 s).
- **New test** `test_mantle.py::test_basis_is_canonical`: it pins the L4 digest (`ede56f0c...`), checks that degree 1
  is z, x, y (correlation > 0.99999), and checks that fresh subprocesses at 1 and 8 threads build the same bits.
- **Goldens regenerated on purpose** (`tests/golden/sim_L4_s1_60myr.json`, `--update-golden`). Every run's eddy
  field is new, so every run is a new draw of the same physics. Stored baselines move with it.
- Full `pytest -q -n 4`: **613 passed** in 1092 s (`step1/full.txt`).
- Scorecard (`step1/scorecard.txt`): Earth group agreement 71.1%, unchanged (the climate code didn't change, so
  `earth_check` isn't affected). Seeds 1 and 2 at 1 Gyr: land 33.8 / 31.8%, crust 42.4 / 40.2%, ice 1.5 / 2.5%,
  NPP 356 / 303. These are new draws, all within the envelopes.

## Step 2: PW-681 + PW-653 on the canonical basis, and PW-559 B (the carbon cycle's balance at 500 ppm)

**Health on the canonical basis** (`step2/health_canon.md`): 32 L6 seeds (defaults, 101-108, 201-216), `--quick`.
The table is `outliers.py`, pooled the way `merge-1024/hsum.py` pools (`step2/outliers.md`, `step2/hsum.md`).

The north star, in numbers:
- **hellhole**: median keyframe temperature > 25 C, or any keyframe > 30 C;
- **always-icebox**: icehouse >= 90% of the time, or ice sea level below -150 m on >= 30% of keyframes;
- **owner's icebox bar** (2026-10-24): at most ~40% of the time in an icehouse (ice >= 20 m of sea level). Earth is
  ~10-30%, and ~70% of seeds should pass.

| tree | seeds | hellhole | icehouse > 40% | always-icebox | pass | icehouse % median / mean | kf < -150 m pooled | old bar ok | N1-N4 ok | temp median / max |
|---|---|---|---|---|---|---|---|---|---|---|
| main physics, canonical basis | 32 | 0 | 16 | 5 | **16 (50%)** | 45 / 44 +- 5 | 11.0% | 31 | 23 | 16.4 / 25.9 |
| + balance 500 ppm | 32 | 0 | 9 | 2 | **23 (72%)** | 19 / 26 +- 5 | 2.6% | 31 | 22 | 18.1 / 27.6 |
| + balance 500 ppm, re-rolled (climate_offset +0.001) | 32 | 0 | 3 | 1 | **29 (91%)** | 14 / 18 +- 4 | see hsum.md | 30 | 18 | 18.0 / 27.6 |
| + balance 700 ppm (tried) | 32 | 0 | 5 | 0 | 27 (84%) | 0 / 15 +- 4 | 0.6% | 32 | 10 | 19.6 / 28.7 |

- **PW-681 verdict:** main is not a hellhole risk: no seed comes near one. It is an icebox risk. Across 32
  old-basis seed-runs and these 32, the icehouse share sits at a mean of 44-45%. Half the seeds fail the owner's
  40% bar, and 5 of 32 are always-icebox. The step-to-step moves in the deep share (merge-1024's 3.8 -> 7.45%, the
  101-108 jump) are the draw: the basis change alone, a pure re-draw, moves single seeds by 30-90 points. But the
  level is signal. It is PW-559's cause, assumption A0: the CO2 stock's balance was today's pCO2, so the planet's
  long-run mean climate was today's icehouse Earth, and the drift (+-3 C) put it below that half the time.
- **The fix, PW-559 option B (`climate.PCO2_BALANCE` = 500 ppm):** the carbon cycle's balance, the stock's frozen
  reference, is no longer today's pCO2. It's the middle of the Phanerozoic record in log terms (~280-400 ppm in the
  Carboniferous-Permian and the late Cenozoic, ~1000+ in the Mesozoic; Foster et al. 2017). `co2_term` still counts
  from the climate model's dT = 0 (350 ppm), so a planet at its balance runs ~1.5 C warmer than today's Earth. The
  plants read the same pCO2 (`climate.pco2`). Nothing else moved: the thermostat's gain, the drift and the
  references are as they were. **Attempt 1 was 700 ppm** (a doubling): 17 of 32 seeds never glaciated in the
  window (median 0%), too warm against Earth's 10-30%. **Attempt 2 was 500 ppm:** median 19% / 14% on the two
  draws (Earth 10-30%), owner's-bar pass 72% / 91% (pooled 81%), always-icebox 2 / 1 of 32, no hellhole, hottest
  keyframe 27.6 C (PETM-like). Deep ice (< -150 m) on 2.6% of keyframes (was 11.0%).
- N1-N4 (ice-v2 criteria) pass 22 / 18 of 32. The fails are now mostly "icehouse 0%, outside 5-70%" over the
  200 Myr quick window, not long or deep eras. That is N3's lower bound, a threshold for the owner. The owner's bar
  says up to 40% is fine and outliers are OK. A 200 Myr window with no icehouse is ordinary for Earth (the
  Mesozoic). Left as is (no threshold change).
- **1 Gyr, the 10 thermostat seeds** (`tools/ice_diag.py`, judged on 300-1000 Myr; `step2/diag_*.summary.txt`).
  Icehouse share per seed (11, 13, 1, 21, 2, 3199, 42, 5, 7, 99):
  - canonical basis: 65, 60, 28, 46, 65, 10, 49, 9, 46, 63. Median 47%; 3 of 10 at <= 40%.
  - balance 500: 3, 22, 51, 28, 57, 22, 54, 5, 43, 53. Median 36%; 5 of 10 at <= 40%, 6 of 10 at <= ~43%.

  The long runs are icier than the quick window. The 600-1000 Myr part of a run is colder than its 300-500 Myr
  part, so on the full history the balance fix gets about half of the seeds under the bar, not 70%+. Inbox draft
  `draft-late-history-cooling-1gyr.md` covers it.
- **PW-653, the thermostat at 3 C per doubling:** the sink's own fb is +0.48 (canonical basis) and +0.58 (balance
  500). A23 expected ~0.51-0.56. The CO2 answer with the trends out has a median of +0.39 C/C, 7 of 10 in the
  0.35-0.9 band (canonical), and +0.47, 3 of 10 in band (balance 500; the misses are mostly above the band's top
  or near 0 on the warm seeds). The thermostat-1024 lane saw s3 0.59 against s4 0.43 on the old basis. That was
  the draw: the canonical draw of the same physics as s4 gives 0.48. PW-627 didn't weaken the sink.
- Full `pytest -q -n 4`: **613 passed** (`step2/full.txt`). The golden was regenerated on purpose (the CO2 term
  moves dT). `test_co2_stock::test_forcing_levels_off_smoothly` now states the definition in pCO2: 0 at
  PCO2_REF, +3 C per doubling, antisymmetric about PCO2_REF, and +1.5 C at the balance. It's a definition, not a
  threshold.
- Earth (`step2/earth_check.txt`): exact 34%, group 71%, log-rain corr 0.649. Unchanged: dT = 0 and the plants'
  350 ppm reference are unchanged. Scorecard (`step2/scorecard.txt`): seeds 1 / 2 at 1 Gyr, land 30.7 / 33.6%, ice
  2.5 / 0.9%, NPP 393 / 340.

## Step 3: PW-348 (ef4b36b)

`world.py` stores land as at least 1 m and sea as at most 0 m, so the stored land mask is the model's.
`test_world_soils` checks soil on every stored non-land cell again. 613 passed (`step3/full.txt`). It was committed
before step 2 because it's independent of the runs.

## Scratch (session scratchpad `v1f/`)

- `canon_tree`: step 1. `bal_tree`: step 2 at 500 ppm (700 for `h_bal700`). `bal_rr`: 500 ppm with
  climate_offset +0.001.
- `h_*`: the health sweeps. `t1024/diag_canon_tree`, `t1024/diag_bal_tree`: ice_diag.
