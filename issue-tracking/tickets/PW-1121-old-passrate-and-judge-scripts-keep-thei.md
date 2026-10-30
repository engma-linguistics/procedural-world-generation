---
id: PW-1121
title: Old passrate and judge scripts keep their own copies of the icebox rule
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: xs
impact: low
found_by: lane65
blocked_by: []
relates: [PW-1091]
refs: [docs/review/base-climate/v1-finish-10/passrate3.py, docs/review/base-climate/v2-climate-1/passrate2.py, docs/review/base-climate/v1-finish-8/passrate2.py, docs/review/base-climate/v1-finish/outliers.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Lane 65 moved the judges that are still used (passrate4, pjudge, fmtally, warm-drift/judge) from the "icebox" flag to the owner's three ice terms, with frozen over as the only ice failure. Older review scripts (passrate, passrate2, passrate3, outliers) still have their own icebox lines and fail rules. They are historical evidence for closed lanes, so they were left as they were. If a lane re-runs one of them, point it at `passrate4.judge` instead; when their tickets close the review folders can be deleted.

- [ ] Delete or leave the old judge copies when their review folders go

## Updates
- 2026-10-30: Created from inbox draft draft-passrate-scripts-copies.md (found by lane65).
