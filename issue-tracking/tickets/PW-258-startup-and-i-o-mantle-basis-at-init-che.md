---
id: PW-258
title: "Startup and I/O: mantle basis at init, checkpoint writes on the main thread (~2-5% of a 100 Myr run)"
type: task
status: in-progress
parent: PW-247
subsystem: store
effort: s
impact: low
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249]
refs: [planet/tectonics/mantle.py, planet/store.py, planet/timeline.py, docs/review/gpu/profile.md]
created: 2026-10-15
updated: 2026-10-15
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

## Updates
- 2026-10-15: Status todo -> in-progress. Infra batch agent started 2026-10-15 night.
- 2026-10-15: Checkpoint part done (82f4830: background CheckpointWriter, 0.46/1.8 s -> 0.02/0.08 s per checkpoint at L6/L7 on the main thread); startup remainder open.
- 2026-10-15: Merged inbox draft draft-startup-io-remainder.md ("PW-258 remainder: checkpoints are written in the background now; init caching still open", found by worktree-agent-abb4e9e7307244dd3 (PW-256/257)).
  Meant to be merged into PW-258 (`board.py intake --merge-into PW-258`).
  Done on branch worktree-agent-abb4e9e7307244dd3: `store.CheckpointWriter` pickles, compresses and
  writes each checkpoint on one background thread (`sim.state()` is already a deep copy; the run waits
  for the previous write before the next and for the last one before it finishes; an error is raised
  on the run's thread). Measured (Threadripper, early-run state): the run's main thread pays 0.02 s
  (L6) / 0.08 s (L7) per checkpoint instead of 0.46 s / 1.8 s; outputs bit-identical. Too small to see in
  a single 100 Myr run's wall time (one checkpoint, at the end).
  Still open from PW-258: cache `mantle.basis` / the grid per level on disk (~1 s L6, ~4 s L7 per
  process), and computing the snapshot's landforms only for keyframes that need them.
- 2026-10-15: Created from inbox draft draft-startup-and-checkpoint-io.md (found by gpu-explore (PW-249)).
