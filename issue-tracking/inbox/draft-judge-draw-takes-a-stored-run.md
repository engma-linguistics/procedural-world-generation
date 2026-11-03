---
title: tools/judge.py judge_draw takes a loaded raw record, so hard_bar --run needs only a loader
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: s
impact: low
found_by: lane151
blocked_by: []
relates: [PW-1272, PW-1393]
refs: [tools/judge.py, tools/hard_bar.py, tools/ice_criteria.py, tools/ice_diag.py, PW-1272]
---

## Description
In plain words: after PW-1393, one function (`tools/judge.py::judge_draw(raw)`) gives the bar and finish-moment verdict for a draw, and both the paired judge and tools/hard_bar.py call it. PW-1272 (judge a stored run without re-simulating) is therefore down to building the `raw` dict (`steps`, `updates`, `params`) from a stored run's keyframe stats; I did not do it because the approximations (dT_end, the star control) need a ruling on which fields may be approximate. hard_bar.py also still has its own per-draw hard-failure code (ocean loss, CO2 crash, 8-fold fall) that could move into judge.py next to `judge_draw` when a second consumer appears.
- [ ] a loader from a stored run to the ice_diag record shape, saying which fields it approximates
- [ ] `hard_bar.py --run <id>` uses it
