---
id: PW-543
title: "Leaked multiprocessing workers: idle spawn_main python processes survive their parent (11 found, ~20 GB, up to 22 h old)"
type: task
status: done
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
- 2026-10-21: Status todo -> done. Pool workers now run a parent-pid watchdog (planet/parallel.py) and exit when the parent dies; serve() closes both pools on any failure; test_parallel_orphans.py SIGKILLs a pool parent and checks the workers go
- 2026-10-21: Created.
