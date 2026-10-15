---
title: "PW-258 remainder: checkpoints are written in the background now; init caching still open"
type: task
status: todo
parent: PW-247
subsystem: store
effort: s
impact: low
found_by: worktree-agent-abb4e9e7307244dd3 (PW-256/257)
blocked_by: []
relates: [PW-258]
refs: [planet/store.py, planet/timeline.py, planet/tectonics/mantle.py]
---

## Description
Meant to be merged into PW-258 (`board.py intake --merge-into PW-258`).
Done on branch worktree-agent-abb4e9e7307244dd3: `store.CheckpointWriter` pickles, compresses and
writes each checkpoint on one background thread (`sim.state()` is already a deep copy; the run waits
for the previous write before the next and for the last one before it finishes; an error is raised
on the run's thread). Measured (Threadripper, early-run state): the run's main thread pays 0.02 s
(L6) / 0.08 s (L7) per checkpoint instead of 0.46 s / 1.8 s; outputs bit-identical. Too small to see in
a single 100 Myr run's wall time (one checkpoint, at the end).
Still open from PW-258: cache `mantle.basis` / the grid per level on disk (~1 s L6, ~4 s L7 per
process), and computing the snapshot's landforms only for keyframes that need them.
