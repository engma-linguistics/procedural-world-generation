---
title: "Peoples made outside planet make still run the language pass on one process, with no progress or opt-out"
type: task
status: todo
parent: PW-767
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lang-lane12
blocked_by: []
relates: [PW-1634, PW-1555]
refs: ["planet/lineages/output.py::save", "planet/lineages/run.py::job", "planet/lineages/run.py::run", "planet/api.py::lineages_job", "planet/make.py::make", "planet/language/run.py::write", "planet/language/history.py::WORKERS", viewer/navigator.js, viewer/lineages.html]
---

## Description
In plain words: PW-1634 made `planet make` run the languages as their own step, with 8 workers, progress and a way to
switch them off. But peoples made any other way, the viewer's "Make peoples" / "Run on world" in the tree editor
(POST /api/lineages) or `planet peoples`, still run the language pass inside the peoples step: on a single process
(history.WORKERS defaults to 1 unless LANG_WORKERS is set), with the progress bar frozen at the end of the peoples
history, and no way to skip it. A one-process pass takes several times the 11 minutes it takes on a24559 with 8
workers (not timed here).

If never done: Daniel, who makes peoples from the viewer, waits a long time with a stuck progress bar for each
peoples run, or kills the job and gets peoples with no names.

Do: give POST /api/lineages the same `languages` and `language_workers` fields as make (lineages.run.job already
takes `languages`), and run the pass after `run()` in the job with the job's progress, as make.py does; a checkbox
in the tree editor's run panel. The peoples stage itself should then never run the pass (drop the call in
output.save), so there is one place it is run from.
