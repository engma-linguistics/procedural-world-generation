---
title: Time zoom frames carry only tree cover; shrubs, herbs and the named type are not stored or migration-limited
type: task
status: todo
parent: PW-184
milestone: later
subsystem: timezoom
effort: m
impact: low
found_by: pw213
blocked_by: []
relates: [PW-213, PW-103]
refs: [planet/timezoom/plants.py, planet/finish.py, planet/vegetation.py]
---

## Description
PW-213 stores `tree_cover` per frame (20 MB/Myr at L6, one layer) and limits only trees to migration
(`vegetation.SPREAD`); shrubs and herbs seed everywhere, so ground the ice leaves is grassy at once, and a
finished world starts from the trees alone (the rest re-settles in `HELD_STEPS`). Gaps:
- the frames have no `vegetation` (named type) or `plant_cover` layer, so the time-zoom tab shows only tree
  cover (the named type needs `classify`, which needs the frame's lakes, flow and soils);
- potentials are refreshed every 10 kyr: ground the ice leaves between two refreshes stays bare until the next
  (up to 10 kyr), and the frames of an interval take the climate of its end (plants.py grows the 10 kyr before
  each full climate);
- refugia are only "forested poleward of 40 deg through every glacial-maximum frame" (meta `vegetation_glacial`);
  PW-103 needs cells that kept forest while their neighbours lost it.
Try: migration-limit the shrubs (faster than trees), refresh the potential of newly open cells at the frame,
store `plant_cover`, and record the refugia properly.
