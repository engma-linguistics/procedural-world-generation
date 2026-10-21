---
title: A restart during the tectonic simulation of a make job still starts the simulation over; resume from the last checkpoint
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: viewer-batch
blocked_by: []
relates: [PW-480, PW-248]
refs: [planet/timeline.py, planet/make.py, planet/store.py]
---

## Description
PW-480 made a restarted `make` job reuse a finished run, time zoom and world (`make.make(state=, resume=)`), but `timeline.simulate` cannot resume, so a server restart in the middle of an L7 run (30+ min per Gyr) still throws the run away. Runs already write checkpoints (`store.save_checkpoint`, every `CHECKPOINT_EVERY` Myr, used by the time zoom and `slice`). The half-run's folder is deleted by `simulate`'s `except BaseException` only on an exception, so after a hard kill it is left as a run directory without `run.json`.
Idea: `make` records the run id it is about to create (needs `simulate` to accept a `run_id`) in its state file before starting; on resume, if checkpoints exist for it, `Simulation` restarts from the last one and carries the already-collected keyframes (they are encoded as the run goes: `data`/`frames` are held in memory only, so they would also have to be checkpointed, or re-derived by replaying).
Check first how much of the keyframe history the checkpoints can regenerate; if none, this is the bigger job (write keyframes incrementally). Also: `planet delete --orphans` should clear the leftover directory from a killed run (check that it does).
- [ ] a killed L5 make resumes mid-run and the finished run is identical to an uninterrupted one (golden-style check)
