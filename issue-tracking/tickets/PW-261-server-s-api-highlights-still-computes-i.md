---
id: PW-261
title: Server's /api/highlights still computes in the server process
type: task
status: in-progress
parent: PW-247
subsystem: infra
effort: s
impact: low
found_by: parallel
blocked_by: []
relates: [PW-250]
refs: [planet/api.py, planet/server.py, planet/parallel.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Since the parallel branch, the server's jobs (zooms, time zooms, finished worlds) run in worker processes (`parallel.Pool`, `planet serve --jobs J`), but `GET /api/highlights` still slices the run (if needed) and computes the highlights in a server thread, under `api.COMPUTE`. Two such requests at once wait for each other, and under the workqueue layer they must. It's a few seconds at L6, so it rarely matters; at L7/L8 a first highlights request on a new keyframe could take tens of seconds.

What to try: send the computation to the server's pool (`pool.call(H.for_world, ...)` through a small module-level wrapper), keeping the cached-only path in the server process. The file locks (`store.lock`) already keep a worker and the server from building the same slice or highlights twice.
- [ ] two highlights requests for different worlds compute at once, without blocking file serving

## Updates
- 2026-10-15: Status todo -> in-progress. Infra batch agent started 2026-10-15 night.
- 2026-10-15: Created from inbox draft draft-highlights-in-worker.md (found by parallel).
