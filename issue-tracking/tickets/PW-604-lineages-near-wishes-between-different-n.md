---
id: PW-604
title: "Lineages: 'near' wishes between different-niche peoples fail more often now that ranges are distinct"
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lineages-lane-2
blocked_by: []
relates: [PW-601]
refs: [planet/lineages/history.py, planet/lineages/crossing.py, docs/proposals/lineages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane 2 made closed country exclusive: alpha_eff rises toward 1.4 where the contact value is low, and peoples are displaced. Peoples now hold distinct ranges, which is what the owner asked for. The cost: "goblin near orc" (rainforest goblins, steppe orcs) scored 0.0-0.03 on 119973, 81aced and c00ebf with one try each. Under lane 1 the same wish scored 0.0-1.0, and it was met only because goblins spread thinly everywhere. Wishes between peoples of the same niche (halfling near human, hobgoblin near goblin) still score 0.4-1.0.

Options:
- A (current, the PW-601 lean): best of N tries plus mild nudges. A wish between different biomes is met only where those biomes touch, so geography decides.
- B: a "near" wish also nudges the younger line's split origin toward the edge of the older line's range. It already multiplies the origin score by 1 + w x p_b smoothed over one ring; widen that to ~5 rings.
- C: PW-601 option B (place the wished lines' origins to satisfy the wish first).

Lean: B. It is small and still only a nudge.

## Updates
- 2026-10-23: Created from inbox draft draft-lineages-near-wishes-after-exclusion.md (found by lineages-lane-2).
- 2026-10-23: Lineages lane 3 built lean B, widened. A near wish now:
  - pulls the habitat toward the other's border (x(1 + 0.5 w) just outside its range, e-folding over 300 km; not into it, which under exclusion let the wisher displace the other);
  - pulls whichever origin comes second toward the other (x(1 + 2 w), e-folding over 1000 km);
  - halves the competition between the two.

  The near score now uses 330 km at any level. Before, it was 3 cells, which is 165 km at L7.
  - Results, best of 2, before -> after: goblin near orc 0.00 -> 0.11 / 0.00 / 0.19 / 0.70 on 1144ce / 31926a / 91448a / 3e0b0a, and 0.00 -> 1.00 on 119973. Hobgoblin near goblin 0.33 / 0.14 / 0.09 / 0.36 / 0.05 -> 1.00 / 0.26 / 1.00 / 0.54 / 0.96. Overall 0.64 / 0.56 / 0.59 / 0.58 / 0.49 -> 0.73 / 0.56 / 0.73 / 0.62 / 0.74. Table in docs/review/lineages/showcase-3.md.
  - Goblin-orc stays low where the preset's rainforest and cold-steppe niches have no shared country. See inbox draft-lineages-goblin-orc-niches.
