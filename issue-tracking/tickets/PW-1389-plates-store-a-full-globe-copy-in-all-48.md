---
id: PW-1389
title: "Plates store a full-globe copy in all 48 slots: allocate alive slots only, or store owned cells sparsely"
type: task
status: done
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: low
found_by: speed report 11-03
blocked_by: []
relates: [PW-801]
refs: [docs/review/speed/l9-memory.md, planet/tectonics/plates.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: each plate keeps arrays the size of the whole planet, for all 48 plate slots (plates.py:19, 101-103), though in an L6 count only 14 slots were alive and 2.1% of slot-cells held crust. That is ~90% of a run's memory (7.4 of 8.2 kB per cell): 1.2 GB at L7, ~19 GB at L9 (estimate). Alive-only slots cut it ~3x; sparse owned cells to ~0.5 GB at L9. Outputs should stay bit-identical. See docs/review/speed/l9-memory.md.

## Updates
- 2026-11-03: Status todo -> done. Merged 3cf50fdd (lane 147): per-plate arrays on private memory maps, dead slots released with madvise at step end (Plates.release_dead). Bit-identical. With PW-1390: L6 2.45 -> 1.34 GB, L7 200 Myr 6.80 -> 4.41 GB peak. Sparse owned cells left as PW-1409.
- 2026-11-03: Created.
