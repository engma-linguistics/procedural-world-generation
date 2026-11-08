---
id: PW-1309
title: Gods mode (faith_made | belief_only | absolute) as a world-creation control and a stored meta field
type: task
status: done
parent: PW-1308
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: lane117
blocked_by: []
relates: [PW-1306, PW-1304, PW-711]
refs: ["planet/lineages/gods.py::Pantheons", "planet/lineages/gods.py::derive", "planet/lineages/techtree.py::build", "planet/lineages/techtree.py::rebuild", planet/lineages/spec.py, planet/lineages/output.py, "planet/server.py::gods", "planet/__main__.py::cmd_religion", viewer/lineages.html, docs/review/religion/slice1.md, "run b4d502", "run a24559"]
created: 2026-11-02
updated: 2026-11-03
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

## Updates
- 2026-11-03: Lane 167: the rest done. gods_mode is a tree meta field (meta.gods_mode, the workbench tree's Gods select beside the target era) and a request field (POST /api/lineages and /api/make gods_mode; the New planet form's peoples step has a Gods select); output.py passes it to techtree.build and write_religion and stores it in run.json meta.gods_mode; /api/gods defaults to it when authored.json has no mode. Belief only now drops divine magic from the first build. Cultures-tab column already re-fetched on the Religion tab's select (lane 166).
- 2026-11-03: Lane 166: viewer part done: a gods-mode select in the Religion tab bar, saved per run in authored.json (gods_mode) and used by /api/gods, taboos and the faith map when no mode= is asked. Left: gods_mode on the tree spec / run request at world creation, so techtree.build drops divine magic in belief_only (the stored meta.techtree still has it for runs switched later in the viewer).
- 2026-11-03: Milestones 11-03: later -> v2: v2 must-have: gods mode as a viewer control, with authored faiths
- 2026-11-03: Triage 11-03: v2 -> later: viewer nicety, not needed for the culinary goal
- 2026-11-02: Created from inbox draft draft-gods-mode-world-control.md (found by lane117).
