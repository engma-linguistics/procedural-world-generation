---
id: PW-1067
title: "Dragon food conversion: 85% assimilation is unsourced (Carbone et al. 2007 use 66%) and the whole 0.5 t carcass counts as eaten (they give 65-91%)"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: med
found_by: dragon-density-r2
blocked_by: []
relates: [PW-1019, PW-991]
refs: [planet/lineages/dragon_ages.py, planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/sensitivity.py]
created: 2026-10-30
updated: 2026-10-31
---

## Description
**In plain words.** Turning a dragon's energy need into prey killed takes two steps the model makes generous: it assumes a dragon gets
85% of the energy in what it eats (no source), and that it eats every bit of every carcass. The one paper on file that gives numbers for
big meat-eaters uses 66% and says only 65-91% of a large carcass is eaten. Using those, a dragon needs up to about twice as much prey,
so the land holds up to about half as many dragons.

Evidence:
- dragon_ages.ASSIMILATED = 0.85, no source. Carbone, Teacher & Rowcliffe 2007 (PLoS Biol 5:e22): "DEI = DEE/0.66 ... derived from an
  estimate of proportional assimilation efficiency" (p. 364); "only a proportion of large-vertebrate prey are consumed (65%-91%
  depending on their mass)" (p. 367).
- Nagy et al. 1999's own conversion (16.8 kJ/g dry matter for mammalian carnivores, food 30% dry matter, pp. 263-264) gives 5.04 kJ per
  g of fresh meat against the model's 5.95 (7 kJ/g x 0.85).
- The peoples' head is 625,000 edible kcal (megafauna.HEAD_KCAL), the dragons' 836,000 x 0.85 = 711,000: one cow, two values.

Direction and size on dragons: fewer. 66% alone x0.78; Nagy's route x0.85; carcass use 65-91% x0.65 to x0.91; together down to about x0.5.
- [ ] pick a sourced assimilation (Carbone 2007's 0.66, or Nagy's route) and a carcass-use share by prey mass
- [ ] one edible-energy figure per head for peoples and dragons

## Updates
- 2026-10-31: Status todo -> done. Lane 90: ASSIMILATED 0.66 (Carbone 2007 p. 364), CARCASS_USE 0.78 (midpoint of 65-91%, p. 367; judgement); HEAD_KCAL = dragon_ages.edible_kcal() for peoples, giants and dragons. docs/review/dragon-food-chain/report.md
- 2026-10-30: Created from inbox draft draft-dragon-kill-conversion-assimilation-carcass.md (found by dragon-density-r2).
