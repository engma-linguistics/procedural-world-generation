---
title: Make a peoples zoom from the viewer and the zoom API
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: zoompeoples
blocked_by: []
relates: [PW-667, PW-669]
refs: [planet/api.py, planet/server.py, viewer/index.html, viewer/zoom.html]
---

## Description
Zooms with a peoples run's land use can only be made from the CLI (`planet zoom WORLD --lat --lon --peoples RUN`). The Zoom box on the globe (viewer/index.html) and `POST /api/zoom` (api.py parse and its `Z.zoom_id` / `Z.zoom` calls) do not carry a `peoples` field, so a world that shows the cleared-land tint (PW-669, `V.wAnthroRun`) cannot offer "zoom here with this run's land use".

What to try: an optional `peoples: RUN` in the zoom request (validated: a peoples run of that world with `meta.anthro`; its id goes into `Z.zoom_id`), and a checkbox "with the peoples' land (run X)" in the zoom box when the world has a peoples run (`V.wAnthroRun`), default on while "show cleared land" is on. The zoom page should name the run (`meta.peoples.run`) in its summary and link to it.
- [ ] a zoom made from the viewer on 1df1c3 with run d489d0 equals the CLI one (same id)
- [ ] the box has no such checkbox on a world without a peoples run
