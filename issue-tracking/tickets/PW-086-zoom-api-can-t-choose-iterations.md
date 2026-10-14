---
id: PW-086
title: Zoom API can't choose iterations
type: task
status: todo
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
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Infrastructure (seed and res_km part done).
