---
id: PW-1153
title: Viewer control for the momentum edge's two dials (meta.surge_early, surge_late)
type: task
status: todo
parent: null
milestone: later
subsystem: viewer
effort: s
impact: low
found_by: lane73
blocked_by: []
relates: []
refs: [planet/lineages/spec.py, planet/lineages/run.py, planet/lineages/history/pressure.py]
created: 2026-10-30
updated: 2026-11-03
---

## In plain words
Lane 73 added a setting for how hard a growing people can push into land others already hold: one value for the early eras and one for
the present. It can only be set in the tree file so far. The peoples editor needs a dropdown for it, next to lane 63's "how hard peoples
press dragons and giants".

## Description
meta.surge_early / meta.surge_late take the choices in spec.SURGE_X (0, 0.5, 1, 2; default 1, 1). Each multiplies
history.params.SURGE_Q, the competition cut at full momentum. The editor schema already carries the defaults and `surge_x`
(run.editor_schema).
- [ ] two dropdowns in viewer/lineages.html, labelled in plain words ("how hard a growing people pushes into held land: early eras / late eras")

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: viewer nicety, not needed for the culinary goal
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-surge-dials-viewer-control.md (found by lane73).
