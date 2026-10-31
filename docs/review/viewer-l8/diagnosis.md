# Viewer at L8: where the time goes (lane 91, 2026-10-31)

**In plain words.** Drawing the whole globe is not what costs. The graphics card draws all 3.9 million
triangles of an L8 globe in about half a millisecond, and turning the globe holds a steady 60 frames a
second. Drawing only the half you can see would save almost nothing. What made L8 slow was work the
browser does *before* drawing: building the globe's mesh in plain JavaScript lists, rewriting every
vertex when only the colours change, and rebuilding the flat map's mesh even though the Equal Earth map
covers it. Those are fixed on this branch (see "Results" at the end). What's left is opening the world, which takes
about 5 s at L8 and is mostly reading the world file, a 448 MB JSON text. That file is also only about 15%
below the largest text Chrome can read. An L9 world could not be opened at all in today's format.

## How it was measured

- L8 world: run 2c0c5d (lane 86b) was still running at 03:50, with no world yet. Instead I used a
  **synthetic L8 world** (`l8synth`): world 2a7385 (L7, seed 11) upsampled onto `grids/L8.json`. The
  icosphere nests, so L8 cells 0..163841 are the L7 cells and every new cell copies a neighbouring L7 cell.
  It is the same size and shape as a real L8 world (184 layers, 448 MB of JSON, 60.6 MB gzipped), written in
  `planet/world.py save`'s line layout. The script is in the scratchpad, not committed. Real L7 worlds are
  112-113 MB, so a real L8 world should be about 450 MB.
- Its own data root (`PLANET_DATA`) in the scratchpad, served by its own `planet serve` on port 8792. The
  code from before this lane ran on port 8793 from a `git archive` of the base commit, for before/after
  pairs. Nothing was written to runs/ or worlds/.
