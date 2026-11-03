# Memory fixes, round 1: checkpoints and empty plate slots (PW-1390, PW-1389; lane 147, 2026-11-03)

From `docs/review/speed/l9-memory.md`. Both fixes leave every output bit-identical.

## In plain words
- **Checkpoints (PW-1390).** Every 50-100 Myr the run saves its full state so a slice can start nearby instead of
  from t=0. It used to copy the whole state first, every plate's full-globe arrays in all 48 slots, and only then
  throw most of the copy away while saving. Now it packs the live state directly, keeping only the plate cells
  something reads. The saved file reads back exactly as before. This was the bigger win:
  **L6 peak memory 2.45 -> 1.50 GB (-39%)**, L7 below.
- **Empty plate slots (PW-1389).** Each plate keeps arrays the size of the whole planet, 48 slots of them, and
  a slot whose plate has died kept its old crust in memory. The arrays now sit on memory the system only hands out
  once something is written, and a dead plate's rows are handed back at the end of each step. Slots never used
  cost nothing. Plate memory actually used at L6 (seed 7, 200 Myr): **195 -> 77 MB**; run peak
  **1.50 -> 1.34 GB**. The layout and the code that reads the plates are unchanged.
- Together, L6 seed 7 300 Myr: **2.45 -> 1.34 GB peak (-45%)**. L7 seed 7 200 Myr: **6.80 -> 4.41 GB (-35%)**.
- Still to do (see the inbox drafts): keyframes held in RAM (PW-801) are now the largest avoidable item; the
  plates still keep a full-globe copy per live plate (sparse storage would need a refactor across ~8 modules,
  `needs-decision` draft); old runs' checkpoints no longer load and their slices replay from t=0 (draft).

## Measured (`/usr/bin/time -v`, `planet simulate --seed 7 --checkpoint-every 50 --threads 4`, two runs at once)

| Run | main cfd7d1cf | PW-1390 only | PW-1390 + PW-1389 |
|---|---|---|---|
| L6, 300 Myr | 2.45 GB, 6:43 | 1.50 GB, 6:12 | 1.34 GB, 5:18 |
| L7, 200 Myr | 6.80 GB, 12:40 | - | 4.41 GB, 12:40 |

Wall times are under varying machine load: not a speed claim.

Plate arrays at L6 (n = 40,962; 10 plates alive at 200 Myr, at most 17 at once; mincore residency):

| | allocated | resident before | resident after |
|---|---|---|---|
| crust columns + owned | 287 MB | 179 MB | 61 MB |
| cell map `idx` (kept full: the golden digest hashes it) | 16 MB | 16 MB | 16 MB |

## Bit-identity evidence
- Same seed, same command on main (a `git archive` of cfd7d1cf, run with this venv) and on the branch, data root
  redirected with `PLANET_DATA` into the lane's scratch dir.
- Done at L6 (300 Myr) and L7 (200 Myr, 16 rifts, 10 plates absorbed, 4 checkpoints): same result at both.
- Every file of the run byte-identical by SHA-256 (all 45 layer files, `volcanoes.json.gz`), `run.json` equal but
  for `created` / `generated_in_s`, `run.txt` but for the run id and time.
- Every checkpoint (6 at L6, at 50..300 Myr) read back with its own code and compared entry by entry (12-46k
  entries each: every array's dtype, shape and bytes; every scalar, list and dict): identical.
- The L6 run had 26 rifts, 17 plates absorbed, 7 sutures: slots died and came back.
- A slice at 160 Myr (replayed from the 150 Myr checkpoint, so through `read_checkpoint` and the new
  `Plates.mapped_copy`) gives the same world file as main's, but for ids, times and code hashes.
- `tests/test_golden.py` passes unchanged (no `--update-golden`).

One catch found on the way: a first version handed a plate's rows back the moment it died, and volcano records
changed from ~120 Myr on. `volcanism.re_home` reads the dead plate's swell under its volcanoes later in the
same step, before moving them to the plate that took them over. The rows are now handed back after
`volcanism.tend`, at the end of the step, and the runs match again.

## How
- `store.pack_state` (called by `save_checkpoint` on the live simulation) copies the plain state once, and of the
  plates only: the small per-slot fields, `owned` and the keep-mask as bits, each crust column on the kept cells
  (`store._keep`: owned cells, cells the world view samples, volcano cells, the same set `shrink_state` kept),
  and `idx` as int32. On the writer thread `pack_idx` turns `idx` into the few cells where it differs from a fresh
  `grid.locate`. `unpack_state` rebuilds full arrays: exactly `shrink_state(state)`.
- `plates._mapped`: a zeroed array on its own private anonymous `mmap`; `Plates.release_dead` (end of each step)
  `madvise(MADV_DONTNEED)`s the whole pages of each dead slot's rows. Correct whatever the OS does with that:
  nothing reads a dead slot's crust after the step it died in, because a slot only comes back through
  `events.split`, which copies the parent's whole frame in. `Plates.empty` writes the blank record only into the
  slots `setup` fills; `Simulation.load_state` puts plates back with `Plates.mapped_copy` (live rows only).
- Tests: `test_store.py::test_checkpoint_reads_back_as_shrunk_state`, `test_state.py::test_dead_plate_slots_cost_no_memory`;
  the existing checkpoint round-trip tests now go through `pack_state`.
