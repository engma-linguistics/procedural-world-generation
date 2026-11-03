---
id: PW-1126
title: "Tech tree: environmental risk (cold, seasonal land) should speed up food-getting gear, as Collard et al. 2005 found"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: culture
effort: s
impact: low
found_by: fun-lane-64
blocked_by: []
relates: []
refs: [planet/lineages/techtree.py, docs/references/techtree/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
Collard, Kemery & Banks 2005 (Canadian Journal of Archaeology 29:1-19; 20 hunter-gatherer groups) found that the risk of resource
failure explains how many and how complex food-getting tools a people has. Risk is measured as effective temperature and plant
productivity. Population size did not explain it. The v1 invention model reads population, specialists, kind and culture, but not risk.

What to try: a `risk` factor on the "food" domain (traps, hooks, harpoons, sledges) from the people's country. That could be cold and
seasonality from the world's climate, read like goods_held from the present range, or from the range at each step once PW-946 lands.
Keep it modest (at most 1.5x) and on the stone-age food techs only.
- [ ] a risk measure per people (cold and seasonal share of its cells)
- [ ] x on food-domain stone-age techs; a test that a cold people gets traps and hooks earlier than a warm one of the same size

## Updates
- 2026-10-30: Created from inbox draft draft-techtree-risk-food-toolkits.md (found by fun-lane-64).
