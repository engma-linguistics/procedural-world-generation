---
id: PW-480
title: planet make jobs cannot be cancelled and restart from scratch after a server restart
type: task
status: done
parent: PW-244
milestone: v1
subsystem: infra
effort: s
impact: med
found_by: agent-make-ui
blocked_by: []
relates: [PW-248, PW-472]
refs: [planet/make.py, planet/api.py, planet/server.py]
created: 2026-10-20
updated: 2026-10-21
---

## Description
`make.make` is one job on the server's queue. Two gaps:
- **Restart:** `api.Jobs` queues an interrupted job again after a server restart, and `make` then starts at the simulate stage again, so a 6 minute (L6) or 30+ minute (L7) run is thrown away and a second run is left half made (or finished and orphaned). Fix: record the stage results in the job (`run`, `timezoom`, `world` as they appear, e.g. through `progress` extras or a small state file under `.jobs/`) and skip stages whose output exists; `T.simulate` itself cannot resume, so at least a finished run is reused.
- **Cancel:** there is no way to stop a job from the viewer (no `DELETE /api/jobs/<id>`; the pool worker would have to be killed, `parallel.Pool`). A wrong L7 submit costs 30 minutes of a worker slot.
- [ ] make resumes at the first missing stage after a restart
- [ ] a Cancel button on the progress panel (and the start-screen banner), partial outputs kept or removed as the owner prefers (partial planets are listed in the gallery meanwhile)

## Updates
- 2026-10-21: Status todo -> done. Done on branch worktree-agent-a0fc90d9213631395: DELETE /api/jobs/<id> (cooperative: flag file, worker raises api.Cancelled at its next progress report; queued jobs never start), Cancel buttons in the start screen, navigator and globe zoom box; make jobs record finished stages (.jobs/<port>.d/<job>.state.json) and a restarted job resumes at the first unfinished stage (tested live: server killed during a time zoom, restart reused the run). A restart during the simulation still redoes it, and cancel waits for the next progress report: inbox drafts.
- 2026-10-20: Created from inbox draft draft-make-resume-cancel.md (found by agent-make-ui).
