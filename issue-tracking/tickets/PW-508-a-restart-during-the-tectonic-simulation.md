---
id: PW-508
title: A restart during the tectonic simulation of a make job still starts the simulation over; resume from the last checkpoint
type: task
status: todo
parent: null
milestone: v1
subsystem: tectonics
effort: m
impact: med
found_by: viewer-batch
blocked_by: []
relates: [PW-480, PW-248]
refs: [planet/timeline.py, planet/make.py, planet/store.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-21
updated: 2026-10-29
---

## Description
PW-480 made a restarted `make` job reuse a finished run, time zoom and world (`make.make(state=, resume=)`), but `timeline.simulate` cannot resume, so a server restart in the middle of an L7 run (30+ min per Gyr) still throws the run away. Runs already write checkpoints (`store.save_checkpoint`, every `CHECKPOINT_EVERY` Myr, used by the time zoom and `slice`). The half-run's folder is deleted by `simulate`'s `except BaseException` only on an exception, so after a hard kill it is left as a run directory without `run.json`.
Idea: `make` records the run id it is about to create (needs `simulate` to accept a `run_id`) in its state file before starting; on resume, if checkpoints exist for it, `Simulation` restarts from the last one and carries the already-collected keyframes (they are encoded as the run goes: `data`/`frames` are held in memory only, so they would also have to be checkpointed, or re-derived by replaying).
Check first how much of the keyframe history the checkpoints can regenerate; if none, this is the bigger job (write keyframes incrementally). Also: `planet delete --orphans` should clear the leftover directory from a killed run (check that it does).
- [ ] a killed L5 make resumes mid-run and the finished run is identical to an uninterrupted one (golden-style check)

## Updates
- 2026-10-29: Owner 10-29: reliability bugs come into v1.
- 2026-10-29: Merged inbox draft draft-run-interrupt-keeps-checkpoints.md ("A crash or Ctrl-C during a run deletes the whole run folder, checkpoints included", found by code-audit-2026-10).
  In plain words. If a long simulation is stopped near the end (a crash, a cancelled job, Ctrl-C), the code deletes everything it wrote, including the saved checkpoints that a future "resume" could restart from. Hours of work go.
  
  Verified on main b36c9581: `timeline.py:155-163` wraps the run in `except BaseException: shutil.rmtree(out, ignore_errors=True)`. BaseException includes KeyboardInterrupt and SystemExit. run.json is written only at the end.
  
  Fix, as part of the resume work rather than a stopgap: write run.json's header with `"status": "running"` at the start, keep the folder on interrupt (`delete --orphans` and `cleanup_outputs` already clear unfinished runs), and later stream keyframes to preallocated `.bin` files (PW-801). Coordinator: consider `intake --merge-into PW-508` if that lane is close.
  
  Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Milestone null -> v1 (PW-597 triage, coordinator, 2026-10-23): a real bug in a v1 feature (a make-job restart redoes the tectonic simulation).
- 2026-10-21: Created from inbox draft draft-simulate-resume-checkpoint.md (found by viewer-batch).
