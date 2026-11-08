# Binary world layers (PW-1209, lane 229)

## In plain words

A world used to be one big JSON text with every layer written out as numbers. At L8 that text was about 450 MB,
close to the longest text Chrome can read (537 MB), and an L9 world (about 1.8 GB) could not be opened at all.

Now a world is a small JSON header (about 0.2 MB: what it is, its summary, its legends, and a list of its layers)
plus one binary file per layer. Each layer is kept in the smallest number type that gives back exactly the values it
had: a biome id in one byte, a temperature rounded to 0.1 °C as a whole number of tenths in two bytes. The viewer
fetches the files side by side while the grid loads, and turns a layer back into numbers only when something reads it.

- **L9 opens now.** A synthetic L9 world (2.6 million cells) opens in 8-16 s and works: turning the globe holds
  60 fps, the flat map and the 3D relief work. You can refine to L9 from the viewer and open the result.
- **L8 opens faster**: about 2.2 s instead of 3.0-3.2 s, with half the JS heap (0.7 GB instead of 1.24 GB).
- **L7 looks and behaves the same**: the globe's mesh and colours are identical to before, byte for byte, and
  every layer holds the same numbers (the only difference: 0.0 where the old text said -0.0).
- **Files are half the size on disk**: an L7 world 110 MB → 50 MB, an L8 world 440 MB → 199 MB.
- **What is slow now is the grid file**, not the world: at L8 the grid's JSON is 1.0 s of the 2.2 s, at L9 it is most
  of the wait and most of the memory. That is a follow-up (inbox draft: binary grid files).

Old worlds in the old format do not open any more. `tools/worlds_to_binary.py` converts them in place, keeping their
ids (so their zooms, names, highlights and peoples runs stay attached), and checks every layer reads back the same.

## After merging (coordinator)

1. Convert the stored worlds, in place, keeping their ids: `uv run python tools/worlds_to_binary.py` (all worlds in
   the old format; or give ids). About 2 s per L7 world and 6 s per L8 one, one at a time; peak memory a few GB for
   an L8 world. Until then the viewer and every command that reads a world fail on old ones.
2. Restart the owner's server (port 8765): the Python side changed (the server reads world layers, `/api/jobs`).
3. Each converted world's header file changes, so caches keyed on it (highlights, the lineages' land goods) are
   worked out again the first time they are asked for.

## What Daniel sees

Nothing changes in how worlds look or behave. Worlds open sooner at L8, and L9 worlds open at all. The refine
control no longer says "the viewer cannot open an L9 world"; it says an L9 world opens slowly (10-20 s, about 4 GB
of the browser's memory). And when a refine is running and you reload the page (or open the viewer in a new tab, say
the next morning), the bar at the top shows its progress and time left straight away, as if this page had started it.

## Numbers

