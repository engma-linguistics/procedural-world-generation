---
title: "Tech tree build takes ~22 s a run with 547 techs (was ~5 s with 102)"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-69
blocked_by: []
relates: [PW-1122]
refs: [planet/lineages/techtree.py]
---

## Description
techtree.build loops over 360 time steps x living peoples x techs in Python (and over every tech per contact pair per step). With
the catalogue ingested (547 techs) a D&D run's build went from ~5 s to ~20-24 s (runs 488d7e 6128a3 114231 570701), on a loaded
machine. It runs once per peoples run (output.save) and on `planet techtree`, and anchor_check builds once per seed per tech
(~2 s per tech at 21 seeds). Fine for now; if it bites: skip techs whose needs are not all known (keep a per-people frontier set
instead of scanning `order`), and in diffusion loop only the giver's known techs.
