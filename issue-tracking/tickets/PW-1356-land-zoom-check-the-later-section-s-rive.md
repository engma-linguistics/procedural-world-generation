---
id: PW-1356
title: Land zoom, check the later section's rivers turned away at the owner line
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: zoom
effort: s
impact: med
found_by: lane129
blocked_by: []
relates: [PW-1302]
refs: ["planet/zoom/match.py::walls", "planet/zoom/match.py::ACCEPT_M3S", "planet/zoom/match.py::inflows", "planet/zoom/stage_landscape.py::final_drainage", docs/review/land-zoom/rivers.py, docs/review/land-zoom/rivers-round1.md, "zoom:d904d6", "zoom:5d2e02", "zoom:a13667", "zoom:fe600a", "zoom:e2313a", "world:dba204"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** Where two sections meet, the later section's water may now cross into the earlier one's ground
only where the earlier section has a stream (at least `ACCEPT_M3S` = 10 m3/s) coming in. Everywhere else along the
line the earlier section's ground is a wall to it (lane 129, `match.walls`). That stopped a river handed on at the
line from running straight back out, and made the later section's rivers enter where the earlier section has them.
But a river of the later section that reaches the line where the earlier one has nothing coming in now turns: it
runs along the line, or away, to another way out. On the desert pair a 166 m3/s river of B's (5d2e02; it entered A's
ground in a13667, where A had about 0) no longer crosses. Nobody has looked at these in the viewer.

To do: find them (B's rivers >= 50 m3/s whose course in the matched build runs within a few pixels of the line for
> 20 km, or that crossed in the build without walls and don't now), look at a few in the viewer
(http://localhost:8765/?world=dba204.json&tab=zoom&zoom=5d2e02), and decide whether to keep the walls, loosen
`ACCEPT_M3S` with the resolution (10 m3/s is a few 4 km pixels' rain but hundreds of 1 km pixels'), or let a big
river of the later section through anyway (the mosaic discharge pass would then carry its water on in the earlier
section).

## Updates
- 2026-11-02: Created from inbox draft draft-land-zoom-walls-divert-rivers.md (found by lane129).
