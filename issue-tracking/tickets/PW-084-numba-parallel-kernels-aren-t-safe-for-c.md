---
id: PW-084
title: Numba parallel kernels aren't safe for concurrent calls from threads
type: task
status: done
parent: null
subsystem: infra
effort: s
impact: low
found_by: perf
blocked_by: []
relates: []
refs: [planet/api.py, planet/kernels.py, planet/climate.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Parallel numba kernels (climate, `kernels.locate`) aren't safe for concurrent calls from several Python
threads. The API runs one job at a time and has a slicing lock, but highlights requests can run alongside
the zoom worker. Add one compute lock around kernel-heavy work in `api.py`, or document the rule.

## Updates
- 2026-10-15: Status todo -> done. Merged (smalls).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Infrastructure.
