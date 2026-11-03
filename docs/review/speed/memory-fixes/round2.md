# Memory fixes, round 2: keyframes go to disk as the run makes them (PW-801; lane 154, 2026-11-03)

From `docs/review/speed/l9-memory.md`, after round 1 (`round1.md`). Every output stays bit-identical.

## In plain words
- **What was wrong.** A run keeps a viewer keyframe (44 map layers plus the volcano list) every few million years.
  It used to hold every keyframe in memory until the very end, then make one more full copy of them all to write
  the files. So memory grew all run long and jumped at the end.
- **What changed.** Each keyframe is now written straight into its layer files the moment it is made, and the
  volcano list is compressed into its file as it goes. Nothing piles up, and there is no copy at the end. The files
  on disk are the same, byte for byte.
- **What it buys** (same seed, same command, main at ceda2abc against this branch):
  **L6 1 Gyr: 2.74 -> 1.09 GB peak (-60%)**; **L7 400 Myr: 4.81 -> 3.36 GB (-30%)**;
  **L7 1 Gyr: 7.94 -> 3.43 GB (-57%)**. An L7 Gyr now fits an 8 GB machine, the ticket's goal (under ~4-5 GB).
- **Bonus for stopped runs.** Before, a run stopped by Ctrl-C or an error lost all its keyframes (only the
  checkpoints were kept). Now the keyframes written before the stop stay on disk and readable. A run killed outright
  (power cut, `kill -9`) is marked interrupted as before; its partial files are cleaned up with it.

## Measured (`/usr/bin/time -v`, `planet simulate --seed 957317 --threads 4`, main and branch side by side, each pinned to 4 cores)

| Run | main ceda2abc | this branch | change |
|---|---|---|---|
| L6, 1000 Myr (268 keyframes) | 2.74 GB, 9:08 | 1.09 GB, 8:39 | -60% |
| L7, 400 Myr (118 keyframes) | 4.81 GB, 21:55 | 3.36 GB, 26:12 | -30% |
| L7, 1000 Myr (268 keyframes) | 7.94 GB, 40:43 | 3.43 GB, 48:43 | -57% |

The baseline is main on the same seed and command, run at the same time, not the older numbers in the ticket (those
came before round 1). Wall times vary with load and with which cores each run got: not a speed claim. The L6 pair
ran unpinned (~10 cores each for 9 min, over this lane's 8-core budget); the L7 pairs were pinned to 4 cores each.

Memory over the L7 1 Gyr pair (`ps` every 30 s; samples miss short peaks such as main's final stacking):

| minutes in | 0 | 9 | 19 | 29 | 39 | end (peak) |
|---|---|---|---|---|---|---|
| main | 1.39 GB | 2.71 | 3.89 | 4.51 | 5.43 | 7.94 |
| branch | 1.38 GB | 1.92 | 2.45 | 2.22 | 2.50 | 3.43 |

Main climbs ~0.1 GB a minute with its keyframes and then stacks them all at the save; the branch stays level
(highest sample 2.79 GB; its peak is the climate and checkpoint moments, not keyframes).

## Bit-identity evidence
- Same seed and command on main (a `git archive` of ceda2abc, run with this venv) and on the branch, the data root
  redirected with `PLANET_DATA` into the lane's scratch dir; nothing written into `runs/` or `worlds/`.
- L6 1 Gyr, L7 400 Myr, L5 400 Myr (checkpoints every 20 Myr) and L7 1 Gyr: in every pair all 44 layer files and
  `volcanoes.json.gz` are byte-identical by SHA-256; `run.json` is equal but for the id, `created`,
  `generated_in_s` and the code hash; `run.txt` differs only in the run id on the replay line.
- Checkpoints: byte-identical at L7 and L5. At L6 the ten checkpoint pickles differ in a few bytes (pickle reuses a
  repeated numpy dtype object differently, a memo detail), but read back and compared entry by entry (25-49k entries
  each: every array's dtype, shape and bytes; every scalar, list and dict) they are identical. The simulation state
  is untouched by this change; the checkpoint code is not.
- `tests/test_golden.py` passes unchanged (no `--update-golden`).
- The streamed gzip is the same bytes as `gzip.compress(..., 6)`: zlib's deflate does not depend on how its input
  is chunked, and the header gets the same mtime 0 and OS byte 255 that `gzip.compress` writes.

## Stopped runs (PW-508's interrupted-run handling), checked by CLI at L5 400 Myr
| How stopped | main | this branch |
|---|---|---|
| Ctrl-C (SIGINT) at ~150 Myr | header "interrupted", checkpoints kept, no layer files, no volcano file | header "interrupted", checkpoints kept, header also lists `layers` and `frames`: 38 whole keyframes (to 148 Myr) that `timeline.load_frames` reads; each layer file exactly 38 frames long; no volcano file, no temp files left |
| `kill -9` | header "running", process gone, so "interrupted" | the same; the 44 partial layer files and a hidden `.volcanoes.json.gz.*.tmp` are left in the folder; `store.orphans()` lists the run and `delete_orphans` removes the whole folder |

An interrupted run is still not listed, found or reused (`store.run_status`), as before: the readable keyframes
are there for a future resume (PW-508) or for a look by hand.

## How
- `store.LayerStream(out, specs)`: opens `layers/<name>.bin` per run layer; `append(name, frame)` casts the encoded
  frame to the spec's little-endian dtype and writes it; `layers()` gives exactly `write_layers`' metadata (shared
  `_layer_meta`), so `run.json` is unchanged. `close(frames=n)` cuts every layer back to the whole keyframes all
  layers have (a Ctrl-C can land between two layers of one keyframe).
- `store.VolcanoStream(run_dir, columns)`: writes the same JSON text in pieces into a `zlib.compressobj(6, wbits=31)`
  under a hidden temporary name, patches the gzip header like `gzip.compress` and renames it into place at
  `finish()`; `abort()` drops it.
- `timeline.simulate`: `keep` appends to the two streams instead of to `data` / `vframes`; at the end the streams
  close instead of `np.stack` + `write_layers` + `write_volcanoes`. On an exception the volcano file is dropped, the
  layers are cut to whole keyframes and the interrupted header records `layers` and `frames`.
- The frame stats list (`frames`, small) still lives in memory: it goes into `run.json`.
- Tests: `test_store.py::test_streamed_keyframes_match_stacked` (stream vs stacked writers, byte for byte, and a
  stream cut part-way through a keyframe); `test_interrupted_run_keeps_its_folder` now also reads the keyframes
  back.

## What is left
- Keyframes no longer count against memory. What is left at L7 (~2-3.4 GB) is the run's own state (the plates'
  full-globe copies, the `needs-decision` draft from round 1), the climate update's temporaries
  (`l9-memory.md`: ~1.6 GB at L7) and the short checkpoint packing.
- PW-508 (resume an interrupted run) no longer has to re-create keyframes: they are on disk up to the stop. A resume
  would reopen the layer files in append mode, cut them back to the last checkpoint's keyframe, and restart from that
  checkpoint (`frames` in the interrupted header gives the times).
