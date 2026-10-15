---
title: Slicing a run exactly at a checkpoint time fails the replay check (snapshot right after a checkpoint load differs)
type: task
status: todo
parent: null
subsystem: store
effort: s
impact: med
found_by: health-sweep
blocked_by: []
relates: [PW-246]
refs: [planet/timeline.py, planet/tectonics/output.py, planet/store.py, "run:cde55b@600Myr(18.30,101.65)"]
---

## Description
Found by the PW-246 health sweep (2026-10-15, main 6926583). `planet slice cde55b --at 600` (L6 seed 1,
1 Gyr, made minutes before by the same code) refuses: "replay at t=600 DOES NOT match the stored
keyframe". 600 is a checkpoint time, so `replay` loads the checkpoint and runs zero steps; the
snapshot then differs from the keyframe stored at that same moment in 2 cells of `elevation`
(plate, crust, ice and the frame stats all match):
- cell at (18.30, 101.65): stored 76 m, replay -5.5 m (continental);
- cell at (74.60, 144.22): stored -33 m, replay -491 m (continental).
Replays that run on from a checkpoint match exactly (100, 200 and 640 Myr from the 600 checkpoint
are bit-identical, and the sweep's determinism re-run is identical over 26 keyframes x all layers),
so the simulation state is restored right; something `snapshot()` reads (`sim.bed()` or
`w_trench`, or a cache) isn't in the checkpoint and is rebuilt only by the next step.
Effect: worlds can't be sliced at 100, 200, ... Myr without `--force` on some runs, and the viewer's
"Finish world here" at those times would fail the same way.
- [ ] find the field (compare `snapshot()` of a fresh `from_state` with the one taken in `keep`)
- [ ] store it in the checkpoint or rebuild it in `from_state`; a test slicing at a checkpoint time
