---
id: PW-1124
title: "Tech tree: copper is found independently ~10 times per world (Earth: a few); check independent origins against the catalogue"
type: task
status: needs-decision
parent: PW-675
milestone: null
subsystem: culture
effort: s
impact: low
found_by: fun-lane-64
blocked_by: []
relates: []
refs: [planet/lineages/techtree.py, docs/references/tech-catalogue/, docs/references/techtree/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words: once peoples have kilns and copper ore, many of them hit on copper smelting on their own before a neighbour can show
them. On Earth it was found in a few places and spread from there.

v1 sets each Holocene tech's rate from Earth's lag after its prerequisites. The rule: a 10 M people at 10/km2 waits, at the median, as
long as Earth did (the anchor check meets it: copper 1.05 kyr vs Earth 1.0; writing 4.05 vs 4.1). Earth's copper came only ~1 kyr
after kilns, so its rate is high (1.1/kyr at full strength). Over 4 D&D runs x 2 draws, copper is found by the peoples themselves ~10
times per world, writing ~5 times (Earth 3-4), cities ~8.

Options:
- A: leave it. Fantasy worlds with many peoples near the same level may have many finds.
- B: a k-first correction. Earth's date is the first of k candidates, so one people waits k times longer. Tried at k = 4: writing's
  world first fell to 0.9 kyr (too late), because the factor compounds down the chain. Rejected.
- C: per-tech independence targets from the catalogue's `origins` lists (how many independent origins each real tech had), with the
  check reporting finds per world against them. Adjust needs (copper's real precondition is a hot-enough kiln and a smelting
  culture, not just kilns), not rates.
Lean: C at catalogue ingestion.

## Updates
- 2026-10-30: Created from inbox draft draft-techtree-independent-finds.md (found by fun-lane-64).
