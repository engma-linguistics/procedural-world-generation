---
id: PW-1065
title: "Where nobody lives, dragon kinds hold a third of the land and 31% of the dragons' food goes uneaten (wild forest 6%, grassland 25% occupied): habitat, not pressure"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: dragon-density-r2
blocked_by: []
relates: [PW-977, PW-990, PW-924]
refs: [docs/review/megafauna/dragon-density/index.html, docs/review/megafauna/dragon-density/numbers.json, planet/lineages/history/megafauna.py, planet/lineages/history/habitat.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** On empty land, more grazers should mean more dragons. Where a dragon kind lives, it does: the dragons come near
what the food feeds. But dragon kinds live on only a third of the empty land, because no kind's habitat suits the rest, and about
a third of the dragons' food there goes uneaten. Wild forest, tundra and grassland are what the kinds mostly miss; wild wetland is
almost all held. Round 1 blamed the peoples' pressure for this; that was wrong (the pressure there is near zero). Most empty land is
also poor and cold, which matters more for the total than the habitat gap.

Evidence (review round 2, section 5.3, all 24 runs pooled, now; `numbers.json` `cells.on.0`):
- nobody's country: mean pressure 0.012; 33% of cells occupied; 31% of the dragons' food there lies in unoccupied cells; if every
  empty cell held dragons at its food-fed density, nobody's country would hold 1.8x today's;
- by prey band: poor (< 1 t/km2, 41 of 45 M km2 per run, median latitude 58 deg) 28% occupied; middling 84%; rich (>= 3 t/km2) 76%
  occupied, 77% suitable (S >= `SUITABLE`); in occupied rich cells dragons are 26 per 1,000 km2 against a food-fed 34 (gap not traced);
- by biome, wild cells occupied: forest 5.8%, tundra 11%, grassland 25%, mountain 52%, desert 66%, wetland 99.8%.

Options:
- **A.** Widen the dragon kinds' habitats (or add a kind) so wild grassland, forest and tundra hold dragons.
- **B.** Keep habitats; say plainly the dragons' food model applies only where kinds live.
- **C.** Let food draw scatter toward unheld land with food (scatter currently draws by habitat K only).

Lean: owner's call (design: which dragons live in forest and grassland). Then trace the residual gap in occupied rich cells.
- [ ] decide A/B/C
- [ ] trace occupied rich cells' density vs food-fed density

## Updates
- 2026-10-30: Created from inbox draft draft-dragon-habitat-coverage-rich-land.md (found by dragon-density-r2).
