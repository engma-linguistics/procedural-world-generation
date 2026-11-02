---
id: PW-1375
title: "Density ladder: run the tech tree inside the history instead of the stage proxies"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: l
impact: med
found_by: lane 136 / lane 137 (density ladder build)
blocked_by: []
relates: [PW-1275, PW-1350]
refs: ["planet/lineages/ladder.py::Ladder.tech", "planet/lineages/ladder.py::PLOUGH_STEPS", "planet/lineages/ladder.py::IRR_LAG", "planet/lineages/ladder.py::TERRACE_LAG", "planet/lineages/ladder.py::ERA_STAGE", planet/lineages/techtree.py, planet/lineages/samples/techtree.toml, planet/lineages/history/growth.py, docs/review/peoples/density-ladder/build.md, docs/review/peoples/density-ladder/ladder.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
The density ladder (PW-1275) needs each people's tech stage while the history runs (plough level bronze / iron / medieval, irrigation,
a hold's terraces). The tech tree (`techtree.py`) only runs after the history, on the saved run, so `ladder.Ladder.tech` uses proxies:
the plough stage from the time since a plough animal was taken up, stepped by the tree's own Earth dates (iron +3.2 kyr, medieval
+5.3 kyr: `PLOUGH_STEPS`), irrigation `IRR_LAG` = 3.5 kyr after cultivation, terraces `TERRACE_LAG` = 6.5 kyr after cultivation, all
capped by the tree's era (`meta.era`, `ERA_STAGE`). So two peoples who took up the plough at the same time stand on the same rung
whatever else they know, and the tree's prerequisites (moldboard plough, three-field, shaduf, noria) never move density.

What to try: run the food track of the tech tree inside the history (or a cheap per-step subset of it) and read the ladder's stage
from the techs actually known; then drop the lags. Check the cost per step on the robust suite (`tools/peoples_robust.py`).
- [ ] ladder stage from known techs, not lags
- [ ] before/after on the robust suite: rung densities and shares

## Updates
- 2026-11-02: Created from inbox draft draft-ladder-tech-tree-inside-history.md (found by lane 136 / lane 137 (density ladder build)).
