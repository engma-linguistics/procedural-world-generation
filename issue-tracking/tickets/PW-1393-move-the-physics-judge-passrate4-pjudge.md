---
id: PW-1393
title: Move the physics judge (passrate4, pjudge) out of docs/review into tools/ with a test
type: task
status: todo
parent: null
milestone: v2
subsystem: infra
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-1121, PW-1272]
refs: ["docs/review/fresh-eyes/2026-11-03.md#2-recommendations-ranked", tools/hard_bar.py, tools/ice_criteria.py, docs/review/base-climate/v1-finish-12, docs/review/base-climate/v1-finish-16, docs/coordination.md]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: the scoring code that decides whether a generated planet passes lives in review folders (the pass-rate script in docs/review/base-climate/v1-finish-12, the judge in v1-finish-16), and a tool imports it from there (tools/hard_bar.py:22-23). Review folders get pruned, so the judge could disappear under the tool. Move both into tools/ as one module (the review names `tools/judge.py`), add a test, and point tools/hard_bar.py, tools/ice_criteria.py and docs/coordination.md at it. PW-1121 (old scripts keep their own copies of the icebox rule) and PW-1272 (hard_bar cannot judge a stored run) are close neighbours; do them together if cheap.
- [ ] tools/judge.py with passrate4.judge and pjudge's finish-moment logic
- [ ] a test that judges a fixed small input
- [ ] review-folder copies removed or left as thin pointers; the ticket notes the commit

## Updates
- 2026-11-03: Created.
