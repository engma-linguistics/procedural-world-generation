---
id: PW-969
title: "Largest plate still peaks at 44-57% for tens of Myr: at the start, at the first reassembly (~200 Myr), and after big sutures"
type: task
status: todo
parent: PW-244
milestone: v2
subsystem: tectonics
effort: m
impact: med
found_by: lane22
blocked_by: []
relates: [PW-827, PW-565, PW-952]
refs: [planet/tectonics/events.py, planet/tectonics/setup.py, docs/review/tectonics/rifts/rifts.md]
created: 2026-10-28
updated: 2026-10-31
---

## Description
After lane 22's rift fixes the largest plate over 600-1000 Myr averages ~26% on five example runs (main 41%; Earth
~20%), but three kinds of peak remain (docs/review/tectonics/rifts/rifts.md, runs 32b140 f7a9b6 b63d9d 2efa01
addc9f):
- t = 0: every run starts with a ~47% plate, the starting supercontinent's plate with its ocean around it.
- ~200 Myr: 45-55% on every run, the first reassembly, when sutures weld whole plates (continent and all the ocean
  floor they carry) into one.
- late: 44-57% for a few tens of Myr after a big suture (e.g. L6 seed 2 at 800 Myr 49%, seed 1 at 1000 Myr 44%).
On Earth a supercontinent's plate didn't carry half the planet's ocean floor with it: Panthalassa had its own plates.
What to look at: (1) whether the starting set-up should give the supercontinent's plate less ocean (setup.py);
(2) whether a suture should weld only the colliding plates' continental parts and the floor within some distance,
leaving the rest to break off along an old ridge or fracture zone; (3) after a suture, whether the welded plate's
ocean floor fails by margin subduction soon enough. Measure: largest plate share per 10 Myr over 0-1000 Myr on
5+ seeds; time spent above 40%.
- [ ] time with the largest plate above 40% after 300 Myr falls to < ~10% of the run on ~70% of seeds

## Updates
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-28: Created from inbox draft draft-giant-plate-peaks-after-sutures.md (found by lane22).
