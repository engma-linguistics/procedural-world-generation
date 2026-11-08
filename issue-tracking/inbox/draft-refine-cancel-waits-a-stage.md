---
title: "Refine from the viewer: Cancel waits for the end of the current stage (up to ~15-20 min in an L9 refine's wave power)"
type: task
status: todo
parent: null
milestone: later
subsystem: viewer
effort: s
impact: med
found_by: lane 227
blocked_by: []
relates: [PW-1438, PW-1209]
refs: [docs/review/viewer/refine-control.md, docs/review/refine-l8/report.md, "planet/api.py::Jobs.cancel", "planet/api.py::any_job", "planet/refine.py::STEPS", "planet/world.py::finish", "planet/coast.py::wave_power"]
---

## Description
In plain words: a server job stops only when it next reports progress (the cancel flag file is read there). A refine reports
at each stage of the finish (`refine.STEPS`), but wave power is one long call: about half of an L8 refine (129 of 266 s) and,
since it grows faster than the cell count, most of an L9 refine's 38 minutes. Pressing Cancel then shows "cancelled" at once,
but the worker process keeps one core-set and up to ~39 GB busy until wave power ends. Daniel would think the machine is free
when it is not, and a second refine started then would be refused only by the memory check, not by the one-at-a-time rule
(the cancelled job no longer counts as running).

What breaks if never done: after Cancel in an L9 refine, ~39 GB and 4+ cores stay in use for up to ~20 min without the viewer
saying so.

Fix options: a progress hook inside `coast.wave_power`'s loop over directions or blocks (cheapest; a cancel point every few
seconds), or let `Jobs.cancel` terminate a refine's worker process (parallel.Pool would need to restart the worker).

- [ ] Cancel frees an L8 refine's worker within ~30 s (measure on a mocked or L7 refine)
