---
title: "Refine from the viewer: the progress bar is gone after a page reload; show the running refine on its own"
type: task
status: todo
parent: null
milestone: v5
subsystem: viewer
effort: s
impact: med
found_by: lane 227
blocked_by: []
relates: [PW-1438]
refs: [docs/review/viewer/refine-control.md, "viewer/navigator.js::follow", "viewer/navigator.js::refineBox", "planet/api.py::Jobs.active", "planet/server.py::refine_estimate"]
---

## Description
In plain words: the navigator keeps the job it is following in the page only. An overnight L9 refine outlives the page:
after a reload (or the next morning, in a new tab) the job still runs on the server, but no progress bar shows and nothing
says a refine is on. Daniel finds it only by pressing "Check the cost" again, which then says "another refine is queued or
running" and offers "Show the running refine". The finished world does appear in the Family tree, under its source world.

What breaks if never done: the v0.5 story ("next morning the L9 world opens") has Daniel open the viewer and see no sign of
the night's refine until he looks for it in the tree or checks the cost again; while it still runs he may think it failed.

Fix: a `GET /api/jobs?type=refine` (or the active refine's id in `/api/planets`), and the navigator follows it on load
(`follow(id, ...)`), so the bar and the ETA come back.

- [ ] after a reload during a refine, the navigator shows its progress and ETA without a click
