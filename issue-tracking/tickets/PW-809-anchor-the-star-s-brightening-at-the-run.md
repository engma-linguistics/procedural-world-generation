---
id: PW-809
title: Anchor the star's brightening at the run's end ("now"), full Gough, with an optional star_now_offset_myr; decide what the forcing is counted against
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-finish-9
blocked_by: []
relates: [PW-761, PW-780, PW-791, PW-806]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, docs/review/base-climate/v1-finish-9/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
Owner ruling (2026-10-24, via the coordinator): a run of length T spans star ages 4570 - T .. 4570 Myr, so it ends
under today's Sun; full Gough (1981) unless the evidence says otherwise; an optional, plainly labelled
`star_now_offset_myr` (default 0, > 0: the run ends that far in the future). Not started in v1-finish-9 (handed off
at its tool budget). The design question that has to be settled first:

Today `earth.star_forcing` counts the brightening against the run's START (dT = 0 at t = 0, the planet's carbon-cycle
references learnt over its first 300 Myr). Anchoring the star's age at the end leaves two readings:
- A. Keep counting against the start (planet-relative). A 1 Gyr run then brightens 4570-1000 -> 4570 Myr: +8.0% of
  luminosity, ~+15 C of raw forcing, about the Sun-like 1.0 rate that made 16/18 L6 1 Gyr runs ice-free in
  v1-finish-7; a 2 Gyr run +17.5% (~+34 C raw). The run still ENDS hot; the anchor alone does not remove the late
  hothouse.
- B. Count against today's Sun (dT = 0 is Earth under today's Sun, which is how the climate model's dT is defined):
  forcing = 238 x lambda x (L(age)/L_now - 1), negative early (-15 C raw at the start of a 1 Gyr run, -34 C for 2 Gyr)
  and 0 at the end. Physically this is the faint-young-Sun setup: Earth stayed habitable because CO2 was much higher
  early. In the model it needs the carbon cycle to build that CO2: the spin-up references (REF_MYR / REF_FREEZE) follow
  the planet's rates for 300 Myr and would learn a frozen planet's slow weathering as its balance, and co2_term levels
  off toward CO2_MAX. Expect snowball starts unless the start's CO2 or the references are set for the dim star.
Lean: B (it is what "the end is now" means, and it makes the last ~500 Myr sit under at most today's Sun), with the
start's carbon stock set from the dim star's balance rather than a frozen spin-up. Then re-measure the strict bar
(L6 18 draws and L7 8 at 1 Gyr, L6 13 at 2 Gyr), tree cover, the wet-tropics check and pCO2; only then decide whether
the PW-791 thermostat (in the branch, opt-in, off) is needed by default.
- [ ] star_forcing anchored at the run's end, star_now_offset_myr labelled in params and the README
- [ ] strict bar re-measured: L6 >= 13/18, L7 >= 7/8 at 1 Gyr; 1500-2000 Myr window ~70% at L6 2 Gyr

## Updates
- 2026-10-24: Status needs-decision -> todo. Coordinator ruling: B. Count the forcing against today's Sun (faint young Sun at the start, 0 at the end); set the starting carbon stock / spin-up references for the dim star so runs don't start as snowballs. Physically right; Earth stayed warm early through high CO2.
- 2026-10-24: Created from inbox draft draft-star-anchor-at-run-end.md (found by v1-finish-9).
