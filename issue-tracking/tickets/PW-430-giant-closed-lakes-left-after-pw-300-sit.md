---
id: PW-430
title: Giant closed lakes left after PW-300 sit in hollows that never spilled, made in a step or two on flat interiors
type: task
status: todo
parent: null
milestone: null
subsystem: hydrology
effort: m
impact: med
found_by: pw300
blocked_by: []
relates: [PW-300, PW-359, PW-054]
refs: [planet/hydrology.py, planet/tectonics/plate_kernels.py, docs/review/health-pw300-after/, docs/review/health-pw300-after/diag/]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-300's valley memory keeps the outlet a basin cut while it spilled, so a basin that used to spill no
longer flips to a giant closed lake (seed 11 @ 200-224 Myr: 4.6-6.9 Mkm2 closed, inland 36-40%, is gone).
What's left of the giant frames (health --quick after PW-300: 39 of 904 frames over 1 Mkm2, 8 in ice ages)
is mostly lakes in hollows that never spilled, so have no outlet to remember:
- closed and shallow on flat plains, in wet or dry climates: seed 77 @ 68 Myr 2.4 Mkm2 closed under 2009 mm
  of rain (level 21 m below its spill, median depth 39 m); seed 42 @ 436/452 3.7-3.8 Mkm2 closed under
  ~800 mm (median depth 17-28 m); seed 11 @ 192 4.3 Mkm2 closed (same with or without the memory);
  seed 21 @ 476-484 2.0-2.7 Mkm2 closed under 120-180 mm (a hyperarid playa basin: plausible);
- open, deep and broad (seed 77 @ 400 2.9 Mkm2, 120 m median depth; seed 42 @ 496 3.7 Mkm2, 70 m), where
  the frame's routing leaves the lake over higher ground than the bed's own spill height (seed 42 @ 496:
  level 758 m vs priority-flood spill 699 m, outflow path 663 -> 762 -> 794 -> 964 m): worth a look at why
  (_bed's fill_shallow / MIN_SLOPE plains filled above a neighbouring hollow's spill?).
A humid hollow that only needs ~20 m more water to spill would, on Earth, have been crossed by its river
while it formed (antecedence), unless it formed faster than the river cuts: PW-359 found plate motion and
nearest-cell resampling make most closed-hollow volume each step, in one step. So this is mostly PW-359's
(an interpolating world view); the routing question in the second bullet is hydrology's.
Probe scripts: docs/review/health-pw300-after/diag/probe.py (`probe.py <repo> <seed> <t>...`),
hollow_origin.py (what changed under a lake between steps).

## Updates
- 2026-10-16: Created from inbox draft draft-fresh-hollow-closed-lakes.md (found by pw300).
