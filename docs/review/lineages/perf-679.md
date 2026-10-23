# Viewer cost on the peoples views (PW-679)

Owner report: the viewer "chugs mightily" on the peoples tab. This note measures what the pages themselves cost,
apart from the machine (the box was at load 28-49 on 48 cores while measuring, so absolute numbers are noisy; every
before/after pair below was taken back to back against the same server, and the JS-only figures are the steady ones).

## Method

`tools/viewer_perf.py` (new): headless Chrome 155 through playwright (`uv run --with playwright python tools/viewer_perf.py PORT RUN`),
software GL (swiftshader), 1400x900. It serves the page through a route that appends a hook to the module scope, so
`--viewer=FILE` can run the old `index.html` against the new one. The server was my own `planet serve --port 8791`
(read-only use of the shared data folders); runs 7bc9ed (world 1df1c3, 146 frames) and 53b9c1 (world 3e9e7d, 149
frames), 163 842 cells (L7), opened as `?run=ID&layer=peoples`.
Modes: the default probe (timings of each interaction), `--profile=hover|step|switch|idle|spin` (the CDP sampling
profiler over one loop, plus script/layout/style time), `--workbench` (lineages.html). Software GL makes
anything that waits on a draw (a switch of colour layer, the 3-second replay) wall-clock noise: a draw call blocks on
the CPU rasteriser. So the per-interaction numbers are JS time measured around the call, with no draw in between.

## What was slow

| # | Where | Cost before | Cause |
|---|-------|-------------|-------|
| 1 | hover (every mouse move over the globe) | 36-39 ms | `ray.intersectObject(mesh)` tests all ~1 M triangles; no spatial index. 100% of the time was triangle tests (getX, dot, crossVectors, intersectTriangle...) |
| 2 | stepping a frame (arrow, replay, scrub) | 23-30 ms JS | 5.8 ms `cellColors`: `peoplesColor` parsed each people's CSS colour string per cell (`Color.set('#...')`: setStyle + SRGBToLinear, ~half of it); 5 ms `peopleOverlays`: every track point (7 per segment x all segments up to now, per people) went through `nearestCell` (a 27-cube hash probe) and `unitVec`, rebuilt every frame |
| 3 | scrubbing the slider | one full repaint per `input` event | 40 events in a burst = 40 repaints (973 ms); a busy machine queues them behind each other |
| 4 | switching between peoples / peoples mix / peoples overlay | refetch + gunzip + parse of 24 MB per layer, every switch | `loadNeeded` drops every layer the new colour layer doesn't use ("one picked again is fetched again"); a cycle of 12 switches fetched 19 layers again (102 MB over the wire, instead of 57) |
| 5 | `peoples overlay` layer | throws in `renderLegend` | no legend branch, fell through to `rampLegend` (page error on every paint on that layer) |

Not a cost (measured, no change made):

- idle and a spinning globe: 0 ms of script per second (the PW-415 "draw only when changed" works; a hidden tab gets no animation frames at all).
- Server: every peoples endpoint answers in under 3 ms (layers 0.8-6 ms from the gz cache, `run.json` 0.4 ms, `/api/lineage-tree` 2.5 ms, `runs/index.json` 0.6 ms). The first view of a fresh run compresses on the fly (not measured here).
- `renderRunSummary` (peoples panel and event list rebuilt on each frame): 0.7 ms, layout 0 ms; not worth caching.
- The workbench (lineages.html): page 58 kB, the run 122 kB, loads in 0.2 s; drawing a tab 2-6 ms, a timeline drag 1.6-2.7 ms per mouse move, a tab switch 8-18 ms. Fine at 53 lines.

## Fixes (viewer/index.html only; no planet/ change, no output change)

1. **Globe pick without testing every triangle** (`pickGlobeCell`): the ray crosses only the thin shell between the lowest and
   highest surface point; walk it in half-cell steps, take the cell nearest each step and its neighbours, and run
   Moller-Trumbore on only those cells' triangles (`topo.triStart`). Flat map still uses three's raycast. `planetViewer.pickCheck(n)` compares it
   with the full raycast on random pointers: 0 mismatches in 1 600+ picks (globe and 3D-relief globe, runs and a finished world; ~70% of the random pointers hit the globe).
2. Colours of each people parsed once (`lineColor`). The old picked-people and overlay branches lerped a colour with itself (see the draft); their output is kept exactly.
3. The tracks and origin rings cache each point's cell and unit vector per run (`V.peopleCache`, `llPosPt`); only the frame's radius is read per frame, so the drawn lines are the same.
4. Slider scrubbing coalesced to one repaint per display frame (the last position wins); arrow keys and play are untouched.
5. A peoples run keeps all its peoples layers loaded (`layersNeeded`), so switching among them, or away and back, refetches nothing (+24 MB resident for `peoples_overlay`, which the hover card also uses).
6. A legend for the `peoples overlay` layer (the overlay peoples present), which removes the page error.

## Timings (run 7bc9ed; 53b9c1 in brackets), JS ms unless noted

| Interaction | Before | After |
|-------------|--------|-------|
| Hover (pointermove) | 36.5 (38.7) | 0.07 (0.08) |
| `cellColors` for the peoples layer | 5.8-6.1 (7.2) | 2.9-3.9 (3.5) |
| Step one frame (`setFrame`, paint + panel + hover) | 23.0 (30.1) | 15.6-20 (19.0) |
| `paint` alone, 10 repaints | 27.4-30.2 (36.5) | 21-26 (29.6) |
| 40 slider events back to back | 973 ms, 40 repaints (1263 ms) | 237-304 ms, 1 repaint (296 ms) |
| Layer fetches during 12 switches of colour layer | 19 more layers, 102 MB total wire | 0 more, 57 MB total wire |
| 80 steps in a row (`--profile=step`, main-thread task time) | 2 582 ms | 1 670 ms |
| Pick a people (repaint + overlays) | 21.6 (38.8) | 19.5-22 (35) |
| Replay 3 s (software GL, noisy) | 18-21 frames | 18-21 frames |
| Page errors | 1 (overlay legend) | 0 |

Load: 56 MB over the wire, 0.9-1.2 s locally, unchanged in shape (+2.4 MB for the overlay layer, the same 57 MB as before once the switches are counted).
Where the rest goes (the remaining ~15-20 ms a frame): `paint` rewrites 1.15 M vertices' position and colour (about 21 MB of upload) per frame; the land radius
genuinely changes between frames (190 000 of 491 522 radii differ from frame 1 to 2: sea level and ice), so it cannot be skipped. That, and the 216 MB of
whole-run layers, are drafted below rather than patched here.

## Follow-ups (inbox drafts)

- `draft-viewer-peoples-pick-dim-noop`: picking a people does not dim the others (and the overlay layer never blends); a self-lerp bug in `peoplesColor`.
- `draft-viewer-run-layers-per-frame`: a run page holds every frame of elevation, ice and the peoples layers (216 MB resident, 56 MB over the wire); load a window of frames or the current one.
- `draft-viewer-paint-cell-colour-texture`: colour and position per vertex, 1.15 M vertices a frame; a per-cell colour texture or a per-cell attribute would cut the upload by ~7x.
