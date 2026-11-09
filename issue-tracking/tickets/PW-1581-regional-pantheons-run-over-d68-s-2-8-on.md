---
id: PW-1581
title: Regional pantheons run over D68's 2-8 on the Seven Meals tree world 07c755 (15 living)
type: task
status: todo
parent: PW-1308
milestone: null
subsystem: culture
effort: s
impact: low
found_by: lane236
blocked_by: []
relates: [PW-1523]
refs: ["planet/lineages/pantheons.py::HUB_SUBJ", "planet/lineages/pantheons.py::HUB_URBAN", "planet/lineages/pantheons.py::Regional.step", docs/review/culture/faiths/domains1.md, "run 07c755", "run 0141d1", "run a24559", "run a2b637"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** Daniel ruled that regional pantheons should be rare: about 2-8 per world (D68 3A). With the hub thresholds set on
the D&D runs (HUB_SUBJ = 2.0, HUB_URBAN = 0.1), 0141d1 has 5, a24559 has 3 and a2b637 has 1. 07c755, the Seven Meals tree on the
earthlike world, has 15 living pantheons with 52 seats over 10.5% of the land. Most are empire hubs. The Seven Meals tree's states
seem to rule more of other peoples' land.

If this is never done, the Pantheons tab on Seven Meals-tree worlds shows about twice the number Daniel asked for, so the "rare" feel
is lost there. The land share is still well under a third.

Fix: find out why 07c755 has so many qualifying empire hubs (rule_table rows: the foreign land per ruler), then try a relative test, for
example the top N realms by foreign land, or HUB_KYR on the empire side. Check on 3+ worlds with re-rolled draws before changing it.
Seven Meals is frozen: measure only, don't tune for it alone.

## Updates
- 2026-11-09: Created from inbox draft draft-pantheons-over-target-on-07c755.md (found by lane236).
