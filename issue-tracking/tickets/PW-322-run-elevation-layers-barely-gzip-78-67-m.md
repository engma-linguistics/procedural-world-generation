---
id: PW-322
title: Run elevation layers barely gzip (78 -> 67 MB); byte-planed or delta-coded int16 layers would
type: task
status: todo
parent: null
subsystem: store
effort: m
impact: low
found_by: viewer-download-climograph
blocked_by: []
relates: [PW-317]
refs: [planet/store.py, planet/server.py, viewer/index.html, "run a1d3b9"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Since PW-317 the server sends run layer files gzipped. Opening L7 run a1d3b9 (elevation view) now moves
~96 MB instead of ~336 MB, but ~67 MB of that is `elevation.bin` alone: an int16 file (frames x cells)
whose low bytes look random to deflate, so it shrinks only 78 -> 67 MB. The other int16 layers
(crust_age, npp, precipitation, plate, sediment_cover, landform_age, glaciated_myr) likely behave alike
when picked. The int8 / mostly-zero layers shrink 5-50x.

Options: (A) the store writes int16 layers byte-planed (all high bytes, then all low bytes, per frame) and
the viewer's decodeFrame / store.read_layer put them back (a few ms per frame in JS); (B) store each frame
as the difference from the previous keyframe (elevation changes little per keyframe at L7), which also
needs a prefix sum when seeking; (C) leave it (local use is fine: 1.3 s to first frame from the cache).
Measure the gzip size and the replay ms per keyframe before choosing. Note the server's `.gzcache` (git-ignored, under the data root) holds ~380 MB per fully visited L7 run; copies are pruned only when their file changes or goes.

## Updates
- 2026-10-15: Created from inbox draft draft-run-layer-byte-shuffle.md (found by viewer-download-climograph).
