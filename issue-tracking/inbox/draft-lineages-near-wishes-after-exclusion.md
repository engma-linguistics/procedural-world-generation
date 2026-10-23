---
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
---

## Description
Lane 2 made closed country exclusive: alpha_eff rises toward 1.4 where the contact value is low, and peoples are displaced. Peoples now hold distinct ranges, which is what the owner asked for. The cost: "goblin near orc" (rainforest goblins, steppe orcs) scored 0.0-0.03 on 119973, 81aced and c00ebf with one try each. Under lane 1 the same wish scored 0.0-1.0, and it was met only because goblins spread thinly everywhere. Wishes between peoples of the same niche (halfling near human, hobgoblin near goblin) still score 0.4-1.0.

Options:
- A (current, the PW-601 lean): best of N tries plus mild nudges. A wish between different biomes is met only where those biomes touch, so geography decides.
- B: a "near" wish also nudges the younger line's split origin toward the edge of the older line's range. It already multiplies the origin score by 1 + w x p_b smoothed over one ring; widen that to ~5 rings.
- C: PW-601 option B (place the wished lines' origins to satisfy the wish first).

Lean: B. It is small and still only a nudge.
