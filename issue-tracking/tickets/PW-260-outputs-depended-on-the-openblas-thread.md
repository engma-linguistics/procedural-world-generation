---
id: PW-260
title: Outputs depended on the OpenBLAS thread count; now pinned to 1 (runs made before replay differently)
type: task
status: todo
parent: null
subsystem: infra
effort: xs
impact: med
found_by: parallel
blocked_by: []
relates: [PW-215, PW-250]
refs: [planet/parallel.py, tests/golden/sim_L4_s1_60myr.json, docs/scorecard.jsonl]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Measured 2026-10-15 on the Threadripper: numba's thread count doesn't change any output, but numpy's OpenBLAS thread count does. Run hashes for an L6 60 Myr seed 1: numba 16 / BLAS 1 = numba 8 / BLAS 1 = `38f26d4e2106`; numba 16 / BLAS 8 = `504e19b80084` (each reproducible). The L4 golden passed at BLAS 8 and 48 but failed at 1 and 2. The matrix products in the simulation (mantle harmonics `Y @ ...` and its SVD, plate rotations, `linalg.solve` in the plate motion) split their sums by thread. OpenBLAS defaults to one thread per core, so outputs depended on the machine (8 threads on the Mac, 48 here), and sequential and parallel scorecards disagreed (seed 1 @ 500 Myr: dry 18.2% against 30.8%).

The parallel branch now always sets OPENBLAS/OMP/MKL_NUM_THREADS=1 (`parallel.set_default_threads`, applied when `planet` is imported; tools now import `planet` before numpy), and regenerated `tests/golden/sim_L4_s1_60myr.json`. One BLAS thread is also faster (L6 100 Myr: 41 s and 115 s of CPU, against 44 s and 410 s).

Left for the coordinator:
- [ ] Runs made before the merge were made at BLAS = cores. Slicing them from keyframes (`world_from_frame`, the default) is unaffected, but a replay (`planet slice` from a checkpoint) will now report ReplayMismatch. Remake or delete runs that need replays (no backward compatibility).
- [ ] Scorecard lines before the merge aren't comparable bit for bit with later ones (it's a statistical record, so this is probably fine). Note the break in `docs/scorecard.jsonl` or in coordination.md.

## Updates
- 2026-10-15: Created from inbox draft draft-blas-threads-change-outputs.md (found by parallel).
