---
title: "LOD seams: judge the edge against the same line with no seam, not against the ground 16-48 px away"
type: task
status: needs-decision
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: xs
impact: med
found_by: lane293
blocked_by: []
relates: [PW-1694, PW-1689]
refs: [tests/test_zoom_lod_build.py, "planet/zoom/lod_build.py::carve_block", "planet/zoom/lod_build.py::edge_steps", docs/review/zoom/lod-plan-v2.md, "world dba204", "cell py.1.1"]
---

## Description
**In plain words.** The rule for "tile edges are invisible" compared the height steps across an edge with the steps 16-48
pixels inside, and asked for 0.9-1.1x. Lane 293 found that a line drawn anywhere inside a single tile, where there is
no edge at all, scores anywhere from 0.4x to 1.4x (median) and 0.6x to 1.9x (90th percentile) on that rule on world
dba204: the ground simply changes over 30 km. So the rule fails seamless ground, and a lane chasing it would tune
the edge to a statistic, not to the look. If this isn't settled, PW-1694's done-when can't be met by any construction,
and later lanes may re-open it.

Measured (dba204, cell py.1.1, level 2, land off the imposed rivers, lane 293): with the edge blocks (PW-1694) the four
edges score 0.89/1.00, 1.07/1.08, 1.07/1.32, 1.22/1.03 (median/p90); the same lines carved as one block over both tiles
(no seam) score 0.90/1.00, 1.06/1.08, 1.07/1.37, 1.21/1.00. Before (lane 290's texture): 0.92/1.09, 0.87/0.97,
1.08/1.40, 0.95/1.28.

Options:
- A. The edge's ratio within 10% of the same line's ratio with no seam (one block carved over both tiles,
  `lod_build.carve_block`). What tests/test_zoom_lod_build.py::test_edge_steps_like_the_inside now does (lane 293);
  the four dba204 edges are within 0.01-0.05 of it. (lean)
- B. Keep 0.9-1.1 against the inside band: unattainable (seamless ground fails it), the test stays xfail.
- C. Average the rule over many edges (all of a cell's level-2 edges): the line-to-line spread averages out, but it
  needs ~100 tiles built per check (~20 min).
- [ ] the coordinator or Daniel picks A, B or C; PW-1694's done-when is updated to match
