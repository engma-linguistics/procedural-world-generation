---
title: regional.py still holds about 1,100 lines of helpers and 400 lines of I/O; split them by topic as the audit proposed, and split zoom.fine.build the same way
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: m
impact: low
found_by: refactor-lane-55
blocked_by: []
relates: [PW-1048, PW-1049]
refs: [planet/zoom/regional.py, planet/zoom/fine.py, docs/review/code-audit-2026-10/index.html]
---

## Description
In plain words. The zoom code now lives in `planet/zoom/` and its main build is a list of named steps, but `regional.py` still contains everything the steps share: the delta, knickpoint, waterfall, lake and glacier helpers (lines ~190 to ~1190) and the image, save and load code at the end. The audit proposed one file per topic (pixel frame, deltas, rivers and falls, lakes, glaciers, preview and images, save and load). This is the second half of that, left out of this lane to keep the diff reviewable. The fine zoom's own build (`fine.py`, about 1,000 lines in one function) has the same shape and was listed in the audit as "afterwards", using the same stage and shared-context method.

Do it with PW-1048 (the two zoom dilate helpers and the falls code) and PW-1049 (the drifted finish copies), since both touch the same helpers. The stage modules reach these helpers as `RG.name`, so a move only needs those references updated.
- [ ] regional.py is only `ZoomCtx`, `build()` and the I/O
- [ ] `fine.build` split into named stages
