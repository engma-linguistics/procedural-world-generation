---
title: The first faith edit after a server restart re-reads the whole run (gods inputs kept only in memory)
type: task
status: todo
parent: null
milestone: later
subsystem: infra
effort: s
impact: low
found_by: lane166
blocked_by: []
relates: [PW-1430]
refs: ["planet/server.py::gods_doc", "planet/server.py::disk_cached", "planet/lineages/gods.py::inputs", "planet/lineages/gods.py::replay", "run b4d502"]
---

## Description
In plain words: opening the Religion tab is now instant after a restart (the gods and taboos docs are cached on disk under
<data root>/.godscache), but the first save of a written faith, or the first gods-mode switch, after a restart still pays the slow
part, `gods.inputs()` (~20-25 s at L7 on a quiet machine, minutes under load), because those inputs (~150 MB per L7 run) are kept only in
the server's memory. Later edits take ~5 s. What goes wrong if this is never done: Daniel waits a few minutes the first time he edits a faith
on a loaded machine and may think the save hung. Options: pickle the inputs into .godscache (about 150 MB per run, pruned to the last
run or two), or show a "working out the run's land first" note in the editor while the save is pending.
