---
id: PW-708
title: "Runs get icier after ~500 Myr: the icehouse share on 1 Gyr is ~36% median, 5 of 10 seeds within the owner's 40% bar, against 72-91% on the 300-500 Myr quick window"
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: climate
effort: s
impact: high
found_by: v1-finish
blocked_by: []
relates: [PW-559, PW-681, PW-653]
refs: [planet/tectonics/earth.py, planet/climate.py, docs/review/base-climate/v1-finish/]
created: 2026-10-23
updated: 2026-10-23
---

## Description
With the carbon cycle's balance at 500 ppm (`climate.PCO2_BALANCE`, lane v1-finish, PW-559 B), the two quick sweeps
(32 L6 seeds, judged on 300-500 Myr) pass the owner's icebox bar (icehouse <= ~40%) on 72% / 91% of seeds. The
icehouse median there is 19% / 14%, and there's no hellhole. On the 10 thermostat seeds over 1 Gyr (`ice_diag`,
judged on 300-1000 Myr) the median is 36%, and only 5 of 10 are at <= 40% (canonical basis without the fix: 47%, 3
of 10). Per seed (11, 13, 1, 21, 2, 3199, 42, 5, 7, 99): 3, 22, 51, 28, 57, 22, 54, 5, 43, 53. The 600-1000 Myr
part of a run is colder than its 300-500 Myr part.

Candidate causes, none measured yet:
- The source falls as the mantle's heat fades (`earth.heat`, `heat_halflife`), while the references are frozen at
  300 Myr (REF_FREEZE). Fewer ridges and arcs mean a lasting CO2 deficit, a slow cooling trend.
- The late ocean floor ages (stress rifts die out after ~600 Myr; docs/overview.md): spreading slows and the
  ridge source drops.
- Erosion supply rises as relief builds.

Options:
- A: find the trend's term (ice_diag's source/sink split on the 10 seeds: `srcsplit.py`, `srcparts.py` in
  thermostat-1024) and fix the mechanism. If it is fading heat, it may be real (Earth's degassing fell too), but it
  has to be weighed against the reference frozen at 300 Myr.
- B: accept: 1 Gyr pass ~50-60% over the whole history, with ice ages concentrated late. The showcase picks
  moments anyway.
- C: a balance of ~600 ppm: more warmth over the whole run, at the cost of more ice-free quick windows (700 ppm
  gave a median of 0% on 300-500 Myr).

Lean: A first (one measurement pass; the scripts exist), and C only if the trend proves real physics.
- [ ] the source/sink split of the late cooling on the 10 seeds
- [ ] the 1 Gyr pass rate against the owner's bar on >= 16 seeds after the decision

## Updates
- 2026-10-23: Status needs-decision -> todo. Coordinator's call: A first (one measurement pass, source/sink split over 300-1000 Myr) so the choice between B and C is informed; then decide and go to PW-202.
- 2026-10-23: Created from inbox draft draft-late-history-cooling-1gyr.md (found by v1-finish).
