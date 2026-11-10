---
id: PW-1634
title: planet make (and the viewer's make) runs the language pass by default after the peoples stage
type: task
status: done
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
- 2026-11-10: Status todo -> done. Lane 12: make runs the language pass as its own stage after peoples (on by default; CLI --no-languages / --language-workers N, request fields languages / language_workers, viewer New planet checkbox), default 8 workers (1-16), estimate make.LANGUAGES_S (L6 ~7 min, L7 ~11 min), per-interval progress. The peoples stage leaves the pass to it (lineages job/run/save languages=False). gods.json with faiths is written by the peoples stage first, so faiths are not re-derived (2.6 s). A failure (e.g. a time zoom under 20 kyr) is logged in run.txt, not fatal. Tested: L6 200 Myr make --peoples into a scratch data root, 422 living, 423 s. Peoples made outside make: draft-viewer-peoples-job-languages-single-process.
- 2026-11-10: Created from inbox draft draft-make-runs-languages.md (found by lang-coordinator).
