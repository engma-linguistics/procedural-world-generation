---
id: PW-543
title: "Leaked multiprocessing workers: idle spawn_main python processes survive their parent (11 found, ~20 GB, up to 22 h old)"
type: task
status: todo
parent: null
milestone: v1
subsystem: infra
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-10-21
updated: 2026-10-21
---

## Description
2026-10-21: 11 idle 'multiprocessing.spawn spawn_main' python processes from this repo (main venv and removed worktrees) were reparented to systemd --user, 1-2.5 GB each, swap full. Killed by PID. Find which pool (planet simulate / timezoom / zoom / pytest) is created without a context manager or terminate() on error/timeout/SIGTERM, and make workers exit when the parent dies (pool shutdown in finally, or a parent-alive check / PR_SET_PDEATHSIG in the initializer).

## Updates
- 2026-10-21: Created.
