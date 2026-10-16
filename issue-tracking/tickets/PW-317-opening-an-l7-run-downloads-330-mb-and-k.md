---
id: PW-317
title: Opening an L7 run downloads ~330 MB and keeps every visited layer's frames in memory
type: task
status: todo
parent: null
subsystem: viewer
effort: m
impact: med
found_by: viewer-replay-speed
blocked_by: []
relates: []
refs: [viewer/index.html, planet/store.py, planet/server.py, "run a1d3b9"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
A run stores one file per layer holding every keyframe (`runs/<id>/layers/<name>.bin`, frames x cells).
The viewer fetches whole files when a layer is first needed: on L7 run a1d3b9 (251 keyframes) the
default elevation view pulls elevation (82 MB), lake_depth (82 MB, int16), lake_kind, ice, flow and
downstream (41 MB each): ~330 MB plus the 21 MB grid. Locally that's ~40 ms to serve and a few hundred
ms to receive; replay itself makes no requests (measured 2026-10-15). But every layer visited stays in
memory for the session (~1-1.5 GB of ArrayBuffers after clicking through the run's layers), and over
a network or on a laptop the first open is slow.

Options: (A) HTTP Range requests for a window of frames around the playhead, prefetching ahead while
playing (the server's SimpleHTTPRequestHandler doesn't do Range; it would need a small handler);
(B) drop a layer's buffer when it is no longer drawn (re-fetch on return); (C) gzip the .bin files on
the wire (int8/int16 grids compress well) via a Content-Encoding the handler adds for pre-gzipped files.
Lean: B (simple, frees memory) plus C if the first open matters. Check frame times stay ~25-30 ms.

## Updates
- 2026-10-15: Created from inbox draft draft-viewer-run-download-size.md (found by viewer-replay-speed).
