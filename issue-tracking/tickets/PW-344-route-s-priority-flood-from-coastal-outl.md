---
id: PW-344
title: "route's priority flood from coastal outlets only: ~3.6x faster at L7, changes `down` on 0.6-2% of land cells"
type: task
status: in-progress
parent: null
subsystem: hydrology
effort: s
impact: low
found_by: coordinator
blocked_by: []
relates: [PW-255]
refs: [planet/hydrology.py, planet/kernels.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
After PW-255 (bit-identical speedups), `route`'s flood is ~60-70% of what's left of the lakes+routing bucket. Queuing only
the coastal outlets instead of every sea cell makes it ~3.6x faster at L7 but changes `down` on 0.6-2% of land cells
(tie-breaks among equal routes). Physically equivalent; needs a goldens update and a health check, so it belongs in the
serial run-physics lane (measurements on PW-255).

## Updates
- 2026-10-16: Status todo -> in-progress. Run-lane agent started.
- 2026-10-16: Created from inbox draft draft-route-coastal-outlets.md (found by coordinator).
