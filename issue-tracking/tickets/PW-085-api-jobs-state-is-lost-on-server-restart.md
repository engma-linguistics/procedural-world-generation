---
id: PW-085
title: api.Jobs state is lost on server restart
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: low
found_by: viewer2
blocked_by: []
relates: []
refs: [planet/api.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
`api.Jobs` keeps job state in memory only, so a server restart loses running/finished jobs and the
viewer's progress polling breaks. Low value unless restarts become common.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Infrastructure.
