---
id: PW-1634
title: planet make (and the viewer's make) runs the language pass by default after the peoples stage
type: task
status: todo
parent: PW-767
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lang-coordinator
blocked_by: []
relates: [PW-1555, PW-986]
refs: ["planet/__main__.py::cmd_make", "planet/make.py::make", "planet/make.py::estimate", "planet/make.py::parse_make_request", planet/language/run.py, "planet/__main__.py::cmd_languages", docs/coordination.md, "run a24559"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: a world made with `planet make --peoples` (or the viewer's Make button) has peoples but no languages
until someone runs `planet languages <run>` by hand. Daniel uses the viewer, not the CLI, so in practice his worlds
have no names or words. He agreed 11-09 that make should run the language pass by default once it was fast; lane 11
(PW-1555) brought it to ~11 min on a24559 at 8 workers. If never done, every new world lacks languages, names and the
names slot's state names.

Do: add a languages stage after the peoples stage (on by default when peoples are made, with an opt-out flag and a
request field for the viewer), include it in `estimate`, report progress, cap workers sensibly. Also the regenerated
gods.json matters: run the religion readout first if the pass needs it, so faiths are not re-derived (~87 s).

## Updates
- 2026-11-10: Created from inbox draft draft-make-runs-languages.md (found by lang-coordinator).
