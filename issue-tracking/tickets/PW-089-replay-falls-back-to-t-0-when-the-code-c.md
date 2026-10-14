---
id: PW-089
title: Replay falls back to t=0 when the code changed
type: task
status: todo
parent: null
subsystem: store
effort: m
impact: low
found_by: store
blocked_by: []
relates: []
refs: [planet/store.py, planet/timeline.py, planet/provenance.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
When the source hash differs from the run's, slicing ignores checkpoints and replays from t=0, so slices of
older runs take minutes, or fail with ReplayMismatch unless `--force`. With "no backward compatibility"
this mostly means: make the message clear and suggest re-running or `--force`.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Infrastructure.
