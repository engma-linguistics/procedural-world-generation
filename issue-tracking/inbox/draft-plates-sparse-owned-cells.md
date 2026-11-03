---
title: "Plates: keep only live slots' rows (or owned cells sparsely) instead of 48 full-globe slots"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: low
found_by: lane 147
blocked_by: []
relates: [PW-1389, PW-1390, PW-801]
refs: [planet/tectonics/plates.py, planet/tectonics/plate_kernels.py::resolve, planet/tectonics/plate_kernels.py::cleanup_ghosts, planet/tectonics/events.py::merge, planet/tectonics/events.py::split, planet/tectonics/volcanism.py::re_home, planet/tectonics/crust.py, planet/tectonics/setup.py, planet/tectonics/simulation.py::_world_view, planet/store.py::pack_state, tests/test_golden.py::sim_digest, docs/review/speed/memory-fixes/round1.md, docs/review/speed/l9-memory.md]
---

## Description
In plain words: lane 147 (PW-1389) stopped the plates' empty slots from costing memory without changing the
code's layout: the per-plate arrays now sit on memory the system only hands out once written, and a dead
plate's rows are handed back at the end of each step. At level 6 the plates' memory went from 195 MB to
77 MB actually used (303 MB reserved). What is left: every live plate still keeps a full-globe copy, though it
owns crust on only ~2% of the cells it carries, and the cell map `idx` (48 x cells, int64) stays full because the
golden test hashes it, dead slots included. The bigger win (~0.5 GB at L9 instead of a few GB) needs the
plates' storage changed, and that touches about eight modules, so it needs Daniel's yes (refactor policy).

Options:
- A. Row indirection: the (P, n) arrays become (rows, n) with `Plates.row[slot]`; every `pl.X[k, ...]` turns
  into `pl.X[pl.row[k], ...]` (simulation.py world view / write-back, the two numba kernels in
  plate_kernels.py, events.py merge/split/absorb, volcanism.py, crust.py, setup.py, store.py, ~40 sites, plus
  tests that index plates by slot). Same values, so bit-identical; saves little beyond what PW-1389 already gets
  (live rows are what is resident now), so on its own **not worth it**.
- B. Sparse owned cells: each plate keeps only the cells it owns plus the ones the world view samples (a
  per-plate sorted cell list + packed columns, rebuilt on merge/split/resolve). ~20x less plate memory at any
  level; touches the same sites as A plus resolve's "fill a new cell" logic; bit-identical only if every read of
  an unowned-but-viewed cell is kept (store._keep lists them: owned, the view's cells, volcano refs). Effort l.
- C. Leave it: after PW-1389/1390 the plates are ~6% of an L6 run's peak; keyframes (PW-801) are the big item.

Lean: C for now, B only if L8/L9 from-scratch runs become a goal (Daniel prefers refine for those). Also
possible cheaply: `idx` as int32 (halves 384 B/cell) if the golden digest is allowed to hash it as int64 still
(hash `idx.astype(np.int64)`): no output changes.
