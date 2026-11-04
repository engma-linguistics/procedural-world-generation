---
id: PW-1261
title: "The wild herds are 2-3x thinner than Africa's measured herds at the same rain: the model's above-ground growth is about half Rosenzweig's"
type: task
status: in-progress
parent: null
milestone: later
subsystem: food
effort: m
impact: med
found_by: lane103
blocked_by: [PW-1316]
relates: [PW-1073, PW-1221, PW-1246]
refs: [planet/lineages/prey.py, planet/gameattrs.py, docs/review/dragon-numbers/round2.md, docs/references/megafauna/coe1976_african_herbivore_biomass_rainfall_oecologia.pdf]
created: 2026-11-01
updated: 2026-11-03
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

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: physics side track, ranked 3; gates no tag (plant growth; status unchanged)
- 2026-11-03: Lane 144 (fork judge, merged 558ce440): PW-1261's 2 frozen-over draws are the same two where a forked do-nothing change also froze over (PW-1404). Still parked on D45.
- 2026-11-03: Lane 140d (5f5d6ddf, round1.md s8): main's cold-tail fragility is the carbon-cycle yardstick learnt from ~5 samples of the spin-up (carries 1.5 of 1.7 C within-seed late-dT sd); the herb change's own push ~-0.1 to -0.15 C. Parked pending D45 (judge from a shared spin-up?); harness being built in lane 144.
- 2026-11-03: Lane 140c (95761e73, round1.md s7): null-nudge screen moves main's 6 coldest by 3-27 pt (one crosses 40% before the window); herb change stays above the null on 6/6 (sign test p~0.03): small real cold push. Weathering reference on spin-up climate: negligible (~+0.01 C), lean close. Held on branch; lane 140d diagnoses the cold-tail margin (spin-up dT vs late dT r=-0.39) and the in-window push.
- 2026-11-03: Lane 140b screen (8bc401dd, round1.md s6): neither half alone fails (herb-only 24.4/39.4, fuel-only 23.4/39.8 on the two draws); failures are chaos at a thin margin plus a small real cold shift (+1.35 pt mean window land ice over 36 draws, herb part at least as much as fuel); not via trees; FUEL_MIN 200 is needed (scrub stops burning without it). Next (lane 140c): null-nudge screen of main's 6 coldest, then a written diagnosis of the weathering reference grown on the spin-up climate.
- 2026-11-02: Lane 140 judge (2 rolls, 36 paired draws): soft 30 -> 26 (p 0.39), dT/CO2 unchanged, trees -1.8 pt, hard bar 2 frozen over (42.9%, 41.7% land ice; main 0). Strike 1, not merged (branch commits 88ebe5a4, ada450a2, 351a995f). Next: targeted screen on the two draws, each part alone (herb resp vs FUEL_MIN 200), before any re-judge.
- 2026-11-02: Status todo -> in-progress. 11-02: lane 140 started on D42 A (C1 herb root respiration with the NPP_WEATHER re-anchor, PW-1332, and the fuel floor PW-1328 if needed). PW-1316 settled without change (B failed).
- 2026-11-02: Status needs-decision -> todo. Owner 2026-11-02: D42 A (herbs' root respiration, see what it gets us). After D39 (PW-1316) lands, since lowering grass NPP warms runs through NPP_WEATHER and the CO2 references.
- 2026-11-02: Status in-progress -> needs-decision. 11-02 lane 123: premise wrong: on Earth's observed climate herds match Coe; grass grows 1.4-1.8x too much (herbs keep ~70% of GPP, roots pay no upkeep) and wet tropical forest ~0.55x. Worlds' herds thin from cloudy/cool semi-arid tropics (PW-1330) and low CO2. Candidate C1 needs NPP_WEATHER re-anchor (PW-1332) and a sourced fire fuel floor (PW-1328) in one round. docs/review/vegetation/npp-check/diagnosis.md
- 2026-11-02: Status needs-decision -> in-progress. 11-02: lane 123, D34 B broadened (all biomes, plant response on observed climate), diagnosis first.
- 2026-11-01: Created from inbox draft draft-wild-herds-below-coe-1976.md (found by lane103).
