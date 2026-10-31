---
id: PW-1064
title: "Food budget: prey to dragon biomass is 96-127:1, inside the band Farlow gives for whole modern mammal guilds; on Farlow's own reasoning a guild eating below a mammal's rate should sit lower, so check against a living guild"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: dragon-density-r2
blocked_by: []
relates: [PW-977, PW-990, PW-1019]
refs: [planet/lineages/history/megafauna.py, planet/lineages/dragon_ages.py, docs/review/megafauna/dragon-density/claims.md]
created: 2026-10-30
updated: 2026-10-31
---

## Description
**In plain words.** For every tonne of dragon, the model's empty land carries about 100 to 130 tonnes of grazers. That is what whole
packs of modern mammal hunters reach, all species together. Round 1 of the review read that as a good fit for a cheap-to-feed,
reptile-like dragon; that reading was backwards. On the source paper's own logic an animal that eats less than a mammal should be denser
for the same prey, so the ratio should be lower, not the same. The model's whole guild (dragons and smaller hunters) does come out lower,
about 35-46:1. Whether those numbers are right wants a check against a real, living predator guild.

Evidence:
- Farlow 1993: modern large-mammal communities "usually somewhere between 200:1 and 100:1 ... but can get as low as 45:1" (p. 176);
  his best case needs at least 50:1 for an endotherm as large as its prey (pp. 172-174) and at least 10:1 for an ectotherm (p. 187),
  which he treats as "a limiting, extreme case" (p. 187). Real communities sit 2-4x above his best case (p. 176).
- His fossil ratios for apex theropods alone run from about 10:1 (articulated Judith River specimens, p. 189) to about 100:1 (Brinkman's
  screen-washed samples, mean 115:1, cumulative 97:1, p. 189); "we cannot confidently conclude much ... from such ratios" (p. 190).
- Model (round-2 numbers.json): 127:1 at the all-ages mean mass 1.26 t, 96:1 at the 1.65 t ecological mass; whole guild 46:1 / 35:1 if the
  smaller classes' biomass follows Carbone et al. 2011's Table 1 (individuals x mass). The model's 1.65 t dragon eats about 2.1x Farlow's
  ectotherm rate (eq. 8) and 0.46x his endotherm rate (eq. 7): between his two cases.

Options:
- **A.** Keep, with the page saying the dragons alone sit at the top of Farlow's fossil range and the guild below the mammal band.
- **B.** Check the guild split against a living guild (PW-1019's Serengeti item) and adjust guild_ratio only if a sourced figure disagrees.
- **C.** Split the guild by biomass rather than food (a different reading of Carbone 2011's table; no source).

Lean: A now, B as part of PW-1019.

## Updates
- 2026-10-31: Lane 90: after the revisions the chain's per-tonne factor is ~0.51 of round 3 and prey falls x0.16-0.46 (above-ground share); see the report's before/after tables. docs/review/dragon-food-chain/report.md
- 2026-10-30: Created from inbox draft draft-dragon-guild-biomass-ratio-check.md (found by dragon-density-r2).
