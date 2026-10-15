---
id: PW-088
title: Checkpoints are big (~23 MB each at L6)
type: task
status: wontdo
parent: null
subsystem: store
effort: m
impact: low
found_by: store
blocked_by: []
relates: []
refs: [planet/store.py, planet/tectonics/simulation.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
A level-6 checkpoint is ~23 MB (≈229 MB per 1 Gyr run, about as much as the layers); L7/L8 much more.
Saving only live plates' slots (dead plates keep full-grid arrays) would shrink them.

## Updates
- 2026-10-14: Status todo -> wontdo. Merged into PW-131 (the concrete checkpoint fix).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Infrastructure.
