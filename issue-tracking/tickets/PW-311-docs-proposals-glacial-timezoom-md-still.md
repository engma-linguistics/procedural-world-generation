---
id: PW-311
title: docs/proposals/glacial_timezoom.md still says the time zoom is view-only; PW-091 made it feed finished worlds
type: task
status: todo
parent: null
subsystem: docs
effort: xs
impact: low
found_by: docs-cleanup
blocked_by: []
relates: [PW-091, PW-090, PW-030, PW-033, PW-037]
refs: [docs/proposals/glacial_timezoom.md, docs/overview.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
The 2026-10-13 design spec lists "**View-only:** results do not feed back into the main run" among the user's decisions. Since PW-091 (done) a time zoom feeds a finished world (`planet finish <timezoom> --kyr N`, overview §2.11). The main run still isn't changed, so the statement is half-true, but a reader of the spec would miss the finish path. The doc was kept in the 2026-10-15 docs cleanup because open tickets PW-030/033/037/090 cite it.
- [ ] Add a one-line status note at the top of the spec (time zoom now also feeds finished worlds, PW-091; see overview §2.11 and §2.14), or fold what the open tickets need into them and delete the spec.

## Updates
- 2026-10-15: Created from inbox draft draft-glacial-timezoom-proposal-view-only-outdated.md (found by docs-cleanup).
