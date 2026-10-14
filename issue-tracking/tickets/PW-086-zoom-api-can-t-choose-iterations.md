---
id: PW-086
title: Zoom API can't choose iterations
type: task
status: done
parent: null
subsystem: infra
effort: xs
impact: low
found_by: viewer2
blocked_by: []
relates: []
refs: [planet/api.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
`POST /api/zoom` accepts `seed` and `res_km` but not `iterations` (always the default 15). Add it.

## Updates
- 2026-10-14: Status in-progress -> done. POST /api/zoom now takes iterations (1..100, default 15), passed to zoom.zoom. Also fixed a latent collision: zoom_id didn't include iterations, so a CLI 'planet zoom --iterations 30' overwrote (and the API would have reused) the default zoom of the same box. The id now appends |itN when iterations != 15, so existing ids are unchanged. Tests in test_api. The running server needs a restart to pick it up.
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Infrastructure (seed and res_km part done).
