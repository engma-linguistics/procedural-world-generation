---
id: PW-422
title: "Time zoom margins: thin films the flow leaves beyond a front hide it from the margin rule (it takes interior snow)"
type: task
status: todo
parent: PW-470
subsystem: timezoom
effort: m
impact: med
found_by: pw418
blocked_by: []
relates: [PW-115, PW-418, PW-366]
refs: [planet/timezoom.py, "run:2c2810@536Myr"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`timezoom.simulate`'s margin rule (a margin cell = grounded ice next to land with <= 1 m of ice; its snow and
melt are an edge's, `edge_h` thick) is fooled by films: each 500-yr step's flow leaves a few m of ice (median
2-15 m) on the ring beyond a front, which the next step's balance melts off (-5 to -11 m/yr). While the film
lies, the real front cell (~0.8-1 km) has no "bare" neighbour, so it is not a margin and takes the interior's
balance. Measured from the L6 seed-2 run @ 580 Myr (e438c3, = 6d67bd) on main: at 0.5 kyr, 157 thick
(>= 300 m) cells sit behind films with smb median +0.46 m/yr, against -1.9 m/yr for the 82 thick cells
the rule does see as margins (148 / +0.05 at 10 kyr). This lets sheets advance onto warm land
(PW-418: ~14 rings in 20 kyr).
What doesn't work (tried in the PW-418 branch, not merged):
- "bare" = land under less ice than `edge_h`: 20 kyr from e438c3 -314 -> -148 m, but 50 kyr still -324.
- "bare" = land whose ice the step's melt removes: the margin, lowered to edge_h, melts out (~1 km in one
  500-yr step at -2 m/yr or more), the next cell becomes the margin, and the sheets melt away (+213 m in 20 kyr).
- the bounded mix (films only: < edge_h and melting out within the step): -155 m at 20 kyr, -360 at 50; and a
  2.5 km test dome on L4 land 5 C colder than sim4 collapses from 8.6 to 4.1 Mkm3 in 10 kyr (main keeps 10.0).
Both ways it's the same flaw: a ~100 km margin cell is either all edge (too much melt: the whole cell's mean
thickness can go in one step) or all interior (too little). It needs a sub-cell margin (PW-115: the share of
the cell that is ablation zone), and the melt applied within the step, not once before the flow (the step's
inflow to a margin isn't melted until the next step). Measure with the PW-418 repro (20/50 kyr from e438c3 @ 580
and 2c2810 @ 536) and tests/test_timezoom_consistency.py.
- [ ] fronts behind films get a margin's balance, without a melt cascade (a cold-world dome holds)

## Updates
- 2026-10-16: Created from inbox draft draft-timezoom-film-shielded-margins.md (found by pw418).
