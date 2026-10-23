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
