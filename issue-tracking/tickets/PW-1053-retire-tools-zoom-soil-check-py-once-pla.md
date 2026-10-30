---
id: PW-1053
title: Retire tools/zoom_soil_check.py once planet/soils.py stops citing it
type: task
status: todo
parent: null
milestone: later
subsystem: infra
effort: xs
impact: low
found_by: housekeeping-52
blocked_by: []
relates: [PW-331, PW-345]
refs: [tools/zoom_soil_check.py, planet/soils.py, docs/overview.md, docs/proposals/soils.md]
created: 2026-10-29
updated: 2026-10-29
---

## Description
Housekeeping lane 52 retired the single-ticket tools the code audit listed, but kept
`tools/zoom_soil_check.py` (PW-331's zoom-soil check, 154 lines, used by no open ticket). The lane was not
allowed to touch `planet/`, and `planet/soils.py:551` cites the tool as where its zoom constants were
measured, so deleting the tool would leave a dead path in code.

To retire it: delete the tool, point the soils.py comment at `<sha>:tools/zoom_soil_check.py` (the last
commit that had it), drop its row in docs/overview.md section 2.17 and its mention in docs/proposals/soils.md
(or make them `<sha>:` refs too), and note the removal on PW-331. Keep it instead if a lane is about to
re-tune the zoom soils.
- [ ] tool removed, comment and docs point at the history

## Updates
- 2026-10-29: Created from inbox draft draft-retire-zoom-soil-check.md (found by housekeeping-52).
