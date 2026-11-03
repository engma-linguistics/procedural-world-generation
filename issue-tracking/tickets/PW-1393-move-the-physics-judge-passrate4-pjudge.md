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
- [x] tools/judge.py with passrate4.judge and pjudge's finish-moment logic
- [x] a test that judges a fixed small input
- [x] review-folder copies removed or left as thin pointers; the ticket notes the commit

## Updates
- 2026-11-03: Created.
- 2026-11-03: Lane 151 moved passrate4 and pjudge into tools/judge.py (`judge.py bar`, `judge.py paired`; `judge_draw(raw)` is shared with tools/hard_bar.py). passrate4.py and pjudge.py in the review folders are now pointer files; test is tests/test_judge.py. Output byte-identical on lane 144's judge dir (paired tables and json for 4 arm pairs, hard_bar per arm, passrate4). PW-1121 and PW-1272 left; follow-up drafts draft-judge-shims-retire and draft-judge-draw-takes-a-stored-run.