Headless Chrome 155 on the real GPU (the owner's setup), `tools/viewer_perf_globe.py`, warm gzip cache. Before: main
at 4ee652c2 served from a `git archive` copy with the worlds in JSON. After: this branch with the same worlds
converted. Same data: L7 world 783674 (164k cells), L8 world fb5e11 (655k cells, lane 104's refine), and a synthetic
L9 world (fb5e11 upsampled onto the L9 grid, `tools/synth_l9_world.py`). The machine was shared (load 17-23), so
times vary by ±20%.

| | L7 783674 before | L7 after | L8 fb5e11 before | L8 after | L9 synthetic before | L9 after |
|---|---|---|---|---|---|---|
| open, to first globe drawn | 1.16-1.21 s | 0.81-0.96 s | 2.97-3.13 s (3.56 cold) | 1.94-2.22 s (2.20 cold) | cannot open | 6.8-7.1 s |
| on the wire (gzipped): world | 18.3 MB | 13.1 MB (181 files) | 66.1 MB | 46.8 MB | (229 MB) | 158 MB |
| on the wire: grid | 7.9 MB | 7.9 MB | 32.0 MB | 32.0 MB | | 129 MB |
| on disk: world | 110 MB | 50 MB | 440 MB | 199 MB | 1.76 GB | 794 MB |
| JS heap after load (after a GC) | 315 MB | 180 MB | 1.24 GB | 0.69-0.70 GB | | 2.75 GB |
| renderer memory after load | 0.78 GB | 0.77 GB | 1.73 GB | 1.58 GB | | 3.65 GB |
| JS heap at the end of the probe | | 289 MB | 3.26 GB | 1.41 GB | | 5.6 GB |
| layer switch on the globe, to drawn | | 43-52 ms | 62-107 ms | 56-119 ms | | 122-437 ms |
| hover, per pointer move | | 1.0 ms | 0.57 ms | 1.88 ms | | 6.1 ms |
| turning the globe (3 s) | | 16.7 ms median | 16.7 ms | 16.7 ms | | 16.7 ms (p95 16.8) |
| flat map / 3D relief on, to drawn | | 0.70 / 0.23 s | 0.94 / 0.60 s | 0.97 / 0.64 s | | 1.76 / 2.58 s |

Load 12-23 for these. "Cold" is the first opening after the server starts, when it gzips the files as it sends them
(after the fix below; before it, the first opening of an L8 world took 11 s). The new refine of 783674 to L8
(world d51851, 150 layers, made by this branch through `POST /api/refine`) opens in 3.0 s (10.8 s cold, before the
fix). "At the end of the probe" includes the harness's own second copy of the grid. Hover is slower on the first
moves because each layer the hover card reads is decoded the first time (about 2 ms per L8 layer); the average over
100 moves is still far under a frame.

"JS heap" is V8's heap after a GC; it does not count typed arrays. "Renderer memory" is the renderer process's
resident memory, which does.

### Where an L8 opening goes now

Load stages, L8 after (ms since the page opened, a typical run): modules 257, header 296, **grid fetched, parsed and
prepared 1305**, layer files all in 1312, world fields 1390, topology 1528, paint 1827, drawn 1998. The layer files
arrive while the grid is still loading, so the world is no longer on the critical path; the grid's 87 MB of JSON is.
Before: the 448 MB world JSON was fetched and parsed in about 2.1 s (797 ms of it `JSON.parse`), then the rest.

### Why an L9 world fits

- **The string limit no longer applies to the world.** Chrome cannot hold a text longer than 536,870,888
  characters. Before, an L9 world was 1.76 GB of JSON, 3.3 times that. Now the world's text is a 0.2 MB header,
  and each layer is read as bytes (an ArrayBuffer), which has no such limit; the biggest L9 layer file is 21 MB
  (a float64 layer). The longest text left is the L9 grid file, 370 MB, 69% of the limit.
- **Bytes per cell.** 180 layers take 303 bytes per cell stored (on an L7 world: 88 layers in one byte, 52 in two,
  9 in four, 6 in eight). L9 has 2,621,442 cells: 794 MB of layer files, which the page keeps as they are.
- **Decoding.** 84 layers are stored as whole numbers of tenths, hundredths or thousandths and become 8-byte numbers
  when read: 21 MB each at L9. If every one of them were read, that would add 1.8 GB; the globe and the hover card
  read a few dozen. Whole-number layers are used as stored, with no copy.
- **Where the memory goes.** These typed arrays live outside the JS heap. What is in the heap at L9 is mostly the
  grid (nested lists of corners and neighbours): 2.75 GB after load, against a heap limit of 4.4 GB on this machine.
  Renderer memory in all: 3.65 GB.
- **Measured** on a synthetic L9 world (`tools/synth_l9_world.py`: fb5e11's layers copied onto the L9 grid, every
  new cell taking an L8 neighbour's values): it opens in 6.8-7.1 s on a quiet machine (8-16 s under load), and the
  globe, layer switches, hover, the flat map and the 3D relief all work, with no page errors.

So an L9 world fits, with room to spare outside the heap, but the grid's JSON is the tight part (inbox draft).

## How it works

- **On disk** (`planet/store.py`): `worlds/<id>.json` is the header, one key per line as before, with `"format":
  "procgen-planet/3"` and `"layers": {name: spec}`. Each layer is `worlds/layers/<id>/<name>.bin`, little-endian.
  The spec gives `file` (relative to `worlds/`), `dtype`, `shape`, `kind` (`int`, `float` or `bool`: what Python
  gets back) and, for numbers rounded to d decimals, `"decimals": d` (value = stored / 10^d).
- **Choosing the type** (`store.world_layer_encode`): whole numbers in the smallest of int8 .. uint32 that holds their
  range; floats rounded to d ≤ 6 decimals as whole numbers of 10^-d (the smallest d that gives back exactly the same
  float64; dividing two exact whole numbers rounds once, so it is the same double the JSON text parsed to); other
  floats as float32 when that is exact, else float64. On an L7 world: 88 layers int8, 52 int16, 9 int32, 6 uint8/16,
  6 float64 (travel, grazing, foraging, timber, fuel, building: written unrounded by their producers).
- **Python** (`world.save`, `world.load`, `store.read_world_layers`): `load` gives back the same arrays the JSON gave
  (int64 for whole numbers, float64 otherwise): every layer of a saved world is checked against the old JSON route
  in `tests/test_auto_layers.py`. `server.world_columns` (the cell climate card, thumbnails) reads only the files it
  needs, as does `store.world_layers(world, names)`, now used by the lineages' few-layer reads (settlements,
  demes, gods: they parsed the world's JSON for `flow` and the human-use layers). `delete` removes the layer folder;
  `planet delete --orphans` finds folders whose world is gone.
- **Viewer** (`viewer/globe/load.js`): `setWorld` starts fetching every layer file as soon as it has the header, in
  parallel with the grid. Each layer is a getter that decodes on first read (an int layer is the stored typed array
  itself; a decimals layer becomes a Float64Array, so the numbers are the same doubles as before). The year means of
  humidity, dewpoint, cloud and sunshine are lazy too. `_plate_velocity` is flat (cell i at 3i..3i+2).
- **Server** (`planet/server.py`): files from 64 KB up are now gzipped (was 256 KB), so an L7 world's one-byte layers
  (160 KB) shrink too. The first time a file is sent gzipped, the server used to walk its whole gzip cache to prune
  stale copies (25 ms); after each of a world's 180 files that made an L8 world's first opening 11 s. Now it drops
  that file's own older copies at once and walks the cache at most once a minute (`prune_gz`): first opening 2.2 s.
  The accept queue is 256 instead of 5, for the burst of connections.
- **Refine from the viewer**: `api.VIEWER_MAX_LEVEL` is 9; the L9 warning now says it opens slowly. The cost's file
  size is 0.45 GB per million cells (layers plus grid), from 0.85.
- **Refine progress after a reload** (the lane 227 draft): `GET /api/jobs?type=refine` gives the queued or running
  refine (`server.active_job`); the navigator asks on load and follows it (`follow`), with ETA and Cancel.

## Checked

- **Same picture**: `tools/viewer_perf_globe.py --fingerprint` on L7 world 783674, before and after: the mesh's
  positions, colours, normals and the flat map canvas hash the same in all nine views (globe, smooth, flat map,
  3D relief, two layers each).
- **Same numbers**: `--layerhash` (new) hashes every layer as the viewer holds it. All layers match except cells
  that held -0.0 (49 in temperature, 330 in wind_e, ...), which now read 0.0. -0.0 and 0.0 compare equal, and both
  print as 0.
- **Lossless conversion**: `tools/worlds_to_binary.py` reads every layer back and compares it with the JSON's
  values; it converted 783674 (1.9 s) and fb5e11 (6.0 s).
- **A real L8 refine through the new code**: `POST /api/refine` of 783674 to L8 on my server (port 8796, 1 job,
  4 threads, data root `exports/lane229/bin`, gitignored): 519 s, world d51851, 171 MB of layer files plus a
  0.18 MB header. It opens in the viewer (3.0 s). It has 150 layers, not 180, because the scratch root has no
  source run for the resource history pass; that is the scratch root, not this change.
- **Refine progress after a reload**: a fresh headless page opened 15 s into that refine showed "Refine 783674 to
  L8: 5%" in the bar, Cancel, and "refining to L8: climate · 15 s so far, about 2 min left" in the Family drop-down
  ([refine-after-reload.png](refine-after-reload.png)).
- **Tests**: `tests/test_store.py::test_world_layer_encoding_is_exact_and_small` (each type choice, exact read-back,
  NaN, [cells, 3], empty, bool); `tests/test_auto_layers.py::test_world_layers_are_binary_files_that_read_back_as_the_json_did`
  (a saved world's every layer equals what the JSON route gave, dtype included; the server's column read; delete);
  `tests/test_refine_job.py` (the L9 warning is now "opens slowly"; `server.active_job` names the running refine
  and nothing once it is done); `tests/test_export.py` writes its synthetic world in the new format. Area tests
  (store, auto layers, export, refine, refine job, server, api, finish, make, demes, gods, settlements): 170 passed.
  Not-slow suite: 1109 passed, 1 skipped (NUMBA_NUM_THREADS=4, -n 2). The first not-slow run caught one more reader
  of the old format (`lineages/settlements.py`; demes and gods had the same pattern), now on `store.world_layers`.
  No golden moved: goldens hash runs and in-memory worlds, which this does not touch.

## Not done

- **The grid file is still JSON** (inbox draft: binary grid files). It is now the critical path at L8 and most of the
  memory at L9, so PW-1209's "L8 in < 1.5 s" is not met (2.2 s; the world itself is off the critical path).
- **Layers are fetched all at once**, not only the ones on screen: they arrive before the grid is ready, so fetching
  fewer would not open the world sooner. Decoding is lazy, which is where the memory goes.
- **Drag and drop** of a world file: the dropped header's layers are fetched from the server, so it works only for a
  world the server has (it never worked from file:// for a world with a grid by reference either).
