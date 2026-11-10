---
title: "Andes (PW-1497 pass 4): share 0.1 + post-orogenic collapse passes 3 of 4 screen bars; finish the gate and read the continental-crust line"
type: task
status: needs-decision
parent: null
milestone: later
subsystem: tectonics
effort: m
impact: med
found_by: lane 275
blocked_by: []
relates: [PW-1497, PW-1509, PW-1446, PW-1293]
refs: [docs/review/tectonics/mountains/scout9.md, docs/review/tectonics/mountains/scout9_decay.py, docs/review/tectonics/mountains/scout7_measure.py, docs/review/tectonics/mountains/scout8.md, "planet/tectonics/crust.py::flow_and_orogeny", "planet/tectonics/crust.py::andean_contraction", "planet/tectonics/plate_kernels.py::crust_flow", tools/fork_screen.py, tools/scorecard.py, tools/hard_bar.py, "Braun & Robert 2005 ESPL 30:1203", "Baldwin, Whipple & Tucker 2003 JGR 108(B3)", "Menard & Molnar 1988 Nature 334:235", "Dewey 1988 Tectonics 7(6)"]
---

## Description
In plain words: the model never takes a mountain belt down after it stops being squeezed (its thick crust lasts
~260-390 Myr; on Earth a dead plateau collapses within ~10-50 Myr). Lane 275 added post-orogenic collapse (crust not
squeezed for 20 Myr flows 31x faster; volume kept; off by default, `collapse=30` turns it on) on top of the Andean
contraction patch. With `andean_shortening=0.1 collapse=30`, on L6 seeds 1, 2, 6001 x 600 Myr against main a784b8ea
on the same seeds: Andes share 21.5% mean (main 10.2%), land above 3 km 2.26% mean, max 3.29% (main 2.76%, max
4.00%), land within 1.4 points of main. Continental crust median: 37.9% on seed 1 (main 37.8% on that seed), 38.5%
and 38.9% on the others. If never done, PW-1497 stays closed as a known Earth difference and the code sits unused
(off by default) on main.

Decision (the continental line of scout8.md section 1, ">= 38%"):
- A. Read it per seed: seed 1 fails by 0.1 point (where main also fails), so the candidate fails; park again.
- B. Read it over the three seeds (median 38.5%): the candidate passes the screen; finish the gate below.
Lean: B, since main itself is below the line on that seed, but it is the owner's or coordinator's reading, not mine.

Gate still to run (lane 275 handed off before it finished):
- [ ] forked screen (`tools/fork_screen.py`, seeds 1, 2, 77, 3199; main base+rng1-3, fpnull, candidate base+rng1-3;
      jobs in the lane's scratch `fork/cont.jobs`; the candidate is the branch with defaults 0.1 / 30)
- [ ] `tools/scorecard.py --jobs 2 --threads 4` with the defaults on, against main's latest line (re-run main's if
      planet/ changed since its commit)
- [ ] hard-failure judge (`tools/hard_bar.py` over paired draws)
- [ ] if all hold: defaults on, `--update-golden`, overview.md section 7 "Andean margin" rewritten, PW-1497 reopened
      and closed done
