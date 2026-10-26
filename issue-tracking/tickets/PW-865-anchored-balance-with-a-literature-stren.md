---
id: PW-865
title: "Anchored balance: with a literature-strength thermostat the planet sits at its balance climate (+1.5 C, 500 ppm), too icy for the strict bar; the star thermostat passes it (16/18 L6) only by pinning at +4% luminosity, with warm finishes and treeless wet tropics"
type: task
status: in-progress
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-finish-11
blocked_by: []
relates: [PW-809, PW-810, PW-791, PW-806, PW-812, PW-559]
refs: [planet/tectonics/earth.py, planet/climate.py, docs/review/base-climate/v1-finish-11/]
created: 2026-10-25
updated: 2026-10-25
---

## Description
v1-finish-11 anchored the carbon balance at the run's end (GEOCARB frame: the weathering reference is planted land
at the balance climate; bare land weathers 1/3 as fast) and gave the sink GEOCARB III's laws (bare X^0.5, planted
(2X/(1+X))^0.4, runoff^0.65 on the climate's 3%/C rain). The thermostat now returns ~57-70% of a lasting forcing
(was 37%), inside GEOCARB's own ~50-70%, and the anchored runs carry 750-2400 ppm medians (the Phanerozoic's scale).
Results, L6 1 Gyr, strict bar unchanged (docs/review/base-climate/v1-finish-11/README.md):
- full Gough alone: 0/6 (icehouse 42-95%, dT median -2.0..+2.2; two at 42.0%);
- + star thermostat: 16/18, but star_ctl sits at +5..+7.7 C (its +4% bound) from ~300 Myr to the end, so the run
  ends under a Sun ~4% brighter than today's; end pCO2 39-906 (10/18 in 180-600), finished true mean outside the
  owner's -6..+3 C on 9/18 (all too warm), land ice at the finish < 6% of land on 12/18 (Earth ~10%), wet
  equatorial lowland trees >= 20% on only 3/18 (PW-806's hard check);
- + star thermostat, L7: 2/2 (6 draws not run); 2 Gyr L6 late window 1500-2000 8/13 (62%, bar ~70%), the
  300-1000 Myr part ICEBOX or > 55% on every 2 Gyr draw (Sun 13-17% fainter, beyond the bound);
- wet-eq trees stay 1-4% even at 400-500 ppm end pCO2 on the 2 Gyr draws (thermostat-free runs 3-39%), so the
  brighter-than-today star's tropical heat is a likely second cause (PW-806), unmeasured;
- probe, alone + climate_offset 2.5: 3/6 (the draws' spread is wider than one offset).

The cause, now that the thermostat is physical: after the forests, a strong thermostat holds a planet near its
balance climate whatever forces it (star, thermostat push, any non-CO2 gas: ~2/3 is answered by CO2). The balance is
PCO2_BALANCE 500 ppm = dT +1.5, which on this model's ice is an icehouse most of the time; the bar's passing regime
is dT median >~ +2.5 (v1-signoff's passing runs +3..+5). Earth meets both a cold, low-CO2 present and a mostly warm
Phanerozoic only because its present is unusually weatherable/cold; in the model the end is a typical moment, so
"end ~Earth-now" (180-600 ppm, -6..+3 C) and "<= 40% icehouse over the run" pull against each other.

Options:
- A. Star thermostat as the earthlike v1 default (PW-810), accepting the +4% end star, warm finishes and the C3
  starvation in the wet tropics; then fix windup (it rides the bound) and PW-806 separately.
- B. A warmer balance: the long-run balance at the Phanerozoic's typical ~800-1000 ppm (Foster et al. 2017;
  Royer 2006) instead of 500, i.e. PCO2_BALANCE re-set under the end anchor, with the thermostat for the outliers at
  a smaller bound. Ends nearer 1000 ppm (outside the 180-600 diagnostic) but forests and the bar both easier.
- C. Keep the physics and re-read the bar for the end-anchored star: icehouse share counted on the last 540 Myr
  only, or a looser icehouse limit, since Earth's own record from 1 Ga includes the Cryogenian.
Lean: B with a small thermostat bound, measured against all three diagnostics; A is a control dressed as physics
when it pins at its bound.
- [ ] option chosen
- [ ] re-measured: L6 18, L7 8, 2 Gyr 13; end pCO2, finish T and ice, wet-tropics trees

## Updates
- 2026-10-25: v1-finish-13: drift sized (dfc8b48) and the coupling-audit carbon couplings (PW-880/881/875/873, 1b52cdf) in; full set (L6 18, 2 Gyr 13, L7 8) running on 1b52cdf (prefix cpl), not tallied at hand-off. Habitable-screen diagnostic (screen.py) on the shade set: a passing moment within 5/10/20 Myr of the end 14/15/15 of 18; the end itself 12/18.
- 2026-10-25: v1-finish-13: shade-only L6 1 Gyr (be00f07, plants' light from the climate's sunshine): bar 15/18, bar + hard finish checks 10/18, wet-eq trees 18/18 (was 5/10), finish T 12/18 (fails warm: +3.2..+9.5), land ice 16/18, end pCO2 180-600 9/18. Drift sized for what the model lacks (dfc8b48, 0.8 C); full set re-running on it. docs/review/base-climate/v1-finish-13/
- 2026-10-25: v1-finish-12: harness on the ruled bar (passrate4.py, no cap). v1-finish-11 physics, thermostat off, 10 of 18 L6 1 Gyr draws: bar 7/10, bar + hard finish checks 3/10 (wet-eq trees 5/10, finish T 8/10, land ice 10/10). Plants' light fix committed (be00f07), so the full set (L6 18, 2 Gyr 13, L7 8) is re-running on it (lane.sh shade); not tallied at hand-off. docs/review/base-climate/v1-finish-12/README.md
- 2026-10-25: Status needs-decision -> in-progress. RULING (owner): option C. Keep the physics: GEOCARB end anchor, literature-strength weathering, star thermostat off. Loosen the icehouse bar: no cap on the share of a run's time under polar ice. Snowball/always-icebox, hellhole and never-ice still fail, and ~70% of draws must pass. The owner's finish checks stay: true mean -6..+3 C and interglacial land ice ~Earth's. Coordinator: the wet-tropics trees >= 20% hard check also stays.
- 2026-10-25: Created from inbox draft draft-balance-climate-vs-bar.md (found by v1-finish-11).
