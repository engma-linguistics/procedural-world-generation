---
title: The peoples stage of `planet make` uses a rough time estimate (one number per level)
type: task
status: todo
parent: null
subsystem: peoples
effort: xs
impact: low
found_by: lane 153
blocked_by: []
relates: [PW-1394, PW-478]
refs: [planet/make.py::PEOPLES_S, docs/coordination.md, "runs b4d502", "run 1184cc"]
---

## Description
In plain words: the New planet form shows a time for each step. The new peoples step uses `PEOPLES_S` in planet/make.py: 25, 70, 220, 700 and 3000 s for levels 4 to 8. These come from `generated_in_s` of the 60 stored peoples runs (level 6: about 120 to 320 s, median ~220; level 7: 80 to 3100 s, median ~500, and it varies with the tree, the number of tries and machine load; level 8: 2700 to 3900 s). Level 4 and 5 are scaled, not measured. Measure peoples runs at levels 4 and 5 on a quiet machine, and say in the form that the step varies with the tree (seven_meals is slower than dnd at level 7), then put the numbers in the run-cost table of docs/coordination.md.
- [ ] PEOPLES_S measured for L4 and L5, per tree if they differ
- [ ] the run-cost table in docs/coordination.md has a peoples row
