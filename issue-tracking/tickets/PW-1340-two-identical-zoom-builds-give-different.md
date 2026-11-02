---
id: PW-1340
title: Two identical zoom builds give different `stats` (arrays identical)
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: zoom
effort: s
impact: low
found_by: lane122
blocked_by: []
relates: []
refs: ["planet/zoom/regional.py::build", "planet/zoom/stage_finish.py::stats", "world dba204", docs/review/land-zoom/cost.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** Lane 122 hashed every output array and the JSON of `z["stats"]` of 4000 km, 2 km builds of dba204(-25, 65), seed 1.
Two builds whose 81 arrays were all identical (one on the old landform code, one on the new) had different `stats` hashes
(b976fc96c6 vs 4eae2e3fd7), so some entry of `stats` may not be deterministic (an ordering of equal-height falls or lakes, a
set, a float sum order from threads?), or the landform change alters a stat without touching any array (not expected). Not
traced. Why it matters: golden tests and any "bit-identical" check of zoom changes can only trust the arrays, not `zoom.json`.
- [ ] build twice on one code version, diff the `stats` dicts key by key, fix the ordering or document it

## Updates
- 2026-11-02: Created from inbox draft draft-zoom-stats-differ-between-identical-builds.md (found by lane122).
