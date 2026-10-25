---
title: "Star anchor: choose the forcing's zero point together with the CO2 balance (PCO2_BALANCE 500 ppm) and the 300 Myr spin-up reference, or anchored runs start in deep ice and end CO2-starved"
type: task
status: needs-decision
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: star-anchor-audit
blocked_by: []
relates: [PW-791, PW-559, PW-798, PW-806, PW-708]
refs: [planet/tectonics/earth.py, planet/climate.py, docs/review/base-climate/star-anchor-audit/]
---

## Description
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
