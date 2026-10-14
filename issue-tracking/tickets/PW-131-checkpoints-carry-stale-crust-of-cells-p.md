---
id: PW-131
title: Checkpoints carry stale crust of cells plates no longer own (~3x their size); volcanoes read it
type: task
status: todo
parent: null
subsystem: store
effort: s
impact: low
found_by: landform
blocked_by: []
relates: []
refs: [planet/store.py, planet/tectonics/volcanism.py, "run 3a4f07"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Each plate keeps its crust on its own copy of the whole grid, and cells its
crust has left keep their old values. Only ~9% of the live plates' cells are
owned (L7 run 3a4f07 at 400 Myr), so a checkpoint is mostly stale data that
compresses badly: at L7 `extra` is 37.6 MB compressed, 6.0 MB with unowned
cells zeroed; thick, cover, age likewise. The landform branch zeroes only the
new record (rec, lith: 31.9 -> 4.7 MB) in `store.save_checkpoint`, because
zeroing all crust columns broke bit-identical replay: `volcanism.base_level`
reads `plates.extra[k, v["ref"], LIFT]` for a volcano whose crust cell may
no longer be owned (its plate subducted or lost that cell), i.e. a stale
swell. Decide what a volcano on lost crust should read (the world cell under
it, or nothing: forget it), then zero all unowned crust in checkpoints.
L7 checkpoints are 90-170 MB each now (run 3a4f07: 1.4 GB for 10).

## Updates
- 2026-10-14: Created from inbox draft draft-checkpoint-unowned-cells.md (found by landform).
