---
id: PW-1178
title: "Metallic dragons live alongside peoples, chromatics stay combative: a temperament per dragon kind in the persecution and food rules"
type: story
status: todo
parent: null
milestone: later
subsystem: peoples
effort: m
impact: med
found_by: fun-lane-63
blocked_by: []
relates: [PW-1068, PW-924, PW-855]
refs: [planet/lineages/history/megafauna.py, planet/lineages/samples/dnd.toml, planet/lineages/spec.py]
created: 2026-10-30
updated: 2026-11-03
---

## Description
**In plain words.** The owner wants (10-30, D16) metallic dragons (gold, silver, bronze, copper, brass) to live more easily
alongside the peoples, and chromatic dragons (red, blue, green, black, white) to stay combative. Today the two are treated almost the
same. The one difference is `rivalry = 0.5` on the metallic stem (PW-924), which only softens the metallics' competition with
other megafauna. The peoples kill every dragon kind alike (`megafauna.kill` / `kept`), and every kind eats the same prey.

A temperament per kind, inherited down the tree like `rivalry`, could act in up to three places. Each is a small, local change:
1. **How hard the peoples press it.** A multiplier on the peoples' kill for that kind, inside `megafauna.kept`. Metallics would get
   less than 1 (they bargain, guard and are tolerated), chromatics 1 or more (they raid and are hunted). The viewer's D14 settings
   (`meta.press_early` / `press_late`) would still multiply on top.
2. **Whether it takes the herders' stock.** A share of `STOCK_TOLERABLE` per kind. Metallics would take less livestock (and so draw
   less of the herders' anger); chromatics would take the full share. This links to the "dragons press back" idea in
   draft-forager-offtake-overstated.md.
3. **Whether it preys on small folk** (the D16 "dragons press back" idea), once that exists: chromatics would, metallics would not.

There is no real-world source to calibrate this against; it is a setting, not a physics claim. Do 1 first: it is one number per
kind, with no new mechanism.
- [ ] `temperament` (or a `press` multiplier) on lineages, inherited like `rivalry`; metallic < 1, chromatic >= 1 in dnd.toml
- [ ] applied in `kept`; a test that a metallic keeps more than a chromatic under the same kill
- [ ] shown in the viewer's lineage panel (the owner uses the viewer)

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-10-30: Created from inbox draft draft-dragon-temperament-metallic-chromatic.md (found by fun-lane-63).
