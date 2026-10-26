---
title: "Anchored star: runs end cold and CO2-starved (end pCO2 25-250 ppm) because weatherability rises over the run against the reference frozen at 300 Myr (relief, then land plants at ~470 Ma), and the thermostat is weak (~40% compensation); the star can't hide it any more"
type: task
status: needs-decision
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-finish-10
blocked_by: []
relates: [PW-809, PW-815, PW-791, PW-810, PW-812, PW-708, PW-830, PW-806]
refs: [planet/tectonics/earth.py, planet/climate.py, docs/review/base-climate/v1-finish-10/]
---

## Description
v1-finish-10 anchored the star at the run's end (PW-809 B: forcing against today's Sun, carbon stock and spin-up
sink reference taken to the balance climate, so a dim start is met by high CO2) and put the plants on Earth's
calendar (PW-807). Measured at L6 1 Gyr on the strict bar (docs/review/base-climate/v1-finish-10/README.md):
- full Gough alone: 0/6 (every one ICEBOX, also in the last 540 Myr, where the star is only -4..0 C);
- 0.45 alone: 1/6 (ICEBOX or > 40%); end pCO2 79-207 ppm on the five fails;
- full Gough + the PW-791 thermostat: 3/6 on the first wave, but end pCO2 25-251 ppm and wet equatorial lowland
  trees 0-4% on four of six (C3 starvation): the thermostat brightens the star past today's to answer a
  carbon cycle that keeps drawing CO2 down.

The cause is in the carbon cycle, not the star:
1. **Weak thermostat.** The sink's temperature law acts on local temperature, which moves 0.5 (tropics) to 0.8
   (40 deg) per C of dT (climate.compute's profile; `earth.temp_response`); with weathering ~ X^0.4 the steady
   state passes only ~40% of a lasting forcing back (WEATHER_CO2 / (WEATHER_CO2 + WEATHER_K r G) ~ 0.63 left).
   A -15.5 C faint-young-Sun start stays ~10 C below balance. (PW-830's saturating law is the v2 fix; the runoff
   part of the feedback is near zero in the model: supply -0.008/C.)
2. **Rising weatherability against a frozen reference.** The reference is learnt over 0-300 Myr on bare land; relief
   builds up (PW-708) and land plants arrive at ~470 Ma (weathering factor 1.0 -> ~1.15-1.2), so the sink runs
   above its reference for the rest of the run and CO2 is drawn below PCO2_BALANCE. The old star (from age 0,
   0.45) cancelled exactly this with +5.6 C of late warming; anchored, the star ends at 0 and can't.

Options:
- A. Anchor the carbon balance at the end too (GEOCARB's frame): the sink's reference is the planet's
  weatherability with land plants (a planted-land plant factor), so bare early land weathers less (GEOCARB's f_E
  ~0.25-0.5 pre-plants against the model's ~0.8) and holds high CO2 early, and the plants' arrival brings it to the
  balance rather than below it. Physical; needs the plant weathering factor re-checked against the literature
  (Berner 1997/2004 f_E; Moulton et al. 2000: plants raise weathering 2-10x; Drever 1994: < 2x).
- B. A reference that follows slow weatherability changes (relief, plants) but not temperature (PW-576 dropped a
  relearning baseline because it forgot real erosion changes: needs the same care).
- C. Leave the carbon cycle and run the thermostat on by default, with a wider bound; accepts low end CO2 and
  treeless tropics (fails PW-806's hard check), so not recommended.
Lean A, then re-measure full Gough alone before the thermostat (PW-810).
- [ ] option chosen; end pCO2 of 1 Gyr L6 runs within ~180-600 ppm on most draws
- [ ] strict bar re-measured (L6 >= 13/18, L7 >= 7/8 at 1 Gyr; 2 Gyr late window ~70%)

v1-finish-11 (2026-10-25): option A built (coordinator ruling) with GEOCARB's weathering laws and a runoff factor;
the plant weathering factor is now 3x at NPP 500 (Moulton/Berner 2-5x, Drever < 2x, GEOCARB 4x). End pCO2 is no
longer systematically starved (medians 750-2400 ppm after 300 Myr), but full Gough alone still fails the bar (0/6)
and end pCO2 still spreads 90-990 with the drift; the remaining question is in draft-balance-climate-vs-bar.md.
- [x] option chosen (A)
