---
id: PW-639
title: "The NE Atlantic's warmth sits in a narrow inflow trunk west of 15W: Rockall 55-62N +2.7 C too warm, while the eastern Atlantic at 42-50N and Biscay are 3 C too cold (inflow share 0 east of 15W south of 50N)"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: ocean
effort: m
impact: med
found_by: base-climate-laneA20
blocked_by: []
relates: [PW-592, PW-582, PW-589]
refs: [planet/ocean.py, planet/climate.py, docs/review/base-climate/laneA20/eumap_main.txt, docs/review/base-climate/laneA20/shelfdiag_main.txt, docs/review/base-climate/laneA20/shelfdiag_slopelat.txt]
created: 2026-10-23
updated: 2026-10-23
---

## Description
This is what is left of PW-592 after lane A20's shelf seas. It is the open-sea part ("NH open sea 45-65N within 2 C").
Earth L6, annual SST minus NCEP annual air (`laneA20/eumap_main.txt`; the SST should be about 1 C above the air):
- **The trunk.** At 54-62N, 30-15W the SST is +3 to +4 above the air. There the inflow's share of the surface
  water is 0.9-1.0 and the overturning's heat is +7 to +8 C.
- **The east.** East of 15W south of 50N, the inflow's share is 0 and the overturning's heat is ~0. The whole
  eastern Atlantic at 42-50N is -2 to -3 below the air, including Biscay (754 m deep, so not a shelf: -3.0).
  Its gyre carry is -1 to -2 (the Canary current's cold return).
- **Why.** The inflow is routed along single shortest-cost paths (`_paths`) to the sinking sites. Its share
  saturates within a few km of width (`moc_q0`), so the route's spread over `moc_km` (300 km) sets its width,
  whatever its transport. The real North Atlantic Current's heat spreads over the whole eastern basin at
  45-60N.
- **Tried and dropped** (`shelfdiag_slopelat.txt`): letting PW-582's slope current act from 25, 35 or 40 deg instead of
  `moc_lat` doesn't move the trunk onto Europe's margin. It only warms the trunk (Rockall +2.6 -> +3.3).

Candidates:
- the inflow's width from its transport (Q / (U H) at the currents it rides) rather than a fixed 300 km;
- the inflow's heat given to the air downstream, which then warms the eastern basin. This is the atmospheric side
  of A20's shelf rule, extended to the open sea. It is a bigger change and needs a planet-relative argument
  for the air's reach.
- [ ] NH open sea 45-65N within 2 C, with Biscay / the E Atlantic 42-50N within 2 C, the band means kept, and stage
  1 holding

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Created from inbox draft draft-ne-atlantic-inflow-trunk-too-narrow.md (found by base-climate-laneA20).
