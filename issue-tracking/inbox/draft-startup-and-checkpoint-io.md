---
title: "Startup and I/O: mantle basis at init, checkpoint writes on the main thread (~2-5% of a 100 Myr run)"
type: task
status: todo
parent: PW-247
subsystem: store
effort: s
impact: low
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249]
refs: [planet/tectonics/mantle.py, planet/store.py, planet/timeline.py, docs/review/gpu/profile.md]
---

## Description
Cold-process costs (Python 3.14, 16 threads): imports ~0.15 s, `build_grid` 0.15 s (L6) / 0.5 s
(L7), `Simulation.__init__` 1.1-1.3 s (L6) / 4.3 s (L7, mostly `mantle.basis`), numba cache loading
on first calls ~0.3-1 s. So a run pays ~2 s (L6) / ~6 s (L7) once; and a slice/finish/zoom process
pays its own. I/O inside a run: `save_checkpoint` ~0.75 s each at L6, ~2.4 s at L7 (one per
100 Myr), keyframe encoding small (0.06 / 0.25 s per 100 Myr); the keyframe snapshot's own compute
(`landform.classify`, `koppen`, `jet_of`) ~1.3 s / 5 s per 100 Myr.

Ideas: cache `mantle.basis` (and the grid) per level on disk; write checkpoints from a background
thread (the arrays are copied anyway); compute the snapshot's landforms only for keyframes that
need them. Saves ~1-3% of a run, more for short jobs (a slice replays 40 Myr: init is ~10% of it).
