# Thread-count independence (PW-1324, lane 124, 2026-11-02)

**Result: not reproduced.** The same seed gives the same simulation state at 1, 2, 6, 8 and 16 numba threads.

Method: `Simulation(build_grid(L), 1, Params(run_end=myr), 2.0)` run with `sim.run(myr, keep)`; at every 10 Myr
`keep` hashes (md5 of the bytes) every field of `sim.snapshot()` (elevation, plates, rock, climate, water, landforms,
volcanoes, ...). Each run is its own process with `NUMBA_NUM_THREADS=T`; `import planet` comes first, so BLAS is 1.
The traces were compared field by field.

| level | length | thread counts | result |
|---|---|---|---|
| L5 | 60 Myr | 1, 2, 6, 16 | all fields identical at every 10 Myr |
| L6 | 100 Myr | 1, 6, 16 | identical |
| L5 | 400 Myr | 1 and 8; whole vs `sim.run` in 100 Myr chunks (as tools/scorecard.py) | all four identical |
| L5 | 1000 Myr | 1 and 16; whole vs 100 Myr chunks | all four identical |

Commands (scratch scripts, not kept): `NUMBA_NUM_THREADS=T PYTHONPATH=. uv run python h.py LEVEL MYR 1 10 out.json [chunk]`.

So lane 118's 33.5% vs 35.6% land at seed 1 cannot come from the numba thread count or from chunking the run.
More likely differences between the two scripts: `Params(run_end=...)` (the star's brightening and the plant
calendar depend on it: a screen that leaves `run_end` at 0 runs a different world), a different commit, or BLAS
threads (docs/coordination.md: OpenBLAS's count does change outputs; `planet` pins it to 1 only if imported before
numpy). Check those first when two "same seed" runs differ.

The kernels (69 `prange` uses) do not add across threads in a thread-dependent order, as far as these runs show.
Guard: `tests/test_thread_independence.py` (L4, 100 Myr, `numba.set_num_threads` 1 vs the pinned 4; ~25 s).
