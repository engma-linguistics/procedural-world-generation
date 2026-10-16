---
id: PW-306
title: "Checkpoints: plates.idx is now the largest field (~25%); store it as its residual from grid.locate"
type: task
status: todo
parent: null
subsystem: store
effort: xs
impact: low
found_by: small-store
blocked_by: []
relates: [PW-131, PW-088]
refs: [planet/store.py, planet/timeline.py, planet/tectonics/plates.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After PW-131 zeroed the plates' unowned crust, the biggest field of a checkpoint is `plates.idx`
((P, n) int64, the plate cell under each world cell: a rotated nearest-neighbour map, which zlib
can't compress): L6 seed 1 at 200 Myr, 3.6 of ~13 MB. It is `grid.locate(grid.centers @ Q[k])`
(Plates.move, with the last step's idx as a warm start), so storing `idx - locate(centers @ Q[k])`
(L6 40 Myr: 0 mismatches over 7 live plates, residual 0.009 MB vs 1.37 MB) and adding it back on
load is exact whatever the warm start did. Needs the grid at load: `store.load_checkpoint(run_dir,
t)` has none, so pass it from `timeline.replay` (outside the PW-131 batch's files).

## Updates
- 2026-10-15: Created from inbox draft draft-checkpoint-plate-idx.md (found by small-store).
