---
title: coordination.md describes the old --at auto rule
type: task
status: todo
parent: null
subsystem: docs
effort: xs
impact: low
found_by: lane110
blocked_by: []
relates: []
refs: [docs/coordination.md, planet/highlights.py, "runs a19366 10fd90 f27dc1 fe954c c9f38c 5aa5ff"]
---

## Description
In plain words: the showcase recipe text says `--at auto` picks a middle-of-the-road moment by medians, but the code now picks the finish moment.

docs/coordination.md "Showcase recipes" says auto picks the keyframe nearest the run's medians among frames after 300 Myr. `highlights.representative_time` now returns the stored `finish_moment` (the run's end when habitable, otherwise a warm or interglacial moment). On six fresh level-7 runs every auto pick was the run's end (1000, 1500, 2000 Myr); three of them (water, cold, hothouse) reported no human-habitable moment in the last 10 Myr and fell back to the end. Update the text, or decide whether showcases want the median rule back (judgement call for Daniel).
- [ ] coordination.md matches `representative_time`
