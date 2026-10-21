---
id: PW-527
title: Earth time zoom puts no ice, hence no outwash or loess, on the Great Lakes and Mississippi valley
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: pw497
blocked_by: []
relates: [PW-497, PW-037, PW-033, PW-435]
refs: [planet/timezoom/deposit.py, planet/timezoom/sim.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Outwash and loess (PW-497) follow the ice. In an Earth L6 time zoom (600 kyr, store run 32a6bc in the
pw497 scratch store) the Laurentide never reaches the Great Lakes: no till, outwash or loess at all
in 36-52 N, 105-75 W, so the Mississippi-valley loess analogue cannot appear. The Scandinavian sheet
is thin and mostly north of 60 N: central Europe (46-52 N, 8-25 E) gets 0.6 m of till and no
outwash or loess; the loess that exists is 60-70 N (50 cells, max ~4 m) and a few cells at 45-56 N (max 0.6 m).
The deposit routing itself works (volume conserved, downwind of the plains); the ice sheets' extent is
PW-033 / PW-435 territory (ice-age physics, parked).
- [ ] after the sheets reach 40-50 N: re-check outwash south of the margins and loess east/downwind
      of them (Earth: central Europe and the Mississippi valley, 5-30 m locally)

## Updates
- 2026-10-21: Coordinator: PW-471's acceptance had the Laurentide reaching 42.5 N at glacial maxima; check whether this is a frame-sampling difference (final frame vs max) or a real regression before anything else.
- 2026-10-21: Created from inbox draft draft-earth-timezoom-ice-misses-loess-lands.md (found by pw497).
