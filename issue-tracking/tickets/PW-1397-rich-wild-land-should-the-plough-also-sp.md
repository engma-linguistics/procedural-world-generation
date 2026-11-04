---
id: PW-1397
title: "Rich wild land: should the plough also speed its farming up (needs a per-hour labour source)?"
type: task
status: needs-decision
parent: null
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: lane 141
blocked_by: []
relates: [PW-1385, PW-1373]
refs: ["planet/lineages/ladder.py::rich_keep", "planet/lineages/ladder.py::Ladder.line", docs/review/peoples/density-ladder/rich-foragers.md, docs/review/peoples/density-ladder/rich_foragers.py, "tools/peoples_robust.py::forage_land"]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: rich fishing coasts now resist farming (PW-1385 A, lane 141): a people farms only part of such land and takes up more
of it over the thousands of years it has known crops. Only time does this; better farming tools do not. Real rich foragers mostly held
out next to hand-tool farmers (Calusa beside maize farmers, Jomon beside early rice farmers), and a plough or iron tools make each hour
of farming pay more, which should pull rich land into farming faster. Lane 141 left the plough out because no per-hour labour number
for plough against hoe was found on a page it could read (only search summaries: a Tanzanian ox-plough study with tillage 7.1 to 1.6
man-days an acre, ajol.info tvj 186529, which did not load).

Options:
- A: leave it to time alone (as built). Simple; at ~1500 AD old farming peoples still leave about half of the richest waters wild.
- B: once a source is read, divide the richness excess by the plough stage's per-hour gain too (a hand-tool farmer 1, plough stages
  above), so plough peoples farm rich coasts sooner and hand-tool gardeners keep more foragers beside them.
- C: tie it to the tech tree's own era once the tree runs inside the history.

Lean: A now; B only if Daniel finds plough peoples leaving too much coast wild in the viewer.
- [ ] a per-hour (or per-worker) labour source for plough vs hoe farming, read in full, if B is chosen

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: rich-wild-land and forager-trade call; not a must-have
- 2026-11-03: Created from inbox draft draft-rich-hold-plough-gain.md (found by lane 141).
