---
id: PW-1418
title: Repoint the last review scripts at tools/judge.py and drop the passrate4/pjudge pointer files
type: task
status: done
parent: null
milestone: null
subsystem: infra
effort: xs
impact: low
found_by: lane151
blocked_by: []
relates: [PW-1393, PW-1121]
refs: [tools/judge.py, docs/review/base-climate/v1-finish-12/passrate4.py, docs/review/base-climate/v1-finish-16/pjudge.py, docs/review/base-climate/v1-finish-16/fmtally.py, docs/review/base-climate/warm-drift/judge.py, docs/review/base-climate/warm-edge-l81/rescore.py, docs/review/base-climate/v1-finish-13/screen.py, docs/review/base-climate/v1-finish-12/pr.sh]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: PW-1393 moved the climate judge into tools/judge.py and left two small pointer files in review folders (passrate4.py, pjudge.py) so that older lane scripts keep working. Four review scripts still import `passrate4` through the pointer (fmtally.py, warm-drift/judge.py, warm-edge-l81/rescore.py; screen.py and v1-finish-12/pr.sh name it). When those folders are pruned, or one of them is used again, change them to `from tools import judge as P` and delete the pointers.
Noticed, not changed (a move only): fmtally.py's docstring says the finish temperature band is -6..+3 C while the code (HUMAN_RANGE) uses -6..+5.
- [ ] each of the scripts above imports tools.judge directly
- [ ] passrate4.py and pjudge.py deleted; docs/review retention check clean

## Updates
- 2026-11-03: Created from inbox draft draft-judge-shims-retire.md (found by lane151).
- 2026-11-03: Done (lane 152): fmtally.py, warm-drift/judge.py, warm-edge-l81/rescore.py, screen.py and pr.sh use tools/judge.py; passrate4.py and pjudge.py deleted. fmtally and the bar output byte-identical on lane 144's judge dirs (m_r0.0005_l6fix, n2_r0.0005_l6fix); warm-drift judge and rescore only compile-checked (their data dirs are gone).
