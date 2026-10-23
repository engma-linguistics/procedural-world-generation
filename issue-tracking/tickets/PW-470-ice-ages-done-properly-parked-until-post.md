---
id: PW-470
title: "Ice ages done properly (parked until post-v1): run ice as a cycle average, the time zoom as a window, realistic margins and orbit response"
type: epic
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: xl
impact: high
found_by: daniel
blocked_by: []
relates: [PW-244, PW-090]
refs: [docs/review/audit/ice-framing-deep-dive.md]
created: 2026-10-20
updated: 2026-10-23
---

## Description
Owner decision 2026-10-20: ice-age physics is parked until after v1; v1 ships a kludgier approximation instead. This epic gathers the physics work. Plan of record: docs/review/audit/ice-framing-deep-dive.md (PW-462). Recommended order when it reopens: PW-467 (zoom-mean vs run tool), PW-465 (run marine ice budget), PW-464 (run ice as cycle mean), then re-apply PW-460/459 (branch worktree-agent-a9f64607e1a64d2e8, 246ef40), then PW-469 spin-up, PW-468 phase picker, PW-466 era start/end. Background: docs/review/audit/PW-033-diagnosis.md, PW-440-handoff.md, PW-030-handoff.md.

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: Created.
