---
id: PW-809
title: Anchor the star's brightening at the run's end ("now"), full Gough, with an optional star_now_offset_myr; decide what the forcing is counted against
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: v1-finish-9
blocked_by: []
relates: [PW-761, PW-780, PW-791, PW-806]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, docs/review/base-climate/v1-finish-9/, planet/climate.py, docs/review/base-climate/star-anchor-audit/]
created: 2026-10-24
updated: 2026-10-25
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
- 2026-10-25: v1-finish-11: carbon balance anchored at the end (GEOCARB frame, ruling A): weathering reference = planted potential vegetation at the balance climate; GEOCARB III CO2 laws and a runoff factor; thermostat returns ~57-70% (was 37%). Full Gough alone 0/6 L6 strict (dT med -2..+2); with the thermostat 16/18. Decision: draft-balance-climate-vs-bar.md. docs/review/base-climate/v1-finish-11/README.md
- 2026-10-24: v1-finish-10: B built. earth.star_forcing counts against today's Sun (age 4570 - run_end + t); start_carbon sets the start's stock for the dim star; the spin-up's sink reference is taken to the balance climate per cell (temp_response), so a cold spin-up is not learnt as the balance. star_now_offset_myr added. Measured: full Gough alone 0/6 L6 strict (all ICEBOX), the thermostat 3/6 first wave; the cause is the carbon cycle (draft-anchored-run-ends-co2-starved.md). docs/review/base-climate/v1-finish-10/README.md
- 2026-10-24: Merged inbox draft draft-star-anchor-zero-point-co2-balance.md ("Star anchor: choose the forcing's zero point together with the CO2 balance (PCO2_BALANCE 500 ppm) and the 300 Myr spin-up reference, or anchored runs start in deep ice and end CO2-starved", found by star-anchor-audit).
  Audit items 1, 2 and 13 (docs/review/base-climate/star-anchor-audit/README.md).
  
  Today three things share t = 0:
  - the climate's dT = 0, which is Earth now, under the present Sun;
  - the CO2 balance, `climate.PCO2_BALANCE` = 500 ppm. The references follow the rates until `REF_FREEZE` (300 Myr)
    and are then kept;
  - the star, `earth.star_forcing`, whose forcing is 0 at t = 0.
  
  The owner's anchor (a run's end is now, PW-791) moves the star's "now" to the end.
  
  **The interaction:** during the spin-up the references follow the sink. Whatever star level the spin-up has is
  learnt as the balance, and the CO2 doesn't push back against it.
  
  Worked example, measuring the forcing from the end, 1 Gyr, before the ice-albedo feedback:
  - full Gough: it starts at ~-14 C, reaches ~-9 C by the freeze, and ends near dT 0 at ~165 ppm;
  - 0.45: the start is -7.3 C raw against now.
  
  The physical answer to a faint young Sun is *high* early CO2. Here the reference cancels that.
  
  PCO2_BALANCE 500 was itself picked on icehouse share before the star existed (378a927, PW-559 B: 45% at today's
  pCO2, 19% at 500, 0% at 700). So it is a warm calibration aimed at the same late-cooling trend that the star now
  also offsets.
  
  Options:
  - A. Keep the forcing's zero at the run's start (today's form), only re-evaluating Gough between 4570 - T and 4570.
    Simple, but then "now" at the run's end is not the climate's dT = 0 baseline.
  - B. Zero at the run's end (present Sun = dT 0), and derive the balance for the start's dimmer star. For example,
    PCO2_BALANCE becomes the pCO2 that holds the spin-up near dT ~0..+1.5 against star_forcing(0) through co2_term,
    planet-relative and computed from the anchor. A per-preset offset would not do this.
  - C. B, plus a spin-up reference that keeps the thermostat active during the spin-up (the references follow the
    rates, but the CO2 still answers the star). PW-576 dropped relearning references, so this needs care.
  
  Lean B: one formula, no per-world number. The end then reads as "now" in both star and climate. Re-check PW-806's
  low-pCO2 share after it.
  - [ ] zero point chosen and written in earth.star_forcing's docstring
  - [ ] a 1 Gyr L6 Earth-like run's dT over 0-300 Myr is not an always-icebox, and its end pCO2 is within ~180-600 ppm
  - [ ] the PCO2_BALANCE comment says how it relates to the anchored star
- 2026-10-24: Status needs-decision -> todo. Coordinator ruling: B. Count the forcing against today's Sun (faint young Sun at the start, 0 at the end); set the starting carbon stock / spin-up references for the dim star so runs don't start as snowballs. Physically right; Earth stayed warm early through high CO2.
- 2026-10-24: Created from inbox draft draft-star-anchor-at-run-end.md (found by v1-finish-9).