- Headless Chrome 155 on the **real GPU** (ANGLE on OpenGL, NVIDIA RTX PRO 6000: the owner's setup).
  1600x1000 viewport. Harness: `tools/viewer_perf_globe.py`. It reports the load stages, the in-page
  costs of each step, a layer switch timed to the next drawn frame, hover, frames drawn while turning
  (a pixel read back each frame, so GPU time counts), the 60 fps loop while turning, the flat map, the
  3D relief, the heap after a GC, and the CDP sampling profiler.
- The machine was shared: load average 25-35 from other lanes. Repeated timings vary by about ±20%.

## Before (base commit 99652aa8)

| | L7 (2a7385, 164k cells) | L8 (synthetic, 655k cells) |
|---|---|---|
| open the world, to first globe drawn | 2.1-2.6 s | 5.7-6.4 s |
| frame while turning (GPU, 1.0 M / 3.9 M triangles) | 0.2-0.3 ms | 0.4-0.5 ms |
| 3 s of turning: frame gaps median / p95 | 16.7 / 16.8 ms | 16.7 / 16.8 ms |
| hover (pointermove, the fast pick of PW-679) | 0.6 ms | 0.7 ms |
| layer switch on the globe, to drawn | 90-130 ms | 220-340 ms |
| to the flat map (Equal Earth), to drawn | 2.2 s | 6.5 s |
| layer switch on the flat map | 0.5-1.1 s | 2.7-5.3 s |
| back to the globe | 0.5 s | 1.9 s |
| 3D relief on / off | 0.64 / 0.47 s | 2.6 / 2.0 s |
| JS heap after load (after a GC) | 0.35 GB | 1.3 GB (Chrome's limit here: 3.76 GB) |

### Where the L8 time went, by candidate

1. **Mesh build (`prepareGrid`, `buildTopology`): the biggest CPU cost.** It took 0.6 s plus 1.5 s at
   every opening, and `buildTopology` ran again on every switch between globe and map, 3D relief on or
   off, and the map's satellite layer on or off. It pushed 4.6 M vertices one number at a time into
   JavaScript arrays (`base.push(...C)`), allocated small arrays per corner (`unitVec`, `cs.map`), and
   built 1.3 M per-corner arrays (`cornerCells`). In the profiles, `cell`, `buildTopology`, `unitVec` and
   the closures took about 13 s of self time over one probe run, plus 3 s of GC.
2. **Per-cell paint loops: secondary.** `paint` rewrote and re-uploaded all 4.6 M positions (55 MB) on
   every repaint, including a layer switch where only the colours change. At L8 that was about half of a
   globe layer switch. The colour ramps themselves (`cellColors`) cost 15-37 ms, which is small. The cache
   misses of PW-371 are real but second order here.
3. **The flat map was the real chug.** The flat map opens in Equal Earth: a 2D canvas (`drawProj`) laid
   over the live three.js map, which it hides completely (`#projView` is opaque and covers the window).
   Yet every repaint still rebuilt and repainted the hidden map's mesh. On the satellite layer that is the
   per-triangle mesh (11.8 M vertices) plus `mapHillshade`'s `computeVertexNormals` through three's
   generic attribute accessors, and switching between satellite and any other layer rebuilt the topology.
   Result: 2.7-5.3 s per layer switch at L8.
4. **Data-texture uploads / draw calls: not a cost.** 17-25 draw calls, 0.4-0.5 ms a frame for the whole
   globe at L8. The redraw-only-on-change loop (PW-415) means an idle globe costs nothing. GPU buffer
   creation (`bufferData`, ~0.2 s at L8) happens only when the topology is rebuilt.
5. **Labels and overlays: small.** `buildOverlays` forced: 18 ms (L7) and 36-68 ms (L8). They rebuild
   only when something they show changes (PW-1045).
6. **Payload decode: the remaining big item, and a hard limit ahead.** The world fetch plus JSON parse
   takes 2.3-3 s at L8 in a clean page and up to 4 s on the loaded machine. The grid adds 0.5-0.7 s, and
   it used to be fetched only after the world had been parsed. Chrome's longest string here is
   536,870,888 characters. `Response.json()` on a longer body fails, with the misleading message
   "Unexpected end of JSON input" (measured). An L8 world is ~448-455 MB, so it fits with about 15% to
   spare. L9 (~1.8 GB) cannot be opened as JSON.
7. **Hover / picking: fine.** 0.5-0.9 ms per pointer move at both levels (PW-679's shell walk).

The heap is stable across view changes (1.25-1.45 GB at L8, measured step by step with `--heap`); there
is no leak.

## Candidate fixes, ranked by gain per effort (for an L8 globe)

| # | fix | gain at L8 | effort | done here |
|---|---|---|---|---|
| 1 | Don't rebuild or repaint the hidden flat-map mesh under the projection canvas | flat-map layer switch 2.7-5.3 s -> 0.1-0.15 s; to flat map 6.5 -> ~1 s | xs | yes |
| 2 | Build the mesh straight into typed arrays (CSR corner lists, unit vectors once per grid) | ~2 s off opening; ~1 s off every globe/map/relief switch | s | yes |
| 3 | Write positions only when the relief changes | globe layer switch ~0.3 -> ~0.1 s | xs | yes |
| 4 | Fetch the grid while the world downloads; keep the last grid prepared | ~0.5-1 s off opening; reopening a world at the same level skips the grid | xs | yes |
| 5 | Binary world layers (typed arrays, like the runs' `.bin` layers) instead of one JSON text | opening ~3 s -> well under 1 s; heap roughly halved; removes the string-length wall before L9 | m (writer + viewer + server's readers) | draft |
| 6 | Keep the globe geometry across 3D relief on/off (same topology: swap material, add normals) | relief toggle ~1.1-1.3 s -> ~0.3 s | s | draft |
| 7 | Per-cell colour in a data texture (PW-316) | layer switch ~0.1 s -> ~30 ms; not needed at L8 now | m | no (PW-316 stays) |
| 8 | Visible-cap culling of CPU work / chunked patches with horizon culling | nothing measurable for drawing at L8 (the GPU draw is 0.5 ms). Patches become the unit of PW-1198's level of detail when finer data exists (L9/L10 near the camera) | m-l | no: see below |

### On "draw only the half I can see"

The GPU already discards back faces, and at L8 the full draw is 0.5 ms out of a 16.7 ms frame. Hiding
the far half would save about 0.2 ms. The CPU work that did scale with the cell count (mesh build, paint
loops, the hidden flat map) is now cut down directly. Culling it to the visible cap would add bookkeeping
for little gain: the layer switch is already ~0.1 s, and every overlay, the summary and the hover card are
whole-world features. Chunking pays off when the globe holds more data than it can draw at once. That is
the level-of-detail globe of PW-1198 (L9/L10 detail patches near the camera, streamed in). The groundwork
done here helps it: the per-grid arrays (corner lists, unit vectors) are typed and shared, and the
topology is one counted pass over the cells, which is easy to restrict to a subset of cells (one patch).
The patch structure itself should wait until there is finer data to show.

## Results (this branch)

Same harness and machine. Ranges are over several runs, and for the openings the old and new code
alternated.

| | L7 before | L7 after | L8 before | L8 after |
|---|---|---|---|---|
| open a world, to first globe drawn (3 alternating runs each) | 2.05-2.26 s | 1.61-1.84 s | 5.65-6.36 s | 4.44-5.43 s |
| frame while turning (GPU) | 0.2-0.3 ms | same | 0.4-0.5 ms | same |
| 3 s of turning: frame gaps median / p95 | 16.7 / 16.8 ms | same | 16.7 / 16.8 ms | same |
| hover, per pointer move | 0.6 ms | same | 0.7 ms | 0.5-0.9 ms |
| layer switch on the globe, to drawn | 92-131 ms | 38-93 ms | 223-343 ms | 65-127 ms |
| to the flat map (Equal Earth), to drawn | 2.2 s | 0.74-0.87 s | 6.5 s | 0.86-1.5 s |
| layer switch on the flat map | 0.47-1.13 s | 46-98 ms | 2.7-5.3 s | 96-149 ms |
| back to the globe | 0.53 s | 0.16-0.28 s | 1.87 s | 0.62-0.99 s |
| 3D relief on / off | 0.64 / 0.47 s | 0.40-0.48 / 0.24-0.29 s | 2.6 / 2.0 s | 1.1-1.7 / 0.59-1.1 s |
| `buildTopology` alone | 394 ms | 75-97 ms | 1541 ms | 231-397 ms |
| `paint` alone (a world, globe) | 24 ms | 12-17 ms | 164 ms | 45-72 ms |
| JS heap after load (after a GC) | 351 MB | 327 MB | 1328 MB | 1247 MB |

What changed (viewer/globe/):
1. **The mesh is built in typed arrays** (`geometry.js` `prepareGrid`, `buildTopology`). Each corner's cells
   are flat lists (`S.V.cStart`/`cList`, CSR) instead of 1.3 M small arrays. The unit vectors of the cells
   and corners are computed once per grid (`S.V.U`, `S.V.UC`). The buffers are counted first, then filled in
   one pass, and the globe has its own plain loop. The 3D relief's fan lists and `cellUnits` reuse them.
2. **Positions are written only when the relief changes** (`paint`). They are keyed on the frame's layers,
   the exaggeration, 3D relief and the sea floor. The smooth normals of the 3D relief follow
   (`S.topo.normalsOk`), so stopping a replay still brings them back.
3. **The flat map's mesh waits under the projection canvas** (`paint`, `buildTopology`, `map2d.js syncProj`,
   `S.meshDeferred`). It is brought up to date when the live map or the globe shows again. The overlays are
   still built, because the canvas draws them (PW-860). The globe's hover pick stays out of the way
   meanwhile (`pick.js updateHover`).
4. **The grid is fetched while the world downloads**, and the last grid is kept prepared (`load.js gridOf`;
   `select.js loadSelection` asks for it using the index's level). Runs use the same path.
5. **Load stages are recorded** in `planetViewer.diag.load` (`DIAG.mark`).

Same picture, checked: `tools/viewer_perf_globe.py --fingerprint` hashes the mesh buffers (topology,
positions, colours, normals, relief radii) after each of 10 views (globe, a layer switch, smooth colours,
flat map, the map's satellite layer, globe again, 3D relief on the globe and on the map). They are
byte-identical between the old code and the new on L7 (`--equirect`, so the live map is the one drawn).
The Equal Earth canvas is pixel-identical too with a software 2D canvas
(`CHROME_ARGS=--disable-accelerated-2d-canvas`). With the GPU 2D canvas, the first map snapshot differs by
1-10 levels along antialiased lines in 741 pixels. That is a rasterisation difference, not a change in
content.

Tests: `tests/test_viewer.py`, `tests/test_viewer_globe.py`, `tests/test_projection_js.py` (50 passed).
Nothing under `planet/` changed.

The real L8 world (run 2c0c5d) was still running at 04:10, with no frames, so it is not measured here.
When it lands, run `uv run --with playwright python tools/viewer_perf_globe.py PORT <world id>` against
your own server. Opening a world for the first time also makes the server gzip it once (several seconds
for 450 MB, cached under `.gzcache`). The numbers above are with that cache warm.
