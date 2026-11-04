---
id: PW-687
title: A run page holds every frame of its layers (216 MB resident on a peoples run)
type: task
status: todo
parent: PW-103
milestone: later
subsystem: viewer
effort: m
impact: med
found_by: perf679
blocked_by: []
relates: [PW-679]
refs: [viewer/index.html, planet/server.py, "run 7bc9ed", docs/review/lineages/perf-679.md]
created: 2026-10-23
updated: 2026-11-03
---

## Description
`loadNeeded` fetches each layer's whole `.bin` (all frames) and keeps it as one typed array. A peoples run at L7 (146
frames) holds elevation 47.8 MB + ice 47.8 MB + five peoples layers at 23.9 MB = 216 MB resident, 57 MB over the wire
(elevation alone 41 MB gzipped) before the first picture, while a frame needs 164 k cells x 7 layers. The first view of a
fresh run also makes the server gzip those 24-48 MB files on the fly (cached afterwards). Nothing here is slow once
loaded (PW-679 measured), but it is the biggest remaining cost of opening a run and of memory use on the owner's laptop
class machines.
Options: (A) HTTP Range requests for a window of frames around the current one (the files are frame-major, so a frame
is a contiguous slice; gzip rules out ranges, so the server would serve them raw or per-frame-chunk gzipped); (B) write
per-frame-chunk files at run time; (C) keep it and only drop `peoples_whole` until its toggle is used (-24 MB). My lean:
A with a 5-frame window, prefetching in the scrub direction. Replay speed is the constraint: a frame must be ready within
its ~20 ms step.
- [ ] opening a peoples run transfers well under 20 MB
- [ ] scrubbing and replay stay as smooth as now

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: viewer nicety, not needed for the culinary goal
- 2026-10-23: Created from inbox draft draft-viewer-run-layers-per-frame.md (found by perf679).
