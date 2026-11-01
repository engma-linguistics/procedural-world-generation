---
title: "The wild herds are 2-3x thinner than Africa's measured herds at the same rain: the model's above-ground growth is about half Rosenzweig's"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: lane103
blocked_by: []
relates: [PW-1073, PW-1221, PW-1246]
refs: [planet/lineages/prey.py, planet/gameattrs.py, docs/review/dragon-numbers/round2.md, docs/references/megafauna/coe1976_african_herbivore_biomass_rainfall_oecologia.pdf]
---

## Description
**In plain words.** Dragons eat the wild herds, so their numbers follow the herds. I checked the model's herds against real African
wildlife counts at the same rainfall (Coe, Cumming & Phillipson 1976, on file). The model's savanna holds 2-3 times fewer large
grazers than real African parks do. Fixing that would give 2-3 times more dragons, giants and herders' stock in warm grassland, with no
fudge. The cause is not in the dragon code. The model's plants put about half as much growth above ground as the formula Coe used.
Something has to give, and it touches the vegetation model and an earlier ruling (PW-1073), so it needs your call.

Evidence (lane 103, `prey.wild` on worlds 067778 and 6909cb, warm land with mean temperature over 18 C, medians per rain band):

| rain, mm | model herds, t/km2 | Coe 1976 linear fit under 700 mm (p. 348: 8.684 x rain - 1205.9 kg/km2) | Coe Table 1 (pp. 344-345), measured |
|---|---|---|---|
| 250-400 | 0.37 / 0.91 | 1.6 | Samburu-Isiolo 2.0 (375 mm) |
| 400-550 | 0.97 / 1.69 | 2.9 | Henderson's ranch 2.9 (406), Mkomasi 1.7 (425) |
| 550-700 | 1.54 / 2.10 | 4.2 | Tsavo 4.0-4.4 (553), Sengwa 4.3 (597), Kruger S 3.8 (650) |
| 700-900 | 2.27 / 2.27 | (fit stops at 700) | Serengeti 8.4 (803), Lochinvar 7.6 (813), Nairobi 4.8 (844), Nakuru 6.7 (878) |

Where it comes from. The model feeds McNaughton et al. 1989's fit the above-ground part of the grazing NPP (PW-1073: the NPP x Gherardi &
Sala 2020's above-ground share, ~0.44 at 625 mm). That gives ~180 g C/m2/yr (~400 g dry) above ground at 550-700 mm. Coe et al. used
Rosenzweig 1968's prediction of above-ground production from evapotranspiration (p. 345); their own fit (Fig. 3, p. 349: log10 B =
1.094 log10 NAAP + 0.389) needs ~940 g dry/m2/yr to give their 4.4 t/km2 at 650 mm. McNaughton's fit at Rosenzweig's NAAP also gives
~5.9 t/km2. So both herd fits agree with the measured herds once the above-ground production is Rosenzweig's; the model's is ~2.4x
lower. Either the vegetation's NPP is low for savanna, or the below-ground share is too high for it, or both. Rosenzweig 1968 and the
vegetation's own calibration are not on file; nothing here says which.

Options:
- **A. Accept.** Earth is not a parity target; the herds stay as they are, and `meta.dragon_abundance` (lane 103) is the lever.
- **B. Check the vegetation NPP of savanna** against a sourced savanna NPP table (climate/vegetation lane), and fix whichever step is
  off. Raises herds, dragons, giants and herders together, everywhere the cause applies.
- **C. Fit the herds to measured biomass directly** (Coe's rainfall fit in warm savanna), bypassing NPP. Simple but Africa-only and
  rain-only (no cold, no forest): not general.

Lean: B, as a cheap diagnosis first (one savanna NPP source read against the model's NPP by rain band), before any change.
