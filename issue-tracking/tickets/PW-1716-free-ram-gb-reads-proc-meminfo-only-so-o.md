---
id: PW-1716
title: free_ram_gb reads /proc/meminfo only, so on macOS every RAM guard (zooms, tiles, refine) is silently off
type: task
status: todo
parent: null
milestone: v1.0
subsystem: infra
effort: s
impact: med
found_by: plan-v1-lane
blocked_by: []
relates: [PW-1678]
refs: ["planet/api.py::free_ram_gb", planet/tiles.py, planet/api.py, docs/review/plan/milestones-to-v1.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: on a Mac the program can't tell how much memory is free, so it starts big jobs that can run the machine out of memory.

`planet/api.py::free_ram_gb` reads Linux's MemAvailable and returns None where it can't. The installer targets macOS as best effort, and the run-cost table was measured on a Mac laptop. If this is never done, a Mac user's level-1 tile build (8.3 GB, planet/tiles.py), a refine or a regional zoom starts with no check and can swap or kill the machine.

Fix: on macOS, read `sysctl hw.memsize` plus `vm_stat` (free + inactive + purgeable pages). Elsewhere, refuse heavy jobs with a clear message instead of running them unguarded.

- [ ] free_ram_gb returns a number on macOS, checked against Activity Monitor within ~10%
- [ ] Where it can't read memory, heavy jobs refuse with a message instead of running unguarded; there is a test for the None path

## Updates
- 2026-11-11: Created from inbox draft draft-free-ram-macos.md (found by plan-v1-lane).
