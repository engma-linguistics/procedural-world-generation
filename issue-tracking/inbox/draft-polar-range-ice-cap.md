---
title: Ice caps 2.4 km thick on 7 km polar ranges give coldest months of -105 C
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: vegclim
blocked_by: []
relates: [PW-190, PW-203]
refs: [planet/tectonics/earth.py, tests/test_invariants.py]
---

## Description
After merging main (2026-10-15, with the vegetation feedbacks of PW-203 and main's ice/vegetation fixes), the L4 test run (seed 1, 300 Myr; tests/conftest.py sim4) grows a 2.4 km ice cap on a 7.1 km range at 78 N: the ice surface sits at ~9.5 km and its coldest month is -105 C (annual -80), which broke test_values_sane's -95 C bound (relaxed to -110 on the vegclim branch, with a comment). Not caused by one feedback: a seed sweep (L4, seeds 1-5, 300 Myr) gives coldest months of -33 to -105 with or without the vegetation feedbacks (without them seed 1 happens not to glaciate that range, -50; seed 4 reaches -69 to -82 either way); whether a high polar range glaciates is chaotic.

Real ice surfaces stop near 4 km (Antarctica) because a thick cap on a high range flows away to its sides and has too little snow at that height. Check whether ice_sheets limits ice thickness on high ground (precipitation falling off with height, flow to the margins; PW-190 land ice depth) and restore the -95 bound if it does.
