---
title: "Endings test at L4 fails with honest margins: a ~440 km margin cell's Nye ramp is a 1.2-2.6 km dome"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: ice-v2-stage1
blocked_by: []
relates: [PW-555, PW-460, PW-115]
refs: [tests/test_timezoom_cycle.py, planet/icemass.py, docs/review/ice-v2/stage-1.md]
---

## Description
`test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast` (sim4, L4, 4 C colder, 6 C glacial
by hand) fails on the stage-1 branch: the first ending keeps 25 of 29 m after 15 kyr (bar: under half).
`icemass.margin_ramp` is grid-relative, so at L4 a margin cell's ramp quadrature heights are 1.2 / 2.6 km:
the margin is as cold as a dome. The same moment gives back 0.67 with the 408 m edge and 0.60 with no
carried sheet air (`tzdiag.py`, stage-1 scratch). Earth at L6 passes the same bar (0.64–0.91).
Options:
- A: keep the test at L4 and make the margin physics pass there too (the lever in stage 1's handoff).
- B: move the test to L5 (~220 km cells), the coarsest grid where honest margins are meant to work; a
  slower fixture (~20 s).
- C: both: B now, A as the physics allows.
Lean: A first (it's within stage 1's remaining attempt); B only if L4 is shown to be a resolution limit, not
a physics gap. Don't loosen the bar.
