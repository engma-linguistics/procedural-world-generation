---
title: "Where nobody lives, most of the dragons' food lies in cells no dragon kind holds (rich empty land ~26% occupied, ~30% suitable): habitat, not pressure"
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
---

## Description
**In plain words.** On empty land, more grazers should mean more dragons. Where a dragon kind lives, it does: the dragons come near
what the food feeds. But on the richest empty land most cells hold no dragon kind at all, because no kind's habitat suits them. So
the richest wild country, above all wild grassland and forest, holds few dragons. Round 1 blamed the peoples' pressure for this;
that was wrong (the pressure there is near zero).

Evidence (review round 2, section 4.3, all 24 runs pooled, now; `numbers.json` `cells.on.0`):
- nobody's country: mean pressure ~0.01; only ~30% of cells occupied; ~59% of the dragons' food there lies in unoccupied cells;
- rich empty land (>= 3 t/km2 prey): ~26% occupied, ~30% suitable (S >= `SUITABLE`) for any kind; in occupied rich cells dragons are
  ~18 per 1,000 km2 against a food-fed ~28 (the remaining gap is not traced);
- game-present table: wild forest ~2% occupied, wild grassland ~31%.
(Numbers from the partial sweep; the page has the final ones.)

Options:
- **A.** Widen the dragon kinds' habitats (or add a kind) so rich open country and forest hold dragons.
- **B.** Keep habitats; say plainly the dragons' food model applies only where kinds live.
- **C.** Let food draw scatter toward rich unheld land (scatter currently draws by habitat K only).

Lean: owner's call (design: which dragons live in forest and grassland). Then trace the residual gap in occupied rich cells.
- [ ] decide A/B/C
- [ ] trace occupied rich cells' density vs food-fed density
