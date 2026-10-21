---
id: PW-500
title: "Job cancel is cooperative: a worker busy in a long kernel only stops at its next progress report"
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: s
impact: low
found_by: viewer-batch
blocked_by: []
relates: [PW-480]
refs: [planet/api.py, planet/parallel.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
`DELETE /api/jobs/<id>` (PW-480) marks the job cancelled at once and touches a flag file; the worker process raises `api.Cancelled` from its next progress report (`api.any_job` wraps the progress callback). The tectonic run reports every keyframe (about every 4 Myr), the zoom/time zoom/finish stages report between their steps, so a cancel usually lands within seconds, but a single long step with no report (an L7 finish, a big zoom's landscape pass) runs to its end first and holds its worker slot meanwhile. A hard stop is not possible with the shared `ProcessPoolExecutor`: killing one worker breaks the whole pool and fails the other running jobs.
Options: (A) leave it; (B) give cancellable jobs (make at L6+) a process of their own that can be killed (a `Pool` of one per job, or `multiprocessing.Process` per make job), keeping the pool for short jobs; (C) more progress reports inside the long kernels. Lean: A until someone cancels an L7 run and waits; then B for make only.
- [ ] measure the longest gap between progress reports per stage at L6/L7

## Updates
- 2026-10-21: Created from inbox draft draft-cancel-hard-stop.md (found by viewer-batch).
