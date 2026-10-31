---
id: PW-1204
title: "A K-ratio 'fit decides' contest does nothing on today's niches: humans' habitat is 0.9-1.0 in every specialist's best country"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: lane84
blocked_by: []
relates: [PW-1180, PW-1149]
refs: [planet/lineages/history/habitat.py, planet/lineages/history/competition.py, planet/lineages/samples/dnd.toml, docs/review/peoples-why/report.md]
created: 2026-10-31
updated: 2026-10-31
---

## In plain words
Decision D20's first lever is "the people that suits the land better presses harder there". Lane 84 tried a simple form of it and it
changed nothing. On today's preset the humans already suit almost every people's best country as well as that people does. The humans'
comfort range is so wide (6-26 C, 350-2200 mm, temperate, subtropical and lowland) that their habitat is high on more than half the
world's land. A fit rule needs a cost of being a generalist, or it has nothing to act on.

## Description
Present climate of world 4360a3, `habitat.capacity` (no learning, no goods):
- Human K >= 0.5 on 54% of land, >= 0.9 on 39%.
- In each people's own best country (its K >= 0.7), the humans' median K is: elves 0.97, orcs 1.00, hobgoblins 1.00, halflings 1.00,
  dragonborn 1.00, gnomes 1.00, leonin 1.00, kenku 0.92, bugbears 0.94, tabaxi 0.87, kobolds 0.82; only dwarves (0.40) and goliaths
  (0.40) have country humans fit badly.
- Ablation (patched `_load` in a scratch probe, not committed): each rival's load on line k weighted by (K_j / K_k), clipped 0.25-4.
  five-people cut (humans, elves, dwarves, halflings, orcs) humans 83.2% -> 83.0% (5 seeds); dnd 66.9% -> 66.4% (seeds 7, 10, 13).

Options, for lane 83 or after it:
- A. A breadth cost: a line's peak K falls with the width of its comfort range and the number of countries it prefers (a
  jack-of-all-trades trade-off), so a specialist outpresses a generalist at home.
- B. Fit by preference, not by K: in a cell that is in a's `prefers` and not in b's, a presses b harder (and the reverse).
- C. Narrow the humans' preset niche only (data, not a rule).

Lean: A or B in lane 83's contest work, judged on the lane 77 suite; C alone is a point fix.

## Updates
- 2026-10-31: Created from inbox draft draft-fit-contest-inert-humans-fit-everywhere.md (found by lane84).
