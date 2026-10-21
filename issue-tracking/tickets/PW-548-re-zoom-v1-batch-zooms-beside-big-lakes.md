---
id: PW-548
title: Re-zoom v1 batch zooms beside big lakes with the PW-531 shore code; health sweep
type: task
status: done
parent: null
milestone: v1
subsystem: zoom
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-202]
refs: []
created: 2026-10-21
updated: 2026-10-21
---

## Description
The 8-planet v1 batch (worlds dad91b 607540 d14b89 c00ebf 1144ce 91448a 3e0b0a 31926a) made its 32 zooms before PW-531 merged. Rebuild those whose region holds a big coarse lake, then run the PW-202 health sweep and scorecard on the batch.

## Updates
- 2026-10-21: Done (branch worktree-agent-ac196b9549bb19fc0, pw548). Apron check: PW-531's `shore_apron` acts on lakes of >= 150 km2 in the landscape pass, and the zoom.json stats count them (`lakes`). Eight zooms have lakes: 59e62e 1a7056 106461 a009c1 got the apron (156 / 1018 / 622 / 3334 px graded); 930fa1 5d0b74 72857c bea8db have only tiny lakes (5-65 km2 in all) and rebuild bit-identically (max height change 0.0 m), so they were not rebuilt. The other 21 zooms have no lakes. 360551, fa7d30 and f0251b (being debugged by another agent) have no lakes, so need no apron rebuild. Rebuilt in place with the same parameters (ids unchanged): land > 300 m, not lake, slope < 1 m/km, whole zoom / within 40 km of a lake: 59e62e 278544 -> 278592 / 64992 -> 64944 km2 (Antarctic-style upland, the apron touches little; 156 px); 1a7056 67456 -> 65504 / 4464 -> 2928 (-34% beside the lakes); 106461 14192 -> 12560 / 2576 -> 1200 (-53%); a009c1 72 -> 72 / 3 -> 3 (nothing flat there; terrain moved up to 46 m). Health check of the batch's runs: docs/review/health/2026-10-21-batch/report.md; drafts draft-batch-worlds-sliced-at-extreme-sea-level, draft-batch-sea-level-ends-deep.
- 2026-10-21: Created.
