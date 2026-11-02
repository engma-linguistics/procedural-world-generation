---
title: Gods mode (faith_made | belief_only | absolute) as a world-creation control and a stored meta field
type: task
status: todo
parent: PW-1308
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: lane117
blocked_by: []
relates: [PW-1306, PW-1304, PW-711]
refs: [planet/lineages/gods.py::Pantheons, planet/lineages/gods.py::derive, planet/lineages/techtree.py::build, planet/lineages/techtree.py::rebuild, planet/lineages/spec.py, planet/lineages/output.py, planet/server.py::gods, planet/__main__.py::cmd_religion, viewer/lineages.html, docs/review/religion/slice1.md, "run b4d502", "run a24559"]
---

## Description
In plain words: the three gods modes exist in code but Daniel can only pick one through `planet religion --mode` or `/api/gods?mode=`. He uses the viewer, so the
mode needs a control where a world or tree is created, and it needs to be saved with the run.

What exists (lane 117): `techtree.build(gods_mode=)` drops divine magic in `belief_only` and stores `gods_mode` in `meta.techtree`; `gods.derive(mode)` changes the
readout words and the spell flag only (the history is identical in every mode). A new run always writes `faith_made` (output.py calls `taboos.write_religion` with
the default). `techtree.for_run` / `rebuild` read `meta.gods_mode` when present, but nothing writes that field.

To do:
- [ ] `gods_mode` on the tree spec / run request (spec.Tree, run.py request), saved into `meta.gods_mode`, passed to `techtree.build` in output.py and to `write_religion`.
- [ ] A control next to the mode/era choices in the viewer's tree tab (and the world-creation form PW-711 when it exists).
- [ ] The Cultures tab's gods column shows the run's mode and re-fetches `/api/gods?mode=` when the user flips it (the endpoint already supports it).
